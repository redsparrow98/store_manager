from reader import write_json, load_json
from inventory_manager import list_all_products

def delete_products():
    
    data = load_json("dataset/products.json")
    
    for product in data:
        print(f"{product} - {data[product]["article_name"]}")
    
    delete_product = input("Input the article id of the product you want to delete: ")
    
    if delete_product in data:
        validation = input(f"Are you sure you want to delete \'{data[delete_product]["article_name"]}\'? (yes/no) ").lower()
        if validation != "yes":
            print("Deletion cancelled")
            return
        

        print(f"Product \'{data[delete_product]["article_name"]}\' succesfully deleted.")
        data.pop(delete_product)
        write_json("dataset/products.json", data)

    else:
        print("Product not found")
        return