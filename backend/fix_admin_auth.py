import mysql.connector
import hashlib
from db_config import DB_CONFIG

def fix_admin():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Correct hash for '123456'
    correct_hash = hashlib.sha256("123456".encode()).hexdigest()
    
    print(f"Update Admin password hash to {correct_hash}...")
    
    query = "UPDATE users SET password = %s WHERE username = %s"
    cursor.execute(query, (correct_hash, "Admin"))
    conn.commit()
    
    if cursor.rowcount > 0:
        print("Admin password updated successfully.")
    else:
        print("Admin user not found or password already correct.")
        
    conn.close()

if __name__ == "__main__":
    fix_admin()
