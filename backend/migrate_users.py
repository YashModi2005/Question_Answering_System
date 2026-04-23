import json
import os
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG, get_db_connection

USER_DB_PATH = os.path.join(os.path.dirname(__file__), "users.json")

def migrate_users():
    if not os.path.exists(USER_DB_PATH):
        print("No users.json found to migrate.")
        return

    try:
        connection = get_db_connection()
        if not connection:
            print("Failed to connect to MySQL. Is the service running and credentials correct in db_config.py?")
            return
            
        cursor = connection.cursor()
        
        with open(USER_DB_PATH, "r") as f:
            users_data = json.load(f)
            
        print(f"Found {len(users_data)} users in users.json. Starting migration...")
        
        for username, data in users_data.items():
            password = data["password"]
            role = data["role"]
            
            # Using IGNORE to avoid errors if users already exist
            insert_query = "INSERT IGNORE INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, password, role))
            
        connection.commit()
        print("Migration complete.")
        
    except Error as e:
        print(f"Error during migration: {e}")
    finally:
        if 'connection' in locals() and connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    migrate_users()
