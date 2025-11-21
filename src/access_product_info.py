from reader import load_json
from pathlib import Path
from flask import Flask, request, render_template

BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"

app = Flask(__name__)

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
        return f"{float(value):,.2f} SEK"
    
    elif key == "discount_percentage":
        return f"{int(value)}%"
    
    elif key == "category":
        return str(value).capitalize()
    
    else:
        return str(value)

def create_product_list(products_data):
    product_list = []

    for product_id, product_info in products_data.items():
        product_name = ""

        if product_info and "article_name" in product_info:
            product_name = product_info["article_name"]

        product_list.append((product_id, product_name))
    return product_list

def format_product_data(product_info):
    formatted_data = []

    for key, value in labels.items():
        if key in product_info:
            key_value = product_info[key] 
            formatted_value = format_value(key, key_value)
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

def access_product_landing_page():
    products_data = load_json(str(FILE_PATH))
    product_list = create_product_list(products_data)
    
    search_input = request.values.get("search_term", "")
    stripped_search = search_input.strip()

    if not stripped_search:
        return render_template(
            "access_product_info.html",
            products=product_list,
            product=None,
            display=None,
            brand_results=None,
            error=None,
        )

    # Matches product ID 
    if stripped_search in products_data:
        matching_product = products_data[stripped_search]
        formatted_display = format_product_data(matching_product)

        return render_template(
            "access_product_info.html",
            products=product_list,
            product=matching_product,
            display=formatted_display,
            brand_results=None,
            error=None,
        )

    # Matches brand
    brand_matches = find_brand_matches(products_data, stripped_search)

    if brand_matches:
        return render_template(
            "access_product_info.html",
            products=product_list,
            product=None,
            display=None,
            brand_results=brand_matches,
            brand_searched=stripped_search,
            error=None,
        )

    # No match
    else:
        return render_template(
            "access_product_info.html",
            products=product_list,
            product=None,
            display=None,
            brand_results=None,
            error=f"No match found for '{stripped_search}'",
        )

if __name__ == "__main__":
    app.run(debug=True)