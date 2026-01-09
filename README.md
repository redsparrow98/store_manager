# Store Manager

A web-based **inventory and store management system** built with **Flask** and **Jinja2**, designed to manage products, users, orders, returns, and notifications with role-based access control.

---

## Description

Store Manager is an internal management system for retail operations. It allows staff and managers to:

* Log in securely
* View and manage inventory
* Track user orders and returns
* Receive low-stock notifications
* Manage user accounts and access levels

The system distinguishes between **Manager** and regular user roles, ensuring that sensitive actions are restricted to authorized users only.

---

## Features

### Authentication & Accounts

* Login system with flash-based error handling
* My Account page with password update functionality
* Role-based access control (Manager / User)

### User Management (Manager only)

* Create new user accounts
* Edit and delete users
* View all registered users

### Inventory Management

* View all products
* Update product information
* Low-stock alerts via notifications

### Orders & Returns

* View user orders grouped by status
* Create and access orders (Manager only)
* Track and manage product returns

### Notifications

* Automatic low-stock alerts
* Clear all notifications

---

## Technologies Used

* **Backend:** Python, Flask
* **Frontend:** HTML5, Jinja2, CSS
* **Session & Flash Messaging:** Flask
* **Version Control:** Git, GitLab

---

## Project Structure (Simplified)

```
store_manager/
│
├── dataset/
│   ├── users.json
│   ├── products.json
│   ├── orders.json
│   ├── user_orders.json
│   ├── returns.json
│   └── stock_orders.json
│
├── src/
│   │
|   ├── static/
│   |    ├── css/
│   |    └── images/
|   |
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── my_account.html
│   │   ├── notifications.html
│   │   ├── returns.html
│   │   ├── update_product.html
│   │   ├── user_orders.html
│   │   └── users.html
│   │
│   ├── account_manager.py
│   ├── inventory_manager.py
│   ├── login.py
│   ├── main.py
│   ├── notifications.py         
│   └── reader.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Requirements

* Python 3.9+
* pip

### Steps

1. Clone the repository

   ```bash
   git clone https://git.chalmers.se/prosic/store_manager.git
   cd store_manager
   ```

2. Create and activate a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\\Scripts\\activate   # Windows
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application

   ```bash
   flask run
   ```

5. Open your browser and navigate to:

   ```
   http://127.0.0.1:5000
   ```

---

## Usage

### Login

* Users must log in using valid credentials
* Incorrect credentials trigger a danger flash message

### Roles

**Manager** can:

* Create, edit, and delete users
* Add and update products
* View and manage all orders and returns

**Regular users** can:

* View inventory
* View their own orders
* Update their own password

---

## Flash Messages & Feedback

The application uses Flask flash messages for:

* Login errors
* Successful updates
* Validation and permission errors

Messages are styled by category (success, error, danger).

---

## Security Notes

* Password fields are masked and never displayed
* Current password is required to update credentials
* Access control enforced at both route and template level

---

## Contributing

This project is intended for educational use. Contributions are welcome via merge requests.

Steps:

1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Open a merge request

---

## Authors

* Project Team – University of Gothenburg

Natalija Prošić 
gusprosna@student.gu.se
Developer

Vera Ek Lundqvist 
guseklunve@student.gu.se
Developer

Lovisa Olsson
gusolsloy@student.gu.se
Developer

Milica Mandic 
gusmanmii@student.gu.se
Developer (Scrum master)

Sophie Vervoort
gusvervso@student.gu.se
Developer (Product owner)

Saga Rennemo
gusrennesa@student.gu.se
Developer

Sayara Salsabil
gussalssa@student.gu.se
Developer




---

## License

This project is for academic use. Licensing can be defined if the project is extended or released publicly.

---

## Project Status

✔ Core functionality implemented
✔ Role-based access working
🔧 Further improvements possible (testing, database integration, UI enhancements)
