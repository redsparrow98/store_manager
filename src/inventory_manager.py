from reader import *
from pathlib import Path

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"


def list_all_products():
    all_products =[]
    data = load_json(FILE_PATH)
    for id, info in data.items():
        article_id = id
        product = info['article_name']
        brand = info['brand']

        format = f"#{article_id} - {product} - {brand}"
        
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

    errors = []

    if not name.strip():
        errors.append("Product name is required")
    if not brand.strip():
        errors.append("Brand is required")
    if float(price) < 0:
        errors.append("Price cant be negative")
    if not category.strip():
        errors.append("Category is required")
    if not (0<= float(discount) <=100):
        errors.append("Discount amount is not valid (0-100%)")
    if int(stock) < 0:
        errors.append("Stock cant be negative")
    
    if errors:
        return False, errors

    else:
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
        return True, f"Product name '{name}' added successfully, ID: {next_id}"



def delete_product(article_id):
    products = load_json(FILE_PATH)
    products.pop(article_id)
    write_json(FILE_PATH, products)



def access_product():
    
    data = load_json(FILE_PATH)
    
    # List of all products to choose from
    list_all_products()

    accessed_product = input("Input the product id of the product you want to access. ")

    if accessed_product in data:
        print(f"Printing product information for {data[accessed_product]['article_name']}:")
        
        for key in data[accessed_product]:
            print (f"{key}: {data[accessed_product][key]}")
            
    else:
        print("Product not found")
        return
    
