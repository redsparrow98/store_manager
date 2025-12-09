from reader import *
from pathlib import Path
from datetime import datetime

#Paths

BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"

notifications = []

#Thresholds

CATEGORY_THRESHOLDS = {
    "phones": 3,
    "tablets": 3,
    "headphones": 3,
    "speakers": 3,
    "computers": 3,
    "smart watches": 3,
    "accessories": 3,
}
DEFAULT_THRESHOLD = 3


#add notification if doesn't exist
def add_notification(article_id: str, message: str):
#check for existing notification
    for n in notifications:
        if n["id"] == article_id and n["message"] == message:
            return

#add new notification
    notifications.append({
        "id": article_id,
        "message": message,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    })



def get_threshold(category: str) -> int:
    return CATEGORY_THRESHOLDS.get(category.lower(), DEFAULT_THRESHOLD)


def scan_low_stock():
    products = load_json(FILE_PATH)

    for article_id, info in products.items():
        product_name = info.get("article_name", "Unnamed Product")
        stock = int(info.get("stock_amount", 0))
        category = info.get("category", "")
        threshold = get_threshold(category)

        if stock <= threshold:
            message = f"{product_name} (ID {article_id}) is low: {stock} left"
            add_notification(article_id, message)

def get_notifications():
    """
    Return the current notifications list.
    This is what Flask will call to pass notifications to templates.
    """
    return notifications
    
