import mysql.connector
from db_config import DB_CONFIG

def check_users():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, password, role FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"User: {user['username']}, Role: {user['role']}, Password Hash: {user['password']}")
    conn.close()

if __name__ == "__main__":
    check_users()
