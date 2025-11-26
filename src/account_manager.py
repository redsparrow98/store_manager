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
