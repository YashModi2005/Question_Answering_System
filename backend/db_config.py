
# MySQL Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",  # UPDATED
    "database": "qa_system"
}

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
