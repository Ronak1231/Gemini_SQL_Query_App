
# 🛢️ Gemini SQL Query App  
A powerful Streamlit application that leverages Google Gemini AI to convert natural language questions into SQL queries and execute them on an SQLite database.  

## Features  
- **Natural Language to SQL Conversion**: Ask questions in plain English, and the app generates SQL queries using Gemini AI.  
- **Database Integration**: Execute the generated SQL queries on an SQLite database (`student.db`) and retrieve the results.  
- **Dynamic Table Management**: Add, view, and manipulate student records in the `STUDENT` table.  

---

## 📋 Prerequisites  
1. Python 3.7 or higher  
2. A valid **Google Gemini API Key**  
3. SQLite  

---

## 🛠️ Setup Instructions  

### 1. Clone the Repository  
```bash  
git clone https://github.com/yourusername/gemini-sql-query-app.git  
cd gemini-sql-query-app  
```  

### 2. Create a Virtual Environment  
```bash  
python -m venv venv  
```  

### 3. Activate the Virtual Environment  
- **Windows**:  
  ```bash  
  venv\Scripts\activate  
  ```  
- **macOS/Linux**:  
  ```bash  
  source venv/bin/activate  
  ```  

### 4. Install Dependencies  
```bash  
pip install -r requirements.txt  
```  

### 5. Set Up Environment Variables  
Create a `.env` file in the project directory and add your Google Gemini API key:  
```
GOOGLE_GEMINI_KEY=your_api_key_here  
```  
### 6. Interact with the Database  
Use the second script to create and insert records into the `STUDENT` table:  
```bash  
python sql.py  
```

### 7. Run the Application  
```bash  
streamlit run app.py  
```

---

## ✨ Example Queries  
1. **How many entries of records are present?**  
   - Generated SQL: `SELECT COUNT(*) FROM STUDENT;`  

2. **Tell me all the students studying in the Data Science class.**  
   - Generated SQL: `SELECT * FROM STUDENT WHERE CLASS='Data Science';`  

---

## 🙌 Contributing  
Feel free to fork this repository, make improvements, and submit a pull request.  

---

## 🐛 Troubleshooting  
If you encounter issues, please create an issue in this repository.  

---

## 📧 Contact  
For inquiries or support, contact [ronakbansal12345@gmail.com].  
