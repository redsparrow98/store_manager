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

@app.route('/inventory/delete-product', methods=['GET','POST'])
def delete_product_page():
    if request.method == "GET":
        return render_template("delete_product.html")
    
    else:
        data = load_json('dataset/products.json')
        article_id = request.form['article_id']
        
        if article_id in data:
            flash (f"{data[article_id]['article_name']} with article id {article_id} has been deleted successfully", "success")
            delete_product(article_id)
            return render_template("delete_product.html")
        
        else:
            flash (f"Product with article id {article_id} not found", "error")
            return redirect(url_for("delete_product_page"))


        for key in product:
            print(f"{labels.get(key, key)}: {format_value(key, product[key])}")

    else:
        print("Product not found")

if __name__=='__main__':
    app.run(debug=True)
