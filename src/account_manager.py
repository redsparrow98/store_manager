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
            "password": generate_password_hash(password),
            "access_level": access_level,
        }
        write_json(USERS_FILE_PATH, users)
    

        # file for testing only so we can see the actualy password not the hashed one
        test_user = load_json(TEST_USERS_FILE_PATH)
        test_user[username] = {
            "password": password,
            "access_level": access_level
        }
        write_json(TEST_USERS_FILE_PATH, test_user)

        return True, "Account succesfully created."



# Deletes user if correct access level
def delete_user(deleted_user):
    users = load_json(USERS_FILE_PATH)
    
    if deleted_user not in users:
        return False
    else:
        users.pop(deleted_user)
        write_json(USERS_FILE_PATH, users)
    
        print(users)
        return True

# Checks if username and password are entered correctly
def check_credentials(username, password):
    users = load_json(USERS_FILE_PATH)
    
    if username in users and check_password_hash(users[username]['password'], password):
        return True
    else:
        return False
    

# Checks if access level is manager or employee
def is_manager(username):
    users = load_json(USERS_FILE_PATH)
    
    if username in users and users[username]['access_level'] == "manager":
        return True
    else:
        return False
