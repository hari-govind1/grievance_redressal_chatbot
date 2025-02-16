import mysql.connector
from datetime import datetime

# MySQL Credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "harigovind",
}

def initialize_department_db(department):
    """Ensures the department database and grievances table exist before inserting data."""
    db_name = department.lower().replace(" ", "_")  # Convert to lowercase with underscores

    # Connect to MySQL (without specifying a database)
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()

    # ✅ Create department database if not exists
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    conn.commit()
    cursor.close()
    conn.close()

    # ✅ Now connect to the department database
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=db_name
    )
    cursor = conn.cursor()

    # ✅ Create grievances table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grievances (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            class VARCHAR(50) NOT NULL,
            user_department VARCHAR(100) NOT NULL,
            location TEXT NOT NULL,
            email VARCHAR(255) NOT NULL,
            additional_comments TEXT,
            summary TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def store_grievance(department, name, user_class, user_department, location, email, additional_comments, summary):
    """Stores grievance details in the respective department's database, excluding grievance text."""
    initialize_department_db(department)  # Ensure the database exists

    db_name = department.lower().replace(" ", "_")
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=db_name
    )
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO grievances (name, class, user_department, location, email, additional_comments, summary, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, user_class, user_department, location, email, additional_comments, summary, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()
