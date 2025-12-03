from reader import *
from pathlib import Path
from flask_login import UserMixin


BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "users.json"

"""Load users from json file"""
def load_users():
    try:
        raw_users = load_json(FILE_PATH)
        return raw_users
    except FileNotFoundError:
        print(f"Error: {FILE_PATH} not found.")
        return{}
    except json.JSONDecodeError:
        print(f"Error: {FILE_PATH} contains invalid JSON.")
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
    if user_data and user_data["password"] == password:
        return User(username=username, access_level=user_data["access_level"])
    return None
