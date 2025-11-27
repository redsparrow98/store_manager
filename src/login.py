import json
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "users.json"

"""Load users from json file"""
def load_users():
    try:
        users_path = Path(__file__).parent/"dataset"/"users.json"
        with open(users_path, "r") as f:
            return json.load(f)
    except FileExistsError:
        print(f"Error: {users_path} not found.")
        return[]
    except json.JSONDecodeError:
        print(f"Error: {users_path} contains invalid JSON.")
        return[]

"""Checks if the username/password is valid and returns user dictionary or none"""    
def check_login(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return{
                "user_id": user["user_id"],
                "username": user["username"],
                "access_leve'": user["access_leve;"]
            }
        return None
