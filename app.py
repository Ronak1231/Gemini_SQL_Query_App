# Importing libraries
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import sqlite3
import google.generativeai as generativeai

# Configuring our API key
generativeai.configure(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# Prompt for LLM
prompt = [
    """
    You are an expert in converting english language to SQL Query !
    The SQL database has the name STUDENT and has the following columns: PRN number,
    Name, CLASS, SECTION, and MARKS.

    Example 1: "How many entries of records are present?", the SQL command
    will be something like: SELECT COUNT(*) FROM STUDENT;
    
    Example 2: "Tell me all the students studying in the Data Science class?",
    the SQL command will be something like: SELECT * FROM STUDENT WHERE CLASS='Data Science'
    
    Also, the SQL code should not have ''' in the beginning or end and no SQL word in the output.
    """
]

# Function to get LLM response
def get_gemini_response(question, prompt):
    model = generativeai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to execute the SQL query on the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Streamlit App
st.set_page_config(page_title="I can Retrieve any SQL Query")
st.header("Gemini App to Retrieve SQL Data")
question = st.text_input("Input: ", key="input")
submit = st.button("Ask the Question")

# If submit button is clicked
if submit:
    # Get SQL query from LLM response
    response = get_gemini_response(question, prompt)
    st.write(f"SQL Query Generated: {response}")  # Display the generated SQL query
    try:
        # Read data from the SQL database
        data = read_sql_query(response, "student.db")
        st.subheader("The Response is:")
        for row in data:
            st.write(row)  # Displaying each row of data
    except Exception as e:
        st.error(f"Error executing the query: {e}")

