from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
from utils import natural_language_to_sql, execute_query

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit UI
st.title("Natural Language SQL Query Interface")
st.write("Ask questions about the employees database in natural language!")

# Add some example queries
st.sidebar.header("Example Questions")
examples = [
    "What is the turnaround time for id 1. Return in hours",
    "What is the clinic with the highest turnaround time. Show in days",
    "What is the average turnaround time for each clinic. Return in hours"
]
st.sidebar.write("\n".join(f"- {example}" for example in examples))

# User input
user_question = st.text_input("Enter your question:")

if user_question:
    with st.spinner("Generating SQL query..."):
        sql_query = natural_language_to_sql(user_question,client)
        
    # st.subheader("Generated SQL Query:")
    # st.code(sql_query, language="sql")
    
    with st.spinner("Executing query..."):
        results = execute_query(sql_query)
        
    if results is not None:
        st.subheader("Query Results:")
        st.dataframe(results)

# Display API key warning if not set
if not os.getenv("OPENAI_API_KEY"):
    st.warning("Please set your OpenAI API key in a .env file as OPENAI_API_KEY=your_key_here") 