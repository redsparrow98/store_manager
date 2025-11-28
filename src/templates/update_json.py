import json
from werkzeug.security import generate_password_hash
from pathlib import Path

FILE = Path("dataset/users.json")

with open (FILE, "r") as f:
    users = json.load(f)

for u in users:
    users[u]["password"] = generate_password_hash(users[u]["password"])

with open(FILE, "w") as f:
    json.dump(users, f, indent=2)
    
print("JSON updated with hashed passwords")