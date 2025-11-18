from reader import load_json

def list_all_products():
    all_products =[]
    data = load_json('dataset/products.json')
    for id, info in data.items():
        article_id = id
        product = info['article_name']
        brand = info['brand']
        price = info['price_SEK']
        discount = info['discount_percentage']

        format = f"""art#{article_id}
-------
Name: {product}
Brand: {brand}
Standard price: {price}
Current discount: {discount}
Current price: {price - int(discount * 100)}"""
        
        all_products.append(format)
    return all_products
        
