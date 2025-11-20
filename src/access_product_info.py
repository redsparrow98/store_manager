from flask import Flask, request
from reader import load_json

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
        return f"{value:.2f} SEK"
    
    elif key == "discount_percentage":
        return f"{int(value)}%"
    
    elif key == "category":
        return str(value).capitalize()
    
    return str(value)


@app.route("/", methods=["GET", "POST"])
def index():
    data = load_json("dataset/products.json")

    product = None
    message = ""

    if request.method == "POST":
        product_id = request.form.get("product_id", "").strip()

        if product_id in data:
            product = data[product_id]
            
        else:
            message = "Product not found."

    html = """
    <h1>Access Product</h1>
    <form method="POST">
        <label>Enter product ID:</label><br>
        <input type="text" name="product_id" required>
        <button type="submit">Search</button>
    </form>
    <br>
    """

    if message:
        html += f"<p style='color:red;'>{message}</p>"

    if product:
        html += f"<h2>Product information for {product['article_name']}</h2><ul>"
        for key, value in product.items():
            html += f"<li><b>{labels.get(key, key)}:</b> {format_value(key, value)}</li>"
        html += "</ul>"

    return html


if __name__ == "__main__":
    app.run(debug=True)
