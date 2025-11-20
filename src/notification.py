import json
from pathlib import Path
from datetime import datetime

"""
1. Read products.json
2.Check stock
3. Create notifications when stock is low
"""

#Paths

BASE_DIR = Path(__file__).parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"

notifications = []

#Thresholds

CATEGORY_THRESHOLDS = {
    "phones": 5,
    "tablets": 5,
    "headphones": 3,
    "speakers": 5,
    "computers": 3,
    "smart watches": 5,
    "accessories": 3,
}
DEFAULT_THRESHOLD = 5

#functions for json

def load_products():
    if not FILE_PATH.exists():
        return{}
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
#add notification if doesnt exist
    
def add_notification(article_id: str, message: str):
    for n in notifications:
        if n ["id"] == article_id and n ["message"] == message:
            return
        notifications.append({
            "id": article_id,
            "message": message,
            "creat_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })

def get_threshold(category: str) -> int:
    return CATEGORY_THRESHOLDS.get(category.lower(), DEFAULT_THRESHOLD)

def scan_low_stock():
    products = load_products()
    for article_id, info in products.items():

        product_name = info.get("article_name", "Unnamed Product")
        stock = info.get("stock_amount", 0)
        category = info.get("category", "")

        threshold = get_threshold(category)
        
        if stock <= threshold:
            message = f"{product_name} (ID {article_id}) is low: {stock} left"
            add_notification(article_id, message)
    
