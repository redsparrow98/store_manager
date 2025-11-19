import json
import os
def apply_discount_to_all_products(discount_percentage, category = None, file_path = "dataset/products.json"):
    """
    Applies a discount to all products from our dataset with an option to choose a category to apply the discount to. Uses parameters:
    1. discount_percentage(float) if input 10, discount percentage is 10%
    2. File path to the JSON file
    3. category: optional product category to apply the discount to"""

    #consider implementing a drop down menu for category selection in FLASK
    if not (0 <= discount_percentage <= 100):
        raise ValueError("Discount must be between 0 and 100")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding = "utf-8") as file:
        products = json.load(file)
    
    #counter to check how many products were updated(implement a message in flask?)
    updated_count = 0
    for product_id, product in products.items():
        if category is None or product.get("category") == category:
            original_price = product.get("price_SEK" , 0)
            if original_price > 0:
                discounted_price = round (original_price * (1 - discount_percentage / 100) , 2)
                product["discounted_price_SEK"] = discounted_price
                product["discount_percentage"] = discount_percentage
                updated_count += 1

    with open(file_path, "w" , encoding = "utf-8") as file:
        json.dump(products, file, indent = 2, ensure_ascii = False)

    print(f"Applied {discount_percentage}% discount to all products.")        
