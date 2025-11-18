import json

def load_json(file_path):
    with open(file_path, "r", encoding="UTF-8") as file:
        data = json.load(file)
        return data


def write_json(file_path, data):
    """Writer onto the JSON DB

    Args:
        file_path (_type_): file path of the JSON DB tto be opened
        data (_type_): data in a dictionary JSON format to be written onto the DB
    """
    with open(file_path, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent= 2)