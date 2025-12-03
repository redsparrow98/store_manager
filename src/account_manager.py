from reader import *
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
USERS_FILE_PATH = BASE_DIR / "dataset" / "users.json"
TEST_USERS_FILE_PATH = BASE_DIR / "dataset" / "test_users.json"

# Creates a new account if username not already taken
def create_account(username, access_level, password, repeat_password):
    users = load_json(USERS_FILE_PATH)
    
    errors = []

    if username in users:
        errors.append("Username already exists, please choose another username")
    if len(username.strip()) == 0:
        errors.append("Username is required")
    if len(password.strip()) == 0:
        errors.append("Password is required")
    if repeat_password != password:
        errors.append("Repeated password doesn't match password")
    if not access_level.strip():
        errors.append("Access level is required.")

    if errors: 
        return False, errors
    
    else:
        users[username] = {
            "password": password,
            "access_level": access_level,
        }
        write_json(USERS_FILE_PATH, users)

        return True, "Account succesfully created."


# Deletes user if correct access level

def delete_user(deleted_user):
    users = load_json(USERS_FILE_PATH)
    test_users = load_json(TEST_USERS_FILE_PATH)
    
    if deleted_user not in users:
        return False
    else:
        users.pop(deleted_user)
        test_users.pop(deleted_user, None)

        write_json(USERS_FILE_PATH, users)
        write_json(TEST_USERS_FILE_PATH, test_users)
        
        print(users)
        return True
    
# Update password

def update_password_page(username, current_password, new_password, repeat_new_password):
    
    users = load_json(USERS_FILE_PATH)

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
        write_json(USERS_FILE_PATH, users)
        return True, "Password succesfully changed"

# Checks if username and password are entered correctly
def check_credentials(username, password):
    users = load_json(USERS_FILE_PATH)
    
    if username in users and check_password_hash(users[username]['password'], password):
        return True
    else:
        return False
    

# Checks if access level is manager or employee
def is_manager(username):
    users = load_json(TEST_USERS_FILE_PATH)
    
    if username in users and users[username]['access_level'] == "Manager":
        return True
    else:
        return False
