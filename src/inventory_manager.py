from reader import *
from pathlib import Path

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"


def list_all_products():
    all_products =[]
    data = load_json('dataset/products.json')
    for id, info in data.items():
        article_id = id
        product = info['article_name']
        brand = info['brand']
        price = info['price_SEK']
        discount = info['discount_percentage']

        format = f"""art#{article_id}
-------
Name: {product}
Brand: {brand}
Standard price: {price}
Current discount: {int(discount * 100)}%
Current price: {price - (price * discount)}"""
        
        all_products.append(format)
    return all_products
        


def add_product(name,brand,price,category,discount,stock):
    """creates a new product for the database from the given parameters.
    The article id is calculated based on the current database

    Args:
        name (String): _description_
        brand (String): _description_
        price (Float): _description_
        category (String): _description_
        discount (Float): _description_
        stock (Integer): _description_
    """
    products = load_json(FILE_PATH)
    
    # find the next ID in sequence using the ternary operator
    current_ids = products.keys()
    next_id_int = int(max(current_ids)) + 1 if current_ids else 1
    next_id = str(next_id_int).zfill(4)


    new_item = {
        "article_name": name,
        "article_id": next_id,
        "brand": brand,
        "price_SEK": float(price),
        "category": category,
        "discount_percentage": float(discount),
        "stock_amount": int(stock)
    }

    products[next_id] = new_item
    write_json(FILE_PATH, products)
