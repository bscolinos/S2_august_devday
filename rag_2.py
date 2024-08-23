import streamlit as st
import mysql.connector
from mysql.connector import Error
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from langsmith import Client
from langsmith import traceable
import os
from dotenv import load_dotenv

load_dotenv()

# Set up LangSmith - done w environment variables - run exp
client = Client()

# MySQL connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to SingleStore: {e}")
        return None

# Vertex AI initialization TODO replace project with your project name
def init_vertex_ai():
    vertexai.init(project="YOUR_PROJECT_NAME_GOES_HERE", location="us-central1")

# Function to generate content w Gemini
@traceable # Enables tracing via langsmith
def generate_gemini_response(prompt):
    model = GenerativeModel("gemini-1.5-flash-001")
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.5,
        "top_p": 0.95,
    }
    safety_settings = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
    ]

    response = model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
    return response.text

# Initialize Vertex AI
init_vertex_ai()

# Streamlit app
st.title("Contract Query and Analysis")

# Filter options - modify these as needed for your app
countries = ['All', 'USA', 'UK', 'Canada', 'Germany', 'France', 'Japan', 'India', 'Australia']
divisions = ['All', 'Sales', 'Marketing', 'HR', 'Finance', 'IT', 'Operations', 'Legal']
contract_types = ['All', 'Service', 'Employment', 'Non-disclosure', 'Lease', 'Purchase']

selected_country = st.selectbox("Select Country", countries)
selected_division = st.selectbox("Select Division", divisions)
selected_contract_type = st.selectbox("Select Contract Type", contract_types)

# Function to fetch filtered contracts
def fetch_filtered_contracts():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, contract_text, country, division, contract_type
                FROM contracts
                WHERE (%s = 'All' OR country = %s)
                AND (%s = 'All' OR division = %s)
                AND (%s = 'All' OR contract_type = %s)
                LIMIT 5
            """
            cursor.execute(query, (
                selected_country, selected_country,
                selected_division, selected_division,
                selected_contract_type, selected_contract_type
            ))
            return cursor.fetchall()
        except Error as e:
            st.error(f"Error executing query: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return []

# get contracts based on filters
filtered_contracts = fetch_filtered_contracts()

# Question input
question = st.text_input("Ask a question about the filtered contracts:")

if question and filtered_contracts:
    # Prepare context from filtered contracts
    context = "\n\n".join([f"Contract {c['id']}:\nCountry: {c['country']}\nDivision: {c['division']}\nType: {c['contract_type']}\nText: {c['contract_text']}..." for c in filtered_contracts])
    
    prompt = f"""Based on the following contract information:

{context}

Please answer the following question:
{question}

Provide a concise and accurate answer based solely on the information given in the contracts."""

    response = generate_gemini_response(prompt)

    st.subheader("Answer:")
    st.write(response)

elif question:
    st.warning("No contracts found with the selected filters. Please adjust your selection.")