import json

def load_json(file_name):
    with open (file_name) as file:
        data = json.load(file)

    

