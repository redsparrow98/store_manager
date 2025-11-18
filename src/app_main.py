from flask import Flask, render_template, redirect, url_for, request, flash
from list_all_products import *

app = Flask(__name__)

@app.route('/')
def display_dashboard():
    return render_template('dashboard.html')

@app.route('/inventory')
def display_inventory():
    return render_template('inventory.html')

@app.route('/inventory/all-products')
def display_all_products():
    all_products = list_all_products()
    return render_template('all_products.html', all_products = all_products)


if __name__=='__main__':
    app.run(debug=True)
