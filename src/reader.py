import json

def load_json(file_path):
    """Read the DB file

    Args:
        file_path (String): File path to the DB

    Returns:
        Dictionary: loads all the data into a dictionary to be used
    """
    with open(file_path, "r", encoding="UTF-8") as file:
        data = json.load(file)
        return data


def write_json(file_path, data):
    """Writer onto the DB

    Args:
        file_path (String): absolute file path using the Pathlib library
        data (Dictionary): data in a dictionary format
        "ID": {
            "article_name": String,
            "article_id": String,
            "brand": String,
            "price_SEK": Float,
            "category": String,
            "discount_percentage": Float,
            "stock_amount": Int
            }
    """
    with open(file_path, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent= 2)