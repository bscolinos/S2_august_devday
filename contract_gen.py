import json
import random
from datetime import datetime, timedelta
import ollama
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize SentenceTransformer for text vectorization
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to generate a fake contract using Ollama
def generate_fake_contract():
    prompt = "Generate a short business contract with random clauses and terms. Keep it under 500 words. Make up numbers and dates (ranging from 01/01/2000 to 05/01/2024)."
    response = ollama.generate(model='llama2', prompt=prompt)
    return response['response']

# Function to generate random metadata
def generate_metadata():
    countries = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Japan', 'India', 'Australia']
    divisions = ['Sales', 'Marketing', 'HR', 'Finance', 'IT', 'Finance', 'Operations', 'Legal']
    contract_types = ['Service', 'Employment', 'Non-disclosure', 'Lease', 'Purchase']
    
    return {
        'country': random.choice(countries),
        'division': random.choice(divisions),
        'contract_type': random.choice(contract_types),
        'effective_date': (datetime.now() + timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
        'contract_value': round(random.uniform(1000, 1000000), 2)
    }

# Generate fake contracts with metadata and vectors
def generate_contracts(num_contracts):
    contracts = []
    
    for _ in range(num_contracts):
        contract_text = generate_fake_contract()
        metadata = generate_metadata()
        vector = model.encode(contract_text).tolist()
        
        contract_data = {
            'contract_text': contract_text,
            'vector': vector,
            **metadata
        }
        
        contracts.append(contract_data)
    
    return contracts


db_config = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Prepare the SQL insert statement
insert_query = """
INSERT INTO contracts 
(contract_text, vector, country, division, contract_type, effective_date, contract_value)
VALUES (%s, JSON_ARRAY_PACK(%s), %s, %s, %s, %s, %s)
"""

# Generate fake contract
num_contracts = 1
while True:
    contracts = generate_contracts(num_contracts)

    # Convert to JSON
    json_data = json.dumps(contracts, indent=2)

    df = pd.read_json(json_data)

    try:
        # Establish a database connection
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Iterate over DataFrame rows and insert data
            for _, row in df.iterrows():
                # Convert vector list to a JSON array string
                vector_json = json.dumps(row['vector'])
                
                # Prepare data tuple
                data = (
                    row['contract_text'],
                    vector_json,
                    row['country'],
                    row['division'],
                    row['contract_type'],
                    row['effective_date'],
                    row['contract_value']
                )
                
                # Execute the insert query
                cursor.execute(insert_query, data)
            
            # Commit the changes
            connection.commit()
            # print(f"Successfully inserted {len(df)} rows.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            # print("MySQL connection is closed")