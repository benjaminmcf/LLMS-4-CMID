# LLMS-4-CMID
Repository for applications and tutorials on using large language models for clinical microbiology and infectious disease

# Natural Language SQL Query Interface

This Streamlit application allows you to query a SQLite database using natural language. It uses OpenAI's GPT model to convert natural language questions into SQL queries.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Running the Application

Run the Streamlit app with:
```bash
streamlit run app.py
```

The application will create a sample SQLite database with turnaround time data and provide a web interface where you can:
- Enter natural language questions about the data
- See the generated SQL queries
- View the query results in a table format
