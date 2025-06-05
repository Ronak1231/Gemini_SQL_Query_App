import streamlit as st
import sqlite3
import hashlib
from dotenv import load_dotenv
import os
import google.generativeai as genai

# -------------------- Load Env --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# -------------------- DB Setup --------------------
def init_user_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_student_db():
    conn = sqlite3.connect("student.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS STUDENT (
            PRN INTEGER PRIMARY KEY,
            NAME TEXT,
            CLASS TEXT,
            SECTION TEXT,
            MARKS INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_user_db()
init_student_db()

# -------------------- Authentication --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, name, password_hash) VALUES (?, ?, ?)",
              (username, name, hash_password(password)))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", 
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

# -------------------- Gemini SQL Prompt --------------------
base_prompt = """
You are an expert in converting English language to SQL Query!
The SQL database is named STUDENT and has the following columns:
PRN (integer), NAME (string), CLASS (string), SECTION (string), and MARKS (integer).

Example 1: "How many entries of records are present?"
Output: SELECT COUNT(*) FROM STUDENT;

Example 2: "Tell me all the students studying in the Data Science class?"
Output: SELECT * FROM STUDENT WHERE CLASS='Data Science';

Return only the SQL query without any explanation or extra text.
"""

def get_gemini_response(question):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content([base_prompt, question])
    return response.text.strip()

def run_sql_query(sql):
    conn = sqlite3.connect("student.db")
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Student DB App", layout="centered")
st.title("📘 Student Record Manager with Gemini SQL")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------- Registration Page --------------------
if choice == "Register":
    st.subheader("Create New Account")
    name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if name and username and password:
            try:
                register_user(name, username, password)
                st.success("Registration successful. Go to Login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists.")
        else:
            st.error("All fields are required.")

# -------------------- Login Page --------------------
elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {user[1]}!")
        else:
            st.error("Invalid credentials.")

# -------------------- Logged In View --------------------
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["➕ Add Student", "🧠 Query Student Data"])

    with tab1:
        st.subheader("Insert Student Record")
        prn = st.text_input("PRN")
        name = st.text_input("Name")
        class_name = st.text_input("Class")
        section = st.text_input("Section")
        marks = st.text_input("Marks")

        if st.button("Add Student"):
            try:
                conn = sqlite3.connect("student.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO STUDENT (PRN, NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?, ?)",
                               (int(prn), name, class_name, section, int(marks)))
                conn.commit()
                conn.close()
                st.success("Student record added.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.subheader("Ask a question in English")
        question = st.text_input("e.g., Show students in class 10A")
        if st.button("Run Query"):
            try:
                sql = get_gemini_response(question)
                st.code(sql, language='sql')
                results = run_sql_query(sql)
                if results:
                    for r in results:
                        st.write(r)
                else:
                    st.info("No results found.")
            except Exception as e:
                st.error(f"Query Error: {e}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully.")
