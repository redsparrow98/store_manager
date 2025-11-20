from flask import Flask, render_template, redirect, url_for, request, flash
from inventory_manager import *
from notification import notifications, scan_low_stock, get_notifications

app = Flask(__name__)
app.secret_key = "demo-key1234"


@app.route('/')
def display_dashboard():
    scan_low_stock()
    notif_count = len(get_notifications())
    return render_template('dashboard.html',notif_count=notif_count)


@app.route('/inventory')
def display_inventory():
    return render_template('inventory.html')


@app.route('/inventory/all-products')
def display_all_products():
    all_products = list_all_products()
    return render_template('all_products.html', all_products = all_products)


@app.route('/inventory/add-product', methods=['GET', 'POST'])
def add_product_page():
    # gets triggered once add-product button in inventory is selected
    if request.method == "GET":
        return render_template("add_product.html")
    # gets triggered when the add button is selected in the add-product route
    else:
        name = request.form["name"]
        brand = request.form["brand"]
        price = request.form["price"]
        category = request.form["category"]
        discount = request.form.get("discount", 0)
        stock = request.form.get("stock", 0)

        success, result = add_product(name,brand,price,category,discount,stock)

        if success:
            flash(result, "success")
        else:
            for error in result:
                flash(error, "error")
        
        return render_template("add_product.html")
    
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
        
@app.route("/notifications")
def show_notifications():
    scan_low_stock()
    return render_template("notifications.html" , notifications = notifications)


if __name__=='__main__':
    app.run(debug=True)
