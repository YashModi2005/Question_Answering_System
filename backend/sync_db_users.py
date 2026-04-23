import mysql.connector
import json
import os
from db_config import DB_CONFIG

USER_DB_PATH = "users.json"

def sync_users():
    if not os.path.exists(USER_DB_PATH):
        print("users.json not found")
        return

    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for username, info in data.items():
        pwd_hash = info["password"]
        role = info["role"]
        
        # Use ON DUPLICATE KEY UPDATE to ensure passwords are correct
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE password = %s, role = %s"
        cursor.execute(query, (username, pwd_hash, role, pwd_hash, role))
        
    conn.commit()
    print(f"Synced {len(data)} users to MySQL.")
    conn.close()

if __name__ == "__main__":
    sync_users()
