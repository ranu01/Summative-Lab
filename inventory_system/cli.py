import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def show_menu():
    print("\n===== INVENTORY MANAGEMENT CLI =====")
    print("1. View all items")
    print("2. View one item")
    print("3. Add item manually")
    print("4. Update item fields")
    print("5. Delete item tracking")
    print("6. Search & Import barcode (External API)")
    print("0. Exit")

def get_all_items():
    try:
        response = requests.get(f"{BASE_URL}/items")
        print("\n--- Current Inventory Array Matrix ---")
        print(response.json())
    except requests.exceptions.ConnectionError:
        print("Error: Backend Flask application is not running.")

def get_one_item():
    item_id = input("Enter item ID: ")
    try:
        response = requests.get(f"{BASE_URL}/items/{item_id}")
        print(response.json())
    except requests.exceptions.ConnectionError:
        print("Error: Backend Flask application is not running.")

def add_item():
    try:
        item = {
            "id": int(input("ID: ")),
            "name": input("Name: "),
            "barcode": input("Barcode: "),
            "quantity": int(input("Quantity: ")),
            "price": float(input("Price: "))
        }
        response = requests.post(f"{BASE_URL}/items", json=item)
        print(response.json())
    except ValueError:
        print("Invalid data format input. Numbers required for ID, Quantity, and Price.")
    except requests.exceptions.ConnectionError:
        print("Error: Backend Flask application is not running.")

def update_item():
    item_id = input("Enter item ID to update: ")
    print("Leave blank if you don't want to change a field")

    data = {}
    name = input("New name: ")
    if name: data["name"] = name

    barcode = input("New barcode: ")
    if barcode: data["barcode"] = barcode

    quantity = input("New quantity: ")
    if quantity: data["quantity"] = int(quantity)

    price = input("New price: ")
    if price: data["price"] = float(price)

    try:
        response = requests.patch(f"{BASE_URL}/items/{item_id}", json=data)
        print(response.json())
    except requests.exceptions.ConnectionError:
        print("Error: Backend Flask application is not running.")

def delete_item():
    item_id = input("Enter item ID to delete: ")
    try:
        response = requests.delete(f"{BASE_URL}/items/{item_id}")
        print(response.json())
    except requests.exceptions.ConnectionError:
        print("Error: Backend Flask application is not running.")

def search_product():
    barcode = input("Enter barcode to lookup: ")
    try:
        response = requests.get(f"{BASE_URL}/search/{barcode}")
        if response.status_code != 200:
            print(response.json())
            return

        product_info = response.json()
        print("\n--- External Product Meta Located ---")
        print(f"Barcode: {product_info.get('barcode')}")
        print(f"Name:    {product_info.get('name')}")
        print(f"Brand:   {product_info.get('brand')}")
        print(f"Catalog: {product_info.get('category')}")
        
        import_choice = input("\nWould you like to import this item to the database? (y/n): ").strip().lower()
        if import_choice == 'y':
            import_response = requests.post(f"{BASE_URL}/search/{barcode}/import")
            print(import_response.json())
        else:
            print("Import sequence aborted.")
    except requests.exceptions.ConnectionError:
        print("Error: Backend Flask application is not running.")

def main():
    while True:
        show_menu()
        choice = input("Choose an option: ")
        if choice == "1": get_all_items()
        elif choice == "2": get_one_item()
        elif choice == "3": add_item()
        elif choice == "4": update_item()
        elif choice == "5": delete_item()
        elif choice == "6": search_product()
        elif choice == "0":
            print("Exiting CLI...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
