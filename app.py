# Importing libraries
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure the Gemini API key from .env
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# Prompt for LLM
prompt = [
    """
    You are an expert in converting English language to SQL Query!
    The SQL database is named STUDENT and has the following columns: 
    PRN (integer), NAME (string), CLASS (string), SECTION (string), and MARKS (integer).

    Example 1: "How many entries of records are present?"
    Output: SELECT COUNT(*) FROM STUDENT;

    Example 2: "Tell me all the students studying in the Data Science class?"
    Output: SELECT * FROM STUDENT WHERE CLASS='Data Science';

    Please return only the SQL query without using triple quotes or the word 'SQL'.
    """
]

# Function to get Gemini response (SQL query)
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    response = model.generate_content([prompt[0], question])
    return response.text.strip()

# Function to execute SQL query and return result
def read_sql_query(sql, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Streamlit UI
st.set_page_config(page_title="I can Retrieve any SQL Query")
st.title("Gemini App to Retrieve SQL Data")
st.markdown("Ask in English, and get results from the **STUDENT** database!")

question = st.text_input("Enter your query in English:", key="input")
submit = st.button("Run Query")

if submit and question:
    with st.spinner("Generating SQL..."):
        try:
            response = get_gemini_response(question, prompt)
            st.code(response, language='sql')
            data = read_sql_query(response, "student.db")

            st.subheader("Query Result:")
            if data:
                for row in data:
                    st.write(row)
            else:
                st.info("No data found.")
        except Exception as e:
            st.error(f"Error: {e}")
