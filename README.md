# SingleStore x Google August Dev Day
Materials presented at SingleStorexGoogle dev day

Here are the materials presented at the event. The repo contains a script for generating syntetic contract data, a script for running a streamlit app to interact with that table, and a .sql file to run in SingleStore that contains the table DDL. Modify all 3 of these as needed to experiment with different data or LLM combinations.

The app allows users to query and analyze contracts using natural language processing powered by Google's Vertex AI / Gemini model. It uses SingleStore for efficient data storage and retrieval, Streamlit for the user interface, and LangSmith for monitoring.

## Features

- Filter contracts by country, division, and contract type (you can modify this as 
- Query filtered contracts using natural language
- Generate AI-powered responses based on contract content
- Integration with LangSmith for tracing and monitoring

## Prerequisites

- Python 3.7+
- SingleStore account (for database and vector storage) - https://www.singlestore.com/cloud-trial/?utm_campaign=Boston - sign up at that link to be entered in our raffle!
- GCP account (for Vertex AI) - free trial available
- LangSmith account (for tracing) - free trial available

## Setup

1. Clone this repository
2. Install required packages: pip install -r requirements.txt
3. Set up a SingleStore free trial:
- Visit [SingleStore](https://www.singlestore.com/cloud-trial/?utm_campaign=Boston) and sign up for a free trial
- Create a new database and note down the connection details

4. Set up Google Cloud Platform and Vertex AI:
- Create a new project on [Google Cloud Console](https://console.cloud.google.com/)
- Enable the Vertex AI API for your project
- Set up authentication (e.g., using a service account key)

5. Set up LangSmith:
- Sign up for an account at [LangSmith](https://www.langsmith.com/)
- Obtain your API key

6. Create a `.env` file in the project root with the following variables:
S2_HOST=your_singlestore_host
DB_NAME=your_database_name
S2_USER=your_singlestore_username
S2_PASSWORD=your_singlestore_password
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=your_langsmith_project_name
