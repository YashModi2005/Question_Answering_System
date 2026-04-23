import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG

def setup_database():
    try:
        # Connect to MySQL server (without database)
        conn_config = DB_CONFIG.copy()
        db_name = conn_config.pop("database")
        
        connection = mysql.connector.connect(**conn_config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' ready.")
        
        # Use database
        cursor.execute(f"USE {db_name}")
        
        # Create users table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        print("Table 'users' ready.")
        
        connection.commit()
        
    except Error as e:
        print(f"Error setting up database: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()
