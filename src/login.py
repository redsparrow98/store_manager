import json
from pathlib import Path
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "users.json"

"""Load users from json file"""
def load_users():
    try:
        users_path = Path(__file__).parent/"dataset"/"users.json"
        with open(users_path, "r") as f:
            raw_users = json.load(f)

        users = {}
        for username, data in raw_users.items():
            users[username] = {
                "password": generate_password_hash(data["password"]),
                "access_level": data["access_level"]
            }
        return users
    except FileNotFoundError:
        print(f"Error: {users_path} not found.")
        return{}
    except json.JSONDecodeError:
        print(f"Error: {users_path} contains invalid JSON.")
        return{}
    
"""Flask login user class"""
class User(UserMixin):
    def __init__(self, username, access_level):
        self.id = username
        self.access_level = access_level

"""User Authentication"""
def authenticate(username, password):
    users = load_users()
    user_data = users.get(username)
    if user_data and check_password_hash(user_data["password"], password):
        return User(username=username, access_level=user_data["access_level"])
    return None
