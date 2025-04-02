import sqlite3
import streamlit as st
import pandas as pd



def natural_language_to_sql(prompt,client):
    system_message = """You are a SQL expert. Convert natural language questions into SQL queries.
    The database has a table called 'BC_TAT' with columns: id, collection_time, reception_time, loading_time, gram_stain_time,
      organism_identification_time, antibiotic_sensitivity_time, final_report_time, clinic_name, 
      clinic_location, organism_name. Turnaround time is the time from collection to final report. Note all time columns
      are in the format 'YYYY-MM-DD HH:MM:SS'. The database is sqlite3.Only allow the user to retrieve data from the table.
    Return ONLY the SQL query, nothing else."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    
    return response.choices[0].message.content.strip()

def execute_query(query):
    print(query)
    conn = sqlite3.connect('data.db')
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error executing query: {query}")
        return None
    finally:
        conn.close()