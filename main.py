import streamlit as st
import sqlite3
import hashlib
from dotenv import load_dotenv
import os
import google.generativeai as genai

# -------------------- Load Gemini Key --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# -------------------- DB Init --------------------
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

init_user_db()

# -------------------- Auth --------------------
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

# -------------------- Gemini --------------------
def get_db_schema():
    conn = sqlite3.connect("general.db")
    c = conn.cursor()
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    schema = ""
    for table in tables:
        table_name = table[0]
        schema += f"Table: {table_name}\n"
        cols = c.execute(f"PRAGMA table_info({table_name})").fetchall()
        for col in cols:
            schema += f"- {col[1]} ({col[2]})\n"
        schema += "\n"
    conn.close()
    return schema.strip()

def get_gemini_response(question, schema_info):
    prompt = f"""
You are an expert in converting English to SQL queries.
The following tables and their schemas exist in a SQLite database:

{schema_info}

Convert the following English question into an SQL query:
"{question}"

Only return the SQL query. No explanation.
"""
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def run_sql_query(sql):
    conn = sqlite3.connect("general.db")
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    headers = [description[0] for description in cur.description]
    conn.commit()
    conn.close()
    return headers, rows

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="Dynamic SQL App", layout="centered")
st.title("📊 Create & Query Any SQL Table")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------- Register --------------------
if choice == "Register":
    st.subheader("Create Account")
    name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if name and username and password:
            try:
                register_user(name, username, password)
                st.success("Registered. Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists.")
        else:
            st.error("All fields are required.")

# -------------------- Login --------------------
elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid credentials.")

# -------------------- Logged In Functionality --------------------
if st.session_state.logged_in:
    tab1, tab2, tab3 = st.tabs(["🧱 Create Table", "📥 Insert Data", "🤖 Query with Gemini"])

    # -------------------- Tab 1: No-SQL Table Builder --------------------
    with tab1:
        st.subheader("🧱 Create Table (No SQL Needed)")
        table_name = st.text_input("Enter table name:")

        if "columns" not in st.session_state:
            st.session_state.columns = []

        col1, col2, col3 = st.columns([4, 3, 2])
        with col1:
            new_col_name = st.text_input("Column Name", key="col_name")
        with col2:
            new_col_type = st.selectbox("Data Type", ["TEXT", "INTEGER", "REAL", "BOOLEAN"], key="col_type")
        with col3:
            is_pk = st.checkbox("Primary Key", key="col_pk")

        if st.button("Add Column"):
            if new_col_name:
                st.session_state.columns.append((new_col_name, new_col_type, is_pk))
                st.success(f"Added column: {new_col_name} ({new_col_type})")

        if st.session_state.columns:
            st.markdown("### 🧱 Column Preview")
            for col in st.session_state.columns:
                st.markdown(f"- `{col[0]}` ({col[1]}){' [PK]' if col[2] else ''}")

        if st.button("Create Table"):
            try:
                columns_sql = []
                for name, dtype, pk in st.session_state.columns:
                    col_def = f"{name} {dtype}"
                    if pk:
                        col_def += " PRIMARY KEY"
                    columns_sql.append(col_def)
                full_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_sql)});"
                conn = sqlite3.connect("general.db")
                conn.execute(full_sql)
                conn.commit()
                conn.close()
                st.success("✅ Table created successfully.")
                st.session_state.columns = []
            except Exception as e:
                st.error(f"Error: {e}")

    # -------------------- Tab 2: Insert Data --------------------
    with tab2:
        st.subheader("📥 Insert Data into Table")
        conn = sqlite3.connect("general.db")
        c = conn.cursor()
        tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        conn.close()

        selected_table = st.selectbox("Choose a table", table_names if table_names else ["No table yet"])

        if selected_table and selected_table != "No table yet":
            conn = sqlite3.connect("general.db")
            c = conn.cursor()
            cols = c.execute(f"PRAGMA table_info({selected_table})").fetchall()
            input_data = {}
            for col in cols:
                if col[5] == 1:  # auto-increment PK
                    continue
                input_data[col[1]] = st.text_input(f"{col[1]} ({col[2]})")
            if st.button("Insert Record"):
                try:
                    col_names = ", ".join(input_data.keys())
                    placeholders = ", ".join(["?"] * len(input_data))
                    values = list(input_data.values())
                    c.execute(f"INSERT INTO {selected_table} ({col_names}) VALUES ({placeholders})", values)
                    conn.commit()
                    st.success("Record inserted successfully.")
                except Exception as e:
                    st.error(f"Insertion error: {e}")
            conn.close()

    # -------------------- Tab 3: Gemini Query --------------------
    with tab3:
        st.subheader("🤖 Ask in English and Get SQL Results")
        question = st.text_input("e.g., Show all employees with salary > 50000")
        if st.button("Run Query"):
            try:
                schema_info = get_db_schema()
                sql = get_gemini_response(question, schema_info)
                cleaned_sql = sql.replace("```sql", "").replace("```", "").strip()

                st.code(cleaned_sql, language="sql")
                headers, rows = run_sql_query(cleaned_sql)

                if rows:
                    st.dataframe([dict(zip(headers, r)) for r in rows])
                else:
                    st.info("No data returned.")
            except Exception as e:
                st.error(f"Query error: {e}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out.")
