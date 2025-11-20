from flask import Flask, render_template, redirect, url_for, request, flash
from inventory_manager import *

app = Flask(__name__)
app.secret_key = "demo-key1234"


from reader import load_json
from inventory_manager import list_all_products

labels = {
    "article_name": "Product name",
    "article_id": "Product ID",
    "brand": "Brand",
    "price_SEK": "Price",
    "category": "Category",
    "discount_percentage": "Discount percentage",
    "stock_amount": "Stock amount",
}

def format_value(key, value):
    if key == "price_SEK":
        return f"{value:.2f} SEK"
    
    elif key == "discount_percentage":
        return f"{int(value)}%"
    
    elif key == "category":
        return str(value).capitalize()
    
    else:
        return str(value)

def access_product():
    data = load_json("dataset/products.json")
    list_all_products()

    accessed_product = input("\nInput the product id of the product you want to access: ").strip()

    if accessed_product in data:
        product = data[accessed_product]
        print(f"\nPrinting product information for {product['article_name']}:")

        for key in product:
            print(f"{labels.get(key, key)}: {format_value(key, product[key])}")

    else:
        print("Product not found")

if __name__=='__main__':
    app.run(debug=True)
