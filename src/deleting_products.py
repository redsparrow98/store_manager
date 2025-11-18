from reader import write_json, load_json
from list_all_products import list_all_products

def delete_products():
    
    data = load_json("dataset/products.json")
    
    # List of all products to choose from
    list_all_products()

    delete_product = input("Input the article id of the product you want to delete. ")
    
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
    