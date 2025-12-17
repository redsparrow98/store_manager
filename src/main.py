from math import prod
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, redirect, url_for, request, flash, session
from inventory_manager import *
from notifications import *
from account_manager import *
from login import *
from pathlib import Path

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"
USERS_FILE_PATH = BASE_DIR / "dataset" / "users.json"
RETURNS_FILE_PATH = BASE_DIR / "dataset" / "returns.json"
ORDER_FILE_PATH = BASE_DIR / "dataset" / "stock_orders.json"


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


@app.route("/dashboard")
@login_required
def dashboard():
    scan_low_stock()
    notif_count = len(get_notifications())
    today = datetime.today().strftime("%B %d, %Y") # Date formatting

    #to load datasets for dashboard values
    products = load_json(FILE_PATH)
    users = load_json(USERS_FILE_PATH)

    #getting all the values needed for dashboard
    total_products = len(products)
    low_stock = 0
    for product in products.values():
        if int(product.get("stock_amount", 0)) <= 5:
            low_stock += 1
    total_users = len(users)
    #need to add it for returns here eventually

    username = current_user.id
    

    return render_template(
        "dashboard.html",
        notif_count = notif_count,
        name = users[username]["name"],
        access_level = users[username]['access_level'],
        today = today,
        total_products = total_products,
        low_stock = low_stock,
        total_users = total_users
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()  
    session.clear()        
    return redirect(url_for("login"))

# Gives the access level to the templates
@app.context_processor
def inject_access_level():
    access_level = session.get("access_level")

    return {"access_level": access_level}

@app.route('/locked-out')
def display_countdown():
    return render_template('locked.html')


@app.route("/inventory", methods=["GET"])
def display_inventory():
    products = load_json(FILE_PATH)
    
    for article_id, info in products.items():
        category = info['category']

    search_term = request.args.get("search_term", "").strip()

    try:
        products = load_json(FILE_PATH)  
        
    except Exception:
        flash("Error loading products.", "error")
        products = {}

    # No search term, show all products
    if not search_term:
        return render_template("inventory.html", products=products, search_term="")

    # Matches product ID
    if search_term in products:
        filtered = {search_term: products[search_term]}
        return render_template("inventory.html", products=filtered, search_term=search_term)

    # Matches brand
    search_term_lower = search_term.lower()
    filtered = {}
    for article_id, item in products.items():
        brand = (item.get("brand") or "").lower()
        if search_term_lower in brand:
            filtered[article_id] = item

    users = load_json(USERS_FILE_PATH)
    username = current_user.id
    access_level = users[username]["access_level"] 

    return render_template("inventory.html", products=filtered, search_term=search_term, access_level=access_level)


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
def notifications_page():
    scan_low_stock() 
    notifications = get_notifications()
    return render_template("notification.html", notifications=notifications)

@app.context_processor
def inject_notifications_count():
    try:
        notification_count = len(get_notifications()) 

    except Exception:
        notification_count = 0

    return {"notifications_count": notification_count}

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
    #loading categories from JSON
    try: 
        dataset = load_json(FILE_PATH)
        categories = sorted({product.get("category") for product in dataset.values() if product.get("category")})
    except FileNotFoundError:
        categories = [] #if file is missing, to not throw an error

    if request.method == "GET":
        
        return render_template("apply_discount.html", categories=categories)

    else:
        discount_input = request.form.get("discount_percentage", "").strip()
        category = request.form.get("category", "").strip() or None
        try:
            if not discount_input:
                raise ValueError("You must enter a discount percentage")
            discount_percentage = float(discount_input) #needed to allow decimals
            message = apply_discount_to_products(discount_percentage, category)
            flash(message, "success")
     
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
        name = request.form['name']
        access_level = request.form['access_level'] 
        password = request.form['password']
        repeat_password = request.form['repeat_password']

        success, result = create_account(username, name, access_level, password, repeat_password)

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
    users = load_json(USERS_FILE_PATH)
    username = current_user.id
    name = users[username]["name"]
    access_level = users[username]["access_level"]

    if request.method == "GET":
        return render_template("my_account.html", 
                            username=username,
                            name=name,
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
    
@app.route('/dashboard/users', methods=['GET'])
def users_page():
    #Reads all existing users
    users = load_json(USERS_FILE_PATH)

    return render_template("users.html", users=users)

@app.route('/dashboard/users/edit-user', methods=['GET', 'POST'])
def edit_user():
    users = load_json(USERS_FILE_PATH)

    #Render existing user information
    if request.method == "POST":
        original_username = request.form['original_username']
        new_username = request.form['username']
        user = users[original_username]

        if not user:
            flash("User not found", "error")
            return redirect(url_for("users_page"))

        #new user info if changes made
        new_user_info = {
            "password": request.form['password'],
            "name": request.form['name'],
            "access_level": request.form['access_level'],   
        }

        if original_username != new_username:
            #checking for duplicates
            if new_username in users:
                flash("Username already exists", "error")

            #pop user since username is dictionary key
            else:
                users.pop(original_username)
                users[new_username] = new_user_info

        #only chaning info if username does not change
        else:
            users[original_username] = new_user_info


        with open(USERS_FILE_PATH, 'w') as f:
            json.dump(users, f, indent=2)

        return redirect(url_for("users_page"))

    #GET request
    username = request.args.get('username')
    user = users.get(username)


    return render_template("edit_user.html", username=username, user=user)


@app.route('/dashboard/orders', methods=['GET'])
def list_orders_page():
    orders = load_json(ORDER_FILE_PATH)
    return render_template('list_orders.html', orders=orders)

@app.route('/dashboard/access-order', methods=['GET', 'POST'])
def access_order_page():
    orders = load_json(ORDER_FILE_PATH)
    
    order_number = request.args['order_number']
    order = orders.get(order_number)

    if request.method == 'GET':
        return render_template('access_order.html', order=order)
    
    else:
        status = request.form["status"]
        result = access_order(status, order_number)

        if result:
            flash(result, "success")

        return redirect(url_for('access_order_page', order_number=order_number))
    
@app.route('/dashboard/add-order', methods=['GET', 'POST'])
def add_order_page():
    
    if request.method == 'GET':
       fields = [{"article_id": "", "qty": ""}]
       return render_template('add_order.html', fields=fields)
    
    else:
        
        fields = []
        action = request.form["action"]
        article_ids = request.form.getlist("article_id")
        quantitys = request.form.getlist("quantity")

        for id, qty in zip(article_ids, quantitys):
            fields.append({"article_id": id, "qty": qty})
         
        if action == "add_field":
            fields.append({"article_id": "", "qty": ""})
            return render_template('add_order.html', fields=fields)

        else:
            username = current_user.id
            date = datetime.today().strftime("%d/%m/%Y")

            success, result = add_order(fields, username, date)

            if success:
                flash(result, "success")
        
            else:
                for error in result:
                    flash(error, "error")
            
            return redirect(url_for('add_order_page'))

@app.route('/dashboard/returns', methods=['GET'])
@login_required
def returns_page():
    try:
        returns = load_json(RETURNS_FILE_PATH)
    except Exception:
        flash("Error loading returns.", "error")
        returns = {}

    # Adds dictionary items to a list 
    returns_list = []
    if type(returns) == dict:
        for key, value in returns.items():
            returns_list.append((key, value))

    return render_template("returns.html", returns=returns_list)

@app.route('/dashboard/returns/info', methods=['GET', 'POST'])
def access_return_info():
    return_id = request.args.get('return_id', '').strip()
    if request.method == "POST":
            # This part gets called when the user presses a button
            status = request.form.get('status')
            access_return(status, return_id)
    returns = load_json(RETURNS_FILE_PATH)
        
    def build_return_display(item, return_id):
        return [
            ('Return ID', return_id),
            ('Article ID', item.get('article_id', '')),
            ('Amount', f"{item.get('stock_amount', '')} pcs"),
            ('Customer', item.get('customer', '')),
            ('Returned on', item.get('date', '')),
        ]
    
    # Matches return ID
    if return_id in returns:
        item = returns[return_id]
        return_display = build_return_display(item, return_id)
            
        return render_template("access_return_info.html", 
                                return_display=return_display, 
                                return_id=return_id, 
                                return_data=returns[return_id])
        
    # If we get here something has gone wrong...
    flash(f'No products found for: {return_id}', 'error')
    return render_template("access_return_info.html")

@app.route('/dashboard/returns/delete_return', methods=['GET'])
def delete_return_page():
    if request.method == "GET":
        return_id = request.args.get('return_id')
        deleted_return = delete_return(return_id)
        flash (f"Return with return id {return_id} has been deleted", "success")
        return redirect(url_for("returns_page"))
    
@app.route('/dashboard/returns/add_return_to_stock', methods=['GET'])
def add_return_to_stock_page():
    return_id = request.args.get('return_id')
    
    if return_id:
        flash(f"Return with return id {return_id} has been added back to stock", "success")
        add_return_to_stock(return_id)
    else:
        flash("Invalid return ID", "error")

    return redirect(url_for("returns_page"))

@app.route('/dashboard/add-return', methods=['GET', 'POST'])
def add_return_page():
    if request.method == "GET":
        return render_template("add_return.html")
    else:
        article_id = request.form["article_id"]
        stock = request.form["stock"]
        customer = request.form["customer"]
        
        # Values that don't need to be added when creating new return
        date = datetime.today().strftime("%d/%m/%y")
        
        success, result = add_return(article_id, int(stock), customer, date)

        if success:
            flash(result, "success")
        else:
            for error in result:
                flash(error, "error")
        
        return render_template("add_return.html")
    
#Route for user orders and delivery tracking
@app.route('/dashboard/user-orders', methods=['GET', 'POST'])
def user_orders_page():
    orders = load_orders()

    order_number = request.args.get('order_number')
    order = orders.get(order_number) if order_number else None

    if request.method == 'GET':
        # Show grouped orders in 3 tables
        grouped_orders = get_orders_grouped()
        return render_template(
            'user_orders.html',
            grouped_orders=grouped_orders,
            order=order
        )

    else:
        status = request.form["status"]
        result = update_order_status(order_number, status)

        if result:
            flash(f"Order {order_number} updated to {status}", "success")
        else:
            flash("Order not found", "error")

        return redirect(url_for('user_orders_page', order_number=order_number))

if __name__=='__main__':
    app.run(debug=True)
