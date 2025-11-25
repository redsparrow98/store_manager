from flask import Flask, render_template, redirect, url_for, request, flash
from inventory_manager import *
from notifications import *



app = Flask(__name__)
app.secret_key = "demo-key1234"


@app.route('/')
def display_dashboard():
    scan_low_stock()
    notif_count = len(get_notifications())
    return render_template('dashboard.html',notif_count=notif_count)


@app.route('/inventory')
def display_inventory():
    all_products = list_all_products()
    return render_template('inventory.html', all_products=all_products)


@app.route('/inventory/add-product', methods=['GET', 'POST'])
def add_product_page():
    if request.method == "GET":
        return render_template("add_product.html")
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
    notifications_list = get_notifications()
    return render_template("notifications.html" , notifications = notifications_list)


@app.route('/inventory/update-product-finder', methods = ['GET', 'POST'])
def update_product_finder_page():
    return update_product_finder()


@app.route('/inventory/update-product', methods = ['GET', 'POST'])
def update_product_two():
    return update_product()


@app.route('/inventory/apply-discount', methods=['GET', 'POST'])
def apply_discount_page():
    if request.method == "GET":
        
        return render_template("apply_discount.html")

    else:
        try:
            discount_percentage = float(request.form["discount_percentage"])
            category = request.form.get("category")  

            apply_discount_to_products(discount_percentage, category)

            flash(f"Applied {discount_percentage}% discount successfully!", "success")
        except ValueError as ve:
            flash(str(ve), "error")
        except FileNotFoundError as fe:
            flash(str(fe), "error")
        except Exception as e:
            flash(f"Unexpected error: {e}", "error")

        return redirect(url_for("apply_discount_page"))


@app.route("/inventory/access-product-information", methods=["GET", "POST"])
def access_product():
    search_input = request.values.get("search_term", "")
    stripped_search = search_input.strip()

    result_data = access_product_landing_page(stripped_search)
    if "brand_search" in result_data:
        return render_template(
            result_data["template"],
            products = result_data["products"],
            product = result_data["product"],
            display = result_data["display"],
            brand_results = result_data["brand_results"],
            brand_search = result_data["brand_search"],
            error = result_data["error"]
            )
    else:
        return render_template(
            result_data["template"],
            products = result_data["products"],
            product = result_data["product"],
            display = result_data["display"],
            brand_results = result_data["brand_results"],
            error = result_data["error"]
            )


if __name__=='__main__':
    app.run(debug=True)
