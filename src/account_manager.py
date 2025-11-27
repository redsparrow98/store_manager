from reader import *
import os
from pathlib import Path

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "users.json"

# Deletes user if correct access level
def delete_user(deleted_user):
    users = load_json(FILE_PATH)
    
    if deleted_user not in users:
        return False
    else:
        users.pop(deleted_user)
        write_json(FILE_PATH, users)
    
        print(users)
        return True

# Update password

def update_password_page(username, current_password, new_password, repeat_new_password):
    users = load_json(FILE_PATH)

    errors = []

    if current_password != users[username]['password']:
        errors.append("Wrong password, try again")
    
    if current_password == new_password:
        errors.append("The new and the current password can't be the same.")
    
    if repeat_new_password != new_password:
        errors.append("Passwords don't match")
    
    if errors:
        return False, errors
    
    else:    
        users[username]['password'] = new_password
        return True, "Password succedfully changed"

# Checks if username and password are entered correctly
def check_credentials(username, password):
    users = load_json(FILE_PATH)
    
    if username in users and password == users[username]['password']:
        return True
    else:
        return False
    

# Checks if access level is manager or employee
def is_manager(username):
    users = load_json(FILE_PATH)
    
    if username in users and users[username]['access_level'] == "manager":
        return True
    else:
        return False
