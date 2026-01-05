from reader import *
import os, random
from pathlib import Path
from datetime import datetime

# This is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"
ORDER_FILE_PATH = BASE_DIR / "dataset" / "stock_orders.json"
RETURNS_FILE_PATH = BASE_DIR / "dataset" / "returns.json"
USER_ORDER_FILE_PATH = BASE_DIR / "dataset" / "user_orders.json"



# APPLY DISCOUNT FUNCTION
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

    # Counter to check how many products were updated(implement a message in flask?)
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

# LISTING ALL PRODUCTS FEATURE
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

# ADDING A PRODUCT FEATURE
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
    for product in products:
        if products[product]['article_name'].lower() == name.lower():
            errors.append(f"\'{products[product]['article_name']}\' is already an existing product")
    if errors:
        return False, errors

    else:
        # Find the next ID in sequence using the ternary operator
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


# DELETING A PRODUCT FEATURE
def delete_product(article_id):
    """Deleted an article using the article id frm the DB

    Args:
        article_id (String): Article ID key for the DB
    Returns: 
    Dict of the deleted products info
    """
    products = load_json(FILE_PATH)
    delete = products.pop(article_id)
    write_json(FILE_PATH, products)
    return delete

# ACCESSING A PRODUCT FEATURE AND HELPER FUNCTIONS
def format_product_data(product_info):
    """Formats a product's data when being accessed through search
    
    Args:
        product_info (dict) the specific products/product info being searched for"""
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
def list_orders():
    orders = load_json(ORDER_FILE_PATH)

    all_orders = []

    for order in orders:
        all_orders.append(orders[order])
    
    return all_orders

# Viewing order and updating order status
def access_order(status, order_number):
    """Viewing the full (restock) order information and changing order status if it's not already set to delivered
    
    Args:
        status (String) The order updated order status
        order_number (String) the order number of the specific order being accessed."""
    
    orders = load_json(ORDER_FILE_PATH)
    products = load_json(FILE_PATH)

    order = orders[order_number]
    article_id = order["article_id"]
    if order["order_status"] != "Delivered" and status != order["order_status"]:
        order["order_status"] = status
        write_json(ORDER_FILE_PATH, orders)
        
        current_stock = int(products[article_id]["stock_amount"])
        ordered_qty = int(order["quantity"])
        products[article_id]["stock_amount"] = current_stock + ordered_qty

        write_json(FILE_PATH, products)
        
        return "Delivery status successfully changed"

# Adding Orders  
def add_order(fields, username, date):
    """Placing new restock orders
    
    Args:
        fields (list) all info for the new order/orders.
        username (String) the current username of the currently logged in user
        date (String) the date when the order was placed """
    
    orders = load_json(ORDER_FILE_PATH)
    products = load_json(FILE_PATH)

    errors = []

    for order in fields:
        if not order.get("article_id").strip():
            errors.append("Article id is required")
        if int(order.get("quantity")) <= 0:
            errors.append("The ordered ammount can't be negative or zero")
        if order.get("article_id") not in products:
            errors.append(f"Article id: {order.get('article_id')} not found")
        
        if errors:
            return False, errors
        
        else:
            current_order_numbers = orders.keys()
            for order_number in current_order_numbers:
                number = order_number[1:]
            
            calculate_next = int(number) + 1
            next_order_number = "O" + str(calculate_next).zfill(4)
            product = products[order.get("article_id")]["article_name"]

            new_order = {
                "order_number": next_order_number,
                "ordered_by": username,
                "article_id": order.get("article_id"),
                "product_name": product,
                "quantity": int(order.get("quantity")),
                "order_date": date,
                "order_status": "Ordered"
                }
            
            orders[next_order_number] = new_order
            write_json(ORDER_FILE_PATH, orders)

    return True, "Order(s) successfully created"


def access_return(status, return_id,):
    """Viewing the return information, updating status, deleting and adding returned products back to stock
    Args:
        status (String) the updated status of the return
        return_id (String) the return id to access the return in the DB """
    
    returns = load_json(RETURNS_FILE_PATH)
    products = load_json(FILE_PATH)
    orders = load_json(USER_ORDER_FILE_PATH)

    return_data = returns[return_id]
    order_id = return_data["order_id"]
    
    if return_data["status"] != "Processed" and status != return_data["status"]:
        return_data["status"] = status
        write_json(RETURNS_FILE_PATH, returns)
        
    for item in orders[order_id]["items"]:
        product_id = item["product_id"]
        stock_to_add = item['quantity']
        
        product_info = products[product_id]
        product_info["stock_amount"] += stock_to_add

    write_json(FILE_PATH, products)
        
    return "Return status successfully changed"

# REGISTER NEW RETURN
def add_return(order_id, customer, date):
    """Add new return to be processed
    Args:
        article_id (String) the product getting returned
        stock (int) the returned ammount of the product
        customer (String) the customer returning the product
        date (String) the return date."""
    
    orders = load_json(USER_ORDER_FILE_PATH)
    returns = load_json(RETURNS_FILE_PATH)
    errors = []

    if not customer.strip():
        errors.append("Customer is required")
    if order_id not in orders:
        errors.append("Order number not found")
    if orders[order_id]["status"] != "delivered":
        errors.append("Order must be delivered in order to be returned ")
    for order in returns:
        if order_id == returns[order]["order_id"]:
            errors.append(f"return for order {order_id} already exists.")
    
    if errors:
        return False, errors
    else:
        random_id = "R" + f"{random.randint(0, 999):03d}"
        
        current_ids = returns.keys()
        if len(current_ids) == 1000:
            return False, f"Max amount of returns reached, cannot create a new."
            
        while random_id in current_ids:
            random_id = "R" + f"{random.randint(0, 999):03d}"
        
        next_id = random_id
        
        new_return = {
            "order_id": order_id,
            "customer": customer,
            "date": date,
            "status": "Open",
        }
        
        returns[next_id] = new_return
        
        write_json(RETURNS_FILE_PATH, returns)
        return True, f"Return for order {order_id} successfully created."
    
# DELETE RETURN
def delete_return(return_id):
    """Deletes a return using the return id from the DB

    Args:
        return_id (String): return ID key for the DB
    Returns: 
        Dict of the returns info
    """
    returns = load_json(RETURNS_FILE_PATH)
    deleted_return = returns.pop(return_id)
    write_json(RETURNS_FILE_PATH, returns)
    return deleted_return

# ADD RETURN BACK TO STOCK
def add_return_to_stock(return_id):
    """Adding returned products back to the inventory
    Args:
        return_id (String) return ID key for the DB."""
    
    returns = load_json(RETURNS_FILE_PATH)
    products = load_json(FILE_PATH)
    orders = load_json(USER_ORDER_FILE_PATH)
    
    return_info = returns.get(return_id)
    if not return_info:
        return False, "Return ID not found."
    
    order_id = return_info.get("order_id")

  
    for item in orders[order_id]["items"]:
        product_id = item["product_id"]
        stock_to_add = item['quantity']
        
        product_info = products[product_id]
        product_info["stock_amount"] += stock_to_add
        if not product_info:
            return False
        

        product_info["stock_amount"] += stock_to_add
        
        write_json(FILE_PATH, products)
        
    returns.pop(return_id)
    orders.pop(order_id)
    write_json(USER_ORDER_FILE_PATH, orders)
    write_json(RETURNS_FILE_PATH, returns)
    
    return True

# USER ORDERS AND DELIVERIES

# Loading and writing to and from products.json and user_orders.json
def load_products():
    return load_json(FILE_PATH)

def save_products(products):
    write_json(FILE_PATH, products)

def load_orders():
    return load_json(USER_ORDER_FILE_PATH)

def save_orders(orders):
    write_json(USER_ORDER_FILE_PATH, orders)


"""Return orders grouped by status for easy separation in 3 tables."""
def get_orders_grouped():
    orders = load_orders()
    grouped = {"ordered": {}, "dispatched": {}, "in transit": {}, "delivered": {}}
    for order_id, order in orders.items():
        status = order["status"]
        grouped.setdefault(status, {})[order_id] = order
    return grouped

def new_user_order(items, date):
    orders = load_orders()
    products = load_products()

    errors = []

    for order in items:
        if order["product_id"] not in products:
            errors.append(f"Product id: {order['product_id']} not found")

    if errors:
        return False, errors
    
    else:
        for order in items:
            for i in range(1, len(items)):
                if order["product_id"] == items[i]["product_id"]:
                    order["quantity"] += items[i]["quantity"]
                    items.pop(i)

        current_ids = orders.keys()
        for order_number in current_ids:
            number = order_number[3:]
            
        next_id_int = int(number) + 1 if current_ids else 1
        next_id = "ORD" + str(next_id_int).zfill(3)

        new_order = {"items": items,
                    "status": "ordered",
                    "created_at": date
                    }

        orders[next_id] = new_order
        save_orders(orders)
        return True, "Order successfully created"
    
def access_user_order(status, order_id):
    """Viewing the order information
    Args:
        return_id (String) the order id to access the order in the DB """
    
    orders = load_orders()
    order_data = orders[order_id]

    products = load_json(FILE_PATH)
    
    if order_data["status"] != "delivered" and status != order_data["status"]:
        
        for order in order_data["items"]:
            article = products[order["product_id"]]
            if article["stock_amount"] < order["quantity"]:
                return False, f"Too low stock of product #{article['article_id']}."
            elif status == "dispatched": 
                article["stock_amount"] -= order["quantity"]
                save_products(products)

        order_data["status"] = status
        save_orders(orders)
        
        return True, "Order status successfully changed"
    else:
        return False, "Order status already has this value"



# =============================================================================
# Analytics functions


def get_top_stored_brand():
    stock = load_json(FILE_PATH)

    # I choose to find the dictionary of the current brands in the inventory
    # These brands should not be hardcoded and they can always change
    brands = {}
    for item in stock.values():
        current_brand = item["brand"].capitalize()

        if current_brand not in brands:
            brands[current_brand] = 1
        else:
            brands[current_brand] += 1

    # In case there are multiple brands with same stock
    highest_stock = max(brands.values())
    top_brands = []

    for brand, count in brands.items():
        if count == highest_stock:
            top_brands.append(brand)


    top_brands.sort()
    return top_brands



def get_top_stored_product():
    stock = load_json(FILE_PATH)

    highest_stock = 0
    for item in stock.values():
        if int(item["stock_amount"]) > highest_stock:
            highest_stock = item["stock_amount"]

    top_products = []
    for item in stock.values():
        if int(item["stock_amount"]) >= highest_stock:
            top_products.append(item["article_name"])
            highest_stock = item["stock_amount"]

    return top_products


def get_done_deliveries_month():
    orders = load_json(USER_ORDER_FILE_PATH)

    current_date = datetime.now()
    orders_count = 0
    for order in orders.values():
        if order["status"] == "delivered":
            created = datetime.fromisoformat(order["created_at"])
            if created.year == current_date.year and created.month == current_date.month:
                orders_count += 1
    
    current_month = current_date.strftime("%B")
    
    return orders_count, current_month
