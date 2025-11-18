import json

def load_json(file_path):
    with open(file_path) as file:
        data = json.load(file)
        