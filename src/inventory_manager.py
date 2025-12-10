from reader import *
import os
from pathlib import Path

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"
RET_FILE_PATH = BASE_DIR / "dataset" / "returns.json"


#APPLY DISCOUNT FUNCTION
def apply_discount_to_products(discount_percentage, category=None):
    """Applies a discount to all products from our dataset with an option to choose a category to apply the discount to

    Args:
        discount_percentage (float): if input 10, discount percentage is 10%
        category (String, optional): Applies discount to a category if parameter is inputted, Defaults to None.

    Raises:
        ValueError: Raises a value error if discount parameter is outside of expected range 0-100.
        FileNotFoundError: Raises a file not found error if the DB file is not existent.
    """
    if discount_percentage is None or discount_percentage == "":
        raise ValueError("You must enter a discount percentage.")

    try:
        discount_percentage = float(discount_percentage)
    except (TypeError, ValueError):
        raise ValueError("Discount must be a number between 0 and 100.")
    if not (0 <= discount_percentage <= 100):
        raise ValueError("Discount must be between 0 and 100")
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(f"File not found: {FILE_PATH}")
    
    dataset = load_json(FILE_PATH)

    #counter to check how many products were updated(implement a message in flask?)
    updated_count = 0
    for product in dataset.values():
        if category is None or product.get("category") == category.capitalize():
            original_price = product.get("price_SEK" , 0)
            if original_price > 0:
                discounted_price = round (original_price * (1 - discount_percentage / 100) , 2)
                product["discounted_price_SEK"] = discounted_price
                product["discount_percentage"] = discount_percentage
                updated_count += 1

    write_json(FILE_PATH, dataset)
    return f"Applied {discount_percentage}% discount."

#LISTING ALL PRODUCTS FEATURE
def list_all_products():
    """Lists all current products in the inventory

    Returns:
        List: List of all the products in the DB
    """
    all_products =[]
    data = load_json(FILE_PATH)
    for article_id, info in data.items():
        all_products.append({
            "article_id" : article_id,
            "article_name": info.get("article_name", ""),
            "category": info.get("category", ""),
            "price_SEK": info.get("price_SEK", 0),
            "discount_percentage": info.get("discount_percentage", 0),
            "stock_amount": info.get("stock_amount", 0),
            "brand": info.get("brand", "")
        })
        
    return all_products

#ADDING A PRODUCT FEATURE
def add_product(name,brand,price,category,discount,stock):
    """creates a new product for the database from the given parameters.
    The article id is calculated based on the current database

    Args:
        name (String): Name of the new product
        brand (String): Brand of the new product
        price (Float): base price of the new product
        category (String): Category of the new product
        discount (Float): Discount amount of the new product
        stock (Integer): Stock amount of the new product
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
    if not (0 <= float(discount) <= 100):
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


#DELETING A PRODUCT FEATURE
def delete_product(article_id):
    """Deleted an article using the article id frm the DB

    Args:
        article_id (String): Article ID key for the DB
    """
    products = load_json(FILE_PATH)
    delete = products.pop(article_id)
    write_json(FILE_PATH, products)
    return delete

#ACCESSING A PRODUCT FEATURE AND HELPER FUNCTIONS
def format_product_data(product_info):
    labels = {
    "article_name": "Product name",
    "article_id": "Product ID", 
    "brand": "Brand",
    "price_SEK": "Price",
    "category": "Category",
    "discount_percentage": "Discount percentage",
    "stock_amount": "Stock amount",
    }

    formatted_data = []

    for key, value in labels.items():
        if key in product_info:
            raw_value = product_info[key]

            if key == "price_SEK":
                formatted_value = f"{float(raw_value):,.2f} SEK"
            elif key == "discount_percentage":
                formatted_value = f"{int(raw_value)}%"
            elif key == "category":
                formatted_value = str(raw_value).capitalize()
            else:
                formatted_value = str(raw_value)

            formatted_data.append((value, formatted_value))

    return formatted_data

def find_brand_matches(products_data, search_term):
    matches = []
    search_lower = search_term.lower()
    
    for product_id, product_info in products_data.items():
        if not product_info:
            continue
            
        brand_value = product_info.get("brand")
        if brand_value and brand_value.lower() == search_lower:
            formatted_products = format_product_data(product_info)
            matches.append((product_id, product_info, formatted_products))

    return matches

# Error handling reused to validate user input in update functions
def is_number(text: str):
    try:
        float(text)
        return True
    except:
        return False

# REGISTER NEW RETURN
def add_return(article_id, stock, customer, date, status):
    returns = load_json(RET_FILE_PATH)

    errors = []
    
    if not article_id.strip():
        errors.append("Article id is required")
    if stock < 0:
        errors.append("Stock cannot be negative")
    if not customer.strip():
        errors.append("Customer is required")
    
    if errors:
        return False, errors
    else:
        # Figure out how to make return id with letters in the beginning
        current_ids = returns.keys()
        next_id_int = int(max(current_ids)) + 1 if current_ids else 1
        next_id = str(next_id_int).zfill(4)
        
        new_return = {
            "article_id": article_id,
            "customer": customer,
            "date": date,
            "status": status,
            "stock_amount": stock
        }
        
        returns[next_id] = new_return
        
        write_json(RET_FILE_PATH, returns)
        return True, f"Return for product {article_id} successfully created."
    
# DELETE RETURN
def delete_return(return_id):
    returns = load_json(RET_FILE_PATH)
    deleted_return = returns.pop(return_id)
    write_json(RET_FILE_PATH, returns)
    return deleted_return

# ADD RETURN BACK TO STOCK
def add_return_to_stock(return_id):
    returns = load_json(RET_FILE_PATH)
    products = load_json(FILE_PATH)
    
    return_info = returns.get(return_id)
    if not return_info:
        return False, "Return ID not found."
    
    article_id = return_info.get("article_id")
    stock_to_add = return_info.get("stock_amount", 0)
    
    product_info = products.get(article_id)
    if not product_info:
        return False, "Associated product not found."
    
    current_stock = product_info.get("stock_amount", 0)
    product_info["stock_amount"] = current_stock + stock_to_add
    
    write_json(FILE_PATH, products)
    
    returns.pop(return_id)
    write_json(RET_FILE_PATH, returns)
    
    return True, f"Added {stock_to_add} units back to stock for product ID {article_id}."


