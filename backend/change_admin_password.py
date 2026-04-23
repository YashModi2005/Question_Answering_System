import auth_utils
import getpass

def change_admin_password():
    print("--- Secure Admin Password Changer ---")
    new_password = getpass.getpass("Enter NEW secure password for 'Admin': ")
    confirm_password = getpass.getpass("Confirm NEW secure password: ")
    
    if new_password != confirm_password:
        print("Error: Passwords do not match!")
        return
        
    if len(new_password) < 8:
        print("Warning: Password is short. It is recommended to use at least 8 characters.")

    success = auth_utils.reset_user_password("Admin", new_password)
    if success:
        print("\nSUCCESS: Admin password has been updated in MySQL.")
        print("Google security warnings should stop now for this account.")
    else:
        print("\nERROR: Could not find 'Admin' user or database connection failed.")

if __name__ == "__main__":
    change_admin_password()
