from math import prod
from flask_login import LoginManager, login_user, login_required, current_user
from flask import Flask, render_template, redirect, url_for, request, flash, session
from inventory_manager import *
from notifications import *
from account_manager import *
from login import *
from pathlib import Path

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"
TEST_USERS_FILE_PATH = BASE_DIR / "dataset" / "test_users.json"


app = Flask(__name__)
app.secret_key = "demo-key1234"


"""Flask Login Setup"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = users.get(user_id)
    if user_data:
        return User(username=user_id, access_level=user_data["access_level"])
    return None

@app.route("/", methods=["GET", "POST"])
def login():
    if "failed_attempts" not in session:
        session['failed_attempts'] = 0
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = authenticate(username, password)
       
        if user:
            session['failed_attempts'] = 0
            login_user(user)
            session["access_level"] = user.access_level
            return redirect(url_for("dashboard"))
        
        session['failed_attempts'] += 1

        if session['failed_attempts'] == 3:
            session['failed_attempts'] = 0
            return redirect(url_for('display_countdown'))
        
        flash(
            f"Invalid username or password. "
            f"{3 - session['failed_attempts']} attempt(s) left", "danger")


    return render_template("login.html")

# Gives the access level to the templates
@app.context_processor
def inject_access_level():
    access_level = session.get("access_level")

    return {"access_level": access_level}

@app.route("/dashboard")
@login_required
def dashboard():
    scan_low_stock()
    notif_count = len(get_notifications())
    return render_template(
        "dashboard.html",
        notif_count = notif_count,
        username = current_user.id,
        access_level = current_user.access_level.lower()
    )

@app.route('/locked-out')
def display_countdown():
    return render_template('locked.html')


@app.route('/inventory')
def display_inventory():
    users = load_json(TEST_USERS_FILE_PATH)
    username = current_user.id
    access_level = users[username]["access_level"]

    all_products = list_all_products()
    return render_template('inventory.html',
                        all_products=all_products,
                        username=username,
                        access_level=access_level
                        )


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


@app.route('/inventory/delete-product', methods=['GET'])
def delete_product_page():
    if request.method == "GET":
    
        article_id = request.args.get('article_id')
         
        deleted_product = delete_product(article_id)
        flash (f"{deleted_product['article_name']} with article id {article_id} has been deleted", "success")
        return redirect(url_for("display_inventory"))
    

@app.route("/notifications")
def show_notifications():
    scan_low_stock()
    notifications_list = get_notifications()
    return render_template("notification.html" , notifications = notifications_list)


@app.route('/inventory/update-product', methods=['GET', 'POST'])
def update_product_page():
    if request.method == 'POST':
        article_id = request.form.get('article_id')
        products = load_json(FILE_PATH)
        product = products[article_id]
        
        product_copy = product.copy()
        product['article_name'] = request.form.get('name', '').strip()
        product['brand'] = request.form.get('brand', '').strip()
        product['price_SEK'] = request.form.get('price', '').strip()
        product['discount_percentage'] = request.form.get('discount', '').strip()
        product['category'] = request.form.get('category', '').strip().capitalize()
        product['stock_amount'] = request.form.get('stock', '').strip()

        # If statements so it only updates if the input is valid
        if product['article_name'].isdigit() or product['article_name'] == "":
            #Shows error message and redirects to same page with original product info in case of wrong input type
            flash (f"Name cannot be digit or blank.", "error")
            return render_template("update_product.html", product=product_copy)

        elif product['brand'].isdigit() or product['brand'] == "":
            flash (f"Brand cannot be digit or blank.", "error")
            return render_template("update_product.html", product=product_copy)

        elif is_number(product['price_SEK']) == False or float(product['price_SEK']) < 0:
            flash (f"Price cannot be negative or blank.", "error")
            return render_template("update_product.html", product=product_copy)
        
        elif is_number(product['discount_percentage']) == False or int(product['discount_percentage']) < 0:
            flash (f"Discount percentage cannot be negative or blank.", "error")
            return render_template("update_product.html", product=product_copy)
            
        elif product['category'].isdigit() or product['category'] == "":
            flash (f"Category cannot be digit or blank.", "error")
            return render_template("update_product.html", product=product_copy)
        
        elif not product['stock_amount'].isdigit():
            flash (f"Stock amount cannot be text, blank or negative.", "error")
            return render_template("update_product.html", product=product_copy)
        
        # Saves the updated product information to the JSON file
        with open(FILE_PATH, 'w') as f:
            json.dump(products, f, indent=2)

        flash('Product information successfully updated!', 'success')
        product = products.get(article_id)
        return render_template('update_product.html', product=product, id=article_id)

    # Gets product details 
    article_id = request.args.get('article_id')
    product = ""

    if article_id:
        try:
            products = load_json(FILE_PATH)
            product = products.get(article_id)

        except:
            product = ""

    return render_template('update_product.html', product=product, id=article_id)



@app.route('/inventory/apply-discount', methods=['GET', 'POST'])
def apply_discount_page():
    if request.method == "GET":
        
        return render_template("apply_discount.html")

    else:
        try:
            discount_percentage = int(request.form["discount_percentage"])
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
    search_term = request.args.get('search_term', '').strip()
    if not search_term:
        return redirect(url_for('display_inventory'))

    try:
        products = load_json(FILE_PATH)

    except Exception:
        flash('Error loading products.', 'error')
        return redirect(url_for('display_inventory'))

    def build_display(product, article_id):
        return [
            ('Product ID', product.get('article_id', article_id)),
            ('Item name', product.get('article_name', '')),
            ('Brand', product.get('brand', '')),
            ('Price', f"{product.get('price_SEK', product.get('price', ''))} kr" if product.get('price_SEK', product.get('price', '')) not in (None, '') else ''),
            ('Discount percentage', f"{product.get('discount_percentage', '')}%" if product.get('discount_percentage', '') not in (None, '') else ''),
            ('Amount', f"{product.get('stock_amount', product.get('stock', ''))} pcs" if product.get('stock_amount', product.get('stock', '')) not in (None, '') else ''),
            ('Category', product.get('category', '')),
        ]

    # Matches product ID
    if search_term in products:
        item = products[search_term]
        product_display = build_display(item, search_term)
        return render_template(
            'access_product_info.html',
            product=item,
            product_display=product_display,
            display=product_display,
            searched_id=search_term,
            id=search_term,
            search_term=search_term
        )

    # Matches brand
    search_lower = search_term.lower()
    brand_results = []
    for article_id, product in products.items():
        brand = (product.get('brand') or '').lower()
        if search_lower in brand:
            display = build_display(product, article_id)
            brand_results.append((str(article_id), product, display))

    if brand_results:
        return render_template('access_product_info.html', brand_results=brand_results, brand_searched=search_term, search_term=search_term)

    flash(f'No products found for: {search_term}', 'error')
    return redirect(url_for('display_inventory'))
        

@app.route('/dashboard/delete-user', methods=['GET','POST'])
def delete_user_page():
    if request.method == "GET":
        return render_template("delete_user.html")
    
    else:
        # Asks the user to put in their own username and password to check access level
        username = request.form['username']
        password = request.form['password']
        
        # Checks if credentials are correct
        if authenticate(username, password) == None: # authenticate returns None or the username of the user
            flash (f"Wrong username or password.", "error")
            return redirect(url_for("delete_user_page"))
    
        # If credentials are correct, asks user to input username for which user they want to delete
        deleted_user = request.form['deleted_user']
        if deleted_user == username:
            flash (f"Cannot delete your own user.", "error")
            return redirect(url_for("delete_user_page"))
            
        if delete_user(deleted_user) == False:
            flash (f"User with username '{deleted_user}' not found.", "error")
            return redirect(url_for("delete_user_page"))
        
        flash (f"User '{deleted_user}' has been deleted successfully.", "success")            
        return render_template("delete_user.html")
        
@app.route('/dashboard/create-account', methods=['GET', 'POST'])
def create_account_page():
    
    if request.method == "GET":
        return render_template("create_account.html")
    
    else:
        username = request.form['username']
        access_level = request.form['access_level'] 
        password = request.form['password']
        repeat_password = request.form['repeat_password']

        success, result = create_account(username, access_level, password, repeat_password)

        # User gets passed to the login and a success message gets flashed
        if success:
            flash (result, "success")
            return render_template("create_account.html")
        else:
            for error in result:
                flash (error, "error")
            return redirect(url_for("create_account_page"))

@app.route('/dashboard/my-account', methods=['GET', 'POST'])
def account_page():
    """
    The variables username and access_level is here because they need to be defined before
    the if-statement since they are supposed to be displayed all the time in the account info
    """
    users = load_json(TEST_USERS_FILE_PATH)
    username = current_user.id
    access_level = users[username]["access_level"]

    if request.method == "GET":
        return render_template("my_account.html", 
                            username=username,
                            access_level=access_level
                            )    
    else:
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        repeat_new_password = request.form['repeat_new_password']

        success, result = update_password_page(username, current_password, new_password, repeat_new_password)

        if success:
            flash (result, "success")

        else:
            for error in result:
                flash (error, "error")
        return redirect(url_for("account_page"))

if __name__=='__main__':
    app.run(debug=True)
