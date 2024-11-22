import sqlite3 

# Connection to our sqlite database
connection = sqlite3.connect("student.db")

# Create a cursor object to insert record, create table, retrieve records
cursor = connection.cursor()

# Create our table
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT (
    PRN INTEGER PRIMARY KEY,
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
);
"""
cursor.execute(table_info)

# Function to insert a student record
def insert_student():
    prn = input("Enter PRN (number): ")
    name = input("Enter Name: ")
    class_name = input("Enter Class: ")
    section = input("Enter Section: ")
    marks = input("Enter Marks (integer): ")
    
    cursor.execute('''INSERT INTO STUDENT (PRN, NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?, ?)''', 
                   (prn, name, class_name, section, marks))

# Ask the user how many records they want to insert
num_records = int(input("How many student records do you want to insert? "))

for _ in range(num_records):
    print(f"\nEntering details for student {_ + 1}:")
    insert_student()

# Display all the records:
print('\nThe inserted records are:')
data = cursor.execute('''SELECT * FROM STUDENT''')
for row in data:
    print(row)

# Close the connection
connection.commit()
connection.close()