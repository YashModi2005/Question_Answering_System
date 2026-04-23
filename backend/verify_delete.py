import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import auth_utils

user_to_delete = "admin"
print(f"Attempting to delete {user_to_delete}...")
success = auth_utils.delete_user(user_to_delete)
print(f"Success: {success}")

users = auth_utils.get_all_users()
print(f"Remaining users: {list(users.keys())}")
if user_to_delete not in users:
    print("VERIFICATION PASSED: User removed from storage.")
else:
    print("VERIFICATION FAILED: User still exists in storage.")
