from reader import write_json, load_json
from inventory_manager import list_all_products

def access_product():
    
    data = load_json("dataset/products.json")
    
    # List of all products to choose from
    list_all_products()

    accessed_product = input("Input the product id of the product you want to access. ")

    if accessed_product in data:
        print(f"Printing product information for {data[accessed_product]["article_name"]}:")
        
        for key in data[accessed_product]:
            print (f"{key}: {data[accessed_product][key]}")
            
    else:
        print("Product not found")
        return