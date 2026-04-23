import json
import os
import hashlib
from mysql.connector import Error
from db_config import get_db_connection

# Removed USER_DB_PATH as we are moving to MySQL

def hash_password(password: str) -> str:
    """Simple SHA-256 hashing for professional password storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username, password):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT username, password, role FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user and user["password"] == hash_password(password):
            return user
        return None
    except Error as e:
        print(f"Database error during verification: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def register_user(username, password, role="user"):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        # Check if user already exists
        check_query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            return None
            
        # Insert new user
        insert_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, hash_password(password), role))
        connection.commit()
        
        return {"username": username, "role": role}
    except Error as e:
        print(f"Database error during registration: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def reset_user_password(username, new_password):
    """Admin: Reset a user's password. Returns True on success, None if not found."""
    connection = get_db_connection()
    if not connection:
        return None
        
    try:
        cursor = connection.cursor()
        update_query = "UPDATE users SET password = %s WHERE username = %s"
        cursor.execute(update_query, (hash_password(new_password), username))
        connection.commit()
        
        if cursor.rowcount > 0:
            return True
        return None
    except Error as e:
        print(f"Database error during password reset: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_user(username):
    """Deletes a user from the system. Cannot delete primary 'Admin'."""
    if username == "Admin":
        return False
        
    connection = get_db_connection()
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        delete_query = "DELETE FROM users WHERE username = %s"
        cursor.execute(delete_query, (username,))
        connection.commit()
        
        return cursor.rowcount > 0
    except Error as e:
        print(f"Database error during deletion: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_count():
    """Returns the total number of registered users."""
    connection = get_db_connection()
    if not connection:
        return 0
        
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        return count
    except Error as e:
        print(f"Database error getting user count: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_users():
    """Returns all users in a dictionary structure for the dashboard."""
    connection = get_db_connection()
    if not connection:
        return {}
        
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username, role FROM users")
        users = cursor.fetchall()
        # Format as {username: {"role": role}} to maintain compatibility with app.py
        return {u["username"]: {"role": u["role"]} for u in users}
    except Error as e:
        print(f"Database error getting all users: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def load_users():
    """Wrapper for legacy code compatibility. Returns all users from MySQL."""
    return get_all_users()
