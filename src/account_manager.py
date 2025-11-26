from reader import *
import os
from pathlib import Path
from flask import Flask, request, render_template, flash, redirect, url_for


app = Flask(__name__)
app.secret_key = "demo-key1234"

# this is to avoid the file path issues we had
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "users.json"

# Creates a new account if username not already taken
def create_account(username, access_level, password, repeat_password):
    users = load_json(FILE_PATH)
    
    errors = []

    if username in users:
        errors.append("Username already exists, please choose another username", "error")
    if not username.strip() == 0:
        errors.append("Username is required")
    if not password.strip() == 0:
        errors.append("Password is required")
    if repeat_password != password:
        errors.append("Repeated password doesn't match password")
    if not access_level.strip():
        errors.append("Access level is required.")

    if errors: 
        return False, errors
    
    else:
        users[username] = {
            "password": password,
            "access_level": access_level,
        }
        write_json(FILE_PATH, users)
        return True, "Account succesfully created."


# Deletes user if correct access level
def delete_user(deleted_user):
    users = load_json(FILE_PATH)
    
    users.pop(deleted_user)
    write_json(FILE_PATH, users)
    
    print(users)
    return True

# Flask that will go into main.py
@app.route('/dashboard/create-account', methods=['GET', 'POST'])
def create_account_page():
    
    if request.method == "GET":
        return render_template("create_account.html")
    
    else:
        username = request.form['username']
        access_level = request.form['access level'] 
        password = request.form['passsword']
        repeat_password = request.form['repeat_password']

        success, result = create_account(username, access_level, password, repeat_password)

        # User gets passed to the login and a success message gets flashed
        if success:
            flash (result, "success")
            
            return redirect(url_for("login_page"))
        else:
            for error in result:
                flash (error, "error")
            return redirect(url_for("create_account_page"))
        

# Checks if username and password are entered correctly
def check_credentials(username, password):
    users = load_json(FILE_PATH)
    
    if username in users and password == users[username]['password']:
        return True
    else:
        return False
    

# Checks if access level is manager or employee
def is_manager(username):
    users = load_json(FILE_PATH)
    
    if username in users and users[username]['access_level'] == "manager":
        return True
    else:
        return False



#This will go in main
@app.route('/dashboard/delete-user', methods=['GET','POST'])
def delete_user_page():
    if request.method == "GET":
        return render_template("delete_user.html")
    
    else:
        # Loads dataset with users data
        users = load_json('dataset/users.json')
        
        # Asks the user to put in their own username and password to check access level
        username = request.form['username']
        password = request.form['password']
        
        # Checks if credentials and acccess level is correct. 
        if check_credentials(username, password) == False or is_manager(username) == False:
            flash (f"Access denied. You don't have the access level to delete a user.", "error")
            return redirect(url_for("delete_user_page"))
        # If correct, asks user to input username for which user they want to delete
        deleted_user = request.form['deleted_user']
        
        if delete_user(deleted_user) == False:
            flash (f"User with username '{users[delete_user]}' not found.", "error")
            return redirect(url_for("delete_user_page"))
        
        flash (f"{users[delete_user]} with access level {[delete_user]['access_level']} has been deleted successfully.", "success")            
        return render_template("delete_user.html")
