from reader import *
from pathlib import Path
from flask import Flask, request, render_template

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
    


# Error handling reused to validate user input in update functions
def is_number(text: str):
    try:
        float(text)
        return True
    except:
        return False
    
    
# Render template with article info for update product functions
def create_template(article, info=""):
    return render_template(
    "update_product.html", 
    name=article["article_name"], 
    id=article["article_id"], 
    brand = article["brand"],
    price = article["price_SEK"], 
    category = article["category"], 
    discount = article["discount_percentage"],
    stock = article["stock_amount"],
    info = info)


# Searches through json and validates if input matches existing article, if not, displays an error message
def update_product_finder():
    data = load_json(FILE_PATH)
    if request.method == "POST":

        article_id = request.form.get("article_id")
        
        if article_id in data: # If article id found, renders new page where you update info
            article = data[article_id]
            return create_template(article)
        else:
            info = "No such product found. Try again." # If article not found, renders the same page the user is on and displays error message
            return render_template("update_product_finder.html", info = info)
        
    return render_template("update_product_finder.html")


def update_product():
    data = load_json(FILE_PATH)
    pressed = request.form.get("btn") # Registers if "Back" button is pressed
    
    if pressed == "back": # If button is pressed, the user gets sent back to first page
        return render_template("update_product_finder.html")
    else: # Reads new input per category from user, except for id and discount percentage which should not be changed in this function
        article_id = request.form.get("article_id") 
        article = data[article_id]
        
        article["article_name"] = request.form.get("name")
        article["brand"] = request.form.get("brand")
        article["price_SEK"] = request.form.get("price")
        article["category"] = request.form.get("category")
        article["stock_amount"] = request.form.get("stock")

        #Below is error handling for the different kinds of user input
        if article["article_name"].isdigit() or article["article_name"] == "":
            return create_template(article, "Article name cannot be digit or blank.")
        
        elif article["brand"].isdigit() or article["brand"] == "":
            return create_template(article, "Article brand cannot be digit or blank.")
        
        elif is_number(article["price_SEK"]) == False or float(article["price_SEK"]) < 0:
            return create_template(article, "Article price cannot be text, blank or negative.")
        
        elif article["category"].isdigit() or article["category"] == "":
            return create_template(article, "Article category cannot be digit or blank.")
                
        elif not article["stock_amount"].isdigit(): #isdigit() returns false for non integers and empty values.
            return create_template(article, "Article price cannot be text, blank or negative.")
        
        else: # If no errors occur, the input is written to the json file
            write_json(FILE_PATH, data)
            info = "Product information successfully updated!"
            return create_template(article, info)