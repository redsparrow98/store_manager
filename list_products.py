import json

def load_json(file_name):
    with open (file_name) as file:
        data = json.load(file)
    
    for id, info in data.items():
        article_id = id
        product = info["article_name"]
        brand = info["brand"]
        price = info["price_SEK"]
        discount = info["discount_percentage"]
        stock = info["stock_amount"]

        print(f"""{article_id}
-------
Name: {product}
Brand: {brand}
Price: {price}
Current discount: {int((discount) * 100)}%""")
        if discount != 0.0:
            print(f"Current price: {price - (price * discount)}")
        print(f"Current stock value: {stock}\n")
        


load_json("dataset/products.json")