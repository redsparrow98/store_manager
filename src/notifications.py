from reader import *
from pathlib import Path
from datetime import datetime

#Paths
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / "dataset" / "products.json"

notifications = {}
low_article_ids = []

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

# Add notification if one doesn't exist
def add_notification(article_id: str, message: str):

    # when user manually clears this notification, it skips adding
    if article_id in cleared_notifications:
        return len(notifications)

    # Check for existing notification
    if article_id in notifications:
        return len(notifications) # Amount of notifications

    # Add new notification if there's no existing one
    notifications[article_id] = {
        "id": article_id,
        "message": message,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    return len(notifications) # Amount of notifications

def get_threshold(category: str) -> int:
    return CATEGORY_THRESHOLDS.get(category.lower(), DEFAULT_THRESHOLD)


def scan_low_stock():
    low_article_ids.clear()

    try:
        products = load_json(FILE_PATH)
    except Exception as e:
        print("Error loading products:", e)
        return

    for article_id, info in products.items():
        product_name = info.get("article_name", "Unnamed Product")
        stock = int(info.get("stock_amount", 0))
        category = info.get("category", "")
        threshold = get_threshold(category)

        if stock <= threshold:
            low_article_ids.append(article_id)
            message = f"{product_name} (ID {article_id}) is low: {stock} left"
            add_notification(article_id, message)

    # Remove notifications for products that no longer are low in stock
    for article_id in list(notifications.keys()):
        if article_id not in low_article_ids:
            notifications.pop(article_id)
            cleared_notifications.discard(article_id)  # allow future notifications

def get_notifications():
    """
    Return the current notifications list.
    This is what Flask will call to pass notifications to templates.
    """
    return list(notifications.values())

cleared_notifications = set() #Track cleared notifications so they don't reappear immediately 
def clear_notifications():
    """
    Clear all notifications at once.
    Called when the user clicks 'Clear all notifications'.
    """
    global notification, clear_notifications
    cleared_notifications.update(notifications.keys())
    notifications.clear()
