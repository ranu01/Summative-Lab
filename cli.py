# Import the HTTP library used to call the Flask backend.
import requests

# Base URL for the local API server.
BASE_URL = "http://127.0.0.1:5000"

# Show the menu choices for the user.
def show_menu():
    print("\n===== INVENTORY CLI =====")
    print("1. View all items")
    print("2. View one item")
    print("3. Add item")
    print("4. Update item")
    print("5. Delete item")
    print("6. Search product (name/barcode)")
    print("0. Exit")

# Get all inventory records from the API.
def get_all_items():
    response = requests.get(f"{BASE_URL}/items")
    print(response.json())

# Get a single item by ID.
def get_one_item():
    item_id = input("Enter item ID: ")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    print(response.json())

# Add a new item to the system.
def add_item():
    item = {
        "id": int(input("ID: ")),
        "name": input("Name: "),
        "barcode": input("Barcode: "),
        "quantity": int(input("Quantity: ")),
        "price": float(input("Price: "))
    }

    response = requests.post(f"{BASE_URL}/items", json=item)
    print(response.json())

# Update an item using partial field values.
def update_item():
    item_id = input("Enter item ID to update: ")

    print("Leave blank if you don't want to change a field")

    data = {}

    name = input("New name: ")
    if name:
        data["name"] = name

    barcode = input("New barcode: ")
    if barcode:
        data["barcode"] = barcode

    quantity = input("New quantity: ")
    if quantity:
        data["quantity"] = int(quantity)

    price = input("New price: ")
    if price:
        data["price"] = float(price)

    response = requests.patch(
        f"{BASE_URL}/items/{item_id}",
        json=data
    )

    print(response.json())

# Delete an item by ID.
def delete_item():
    item_id = input("Enter item ID to delete: ")
    response = requests.delete(f"{BASE_URL}/items/{item_id}")
    print(response.json())

# Search products by name or barcode and optionally import one of the matches.
def search_product():
    product_name = input("Enter product name or barcode: ").strip()
    if not product_name:
        print("Product name or barcode cannot be blank.")
        return

    params = {"barcode": product_name} if product_name.isdigit() else {"name": product_name}
    response = requests.get(
        f"{BASE_URL}/search",
        params=params
    )
    if response.status_code != 200:
        print(response.json())
        return

    products = response.json().get("products", [])
    if not products:
        print("No matching products found.")
        return

    warning = response.json().get("warning")
    if warning:
        print(warning)

    print("\n--- Matching Products ---")
    for index, product in enumerate(products, start=1):
        print(
            f"{index}. {product.get('name')} | "
            f"Brand: {product.get('brand')} | "
            f"Category: {product.get('category')} | "
            f"Barcode: {product.get('barcode')}"
        )

    if all(product.get("in_inventory") for product in products):
        print("These matching items are already in your inventory.")
        return

    selection = input("Choose a product number to import (0 to cancel): ").strip()
    if selection == "0":
        print("Import sequence aborted.")
        return
    if not selection.isdigit() or not 1 <= int(selection) <= len(products):
        print("Invalid product selection.")
        return

    product_info = products[int(selection) - 1]
    barcode = product_info["barcode"]

    import_choice = input("\nWould you like to import this item to the database? (y/n): ").strip().lower()
    if import_choice == 'y':
        import_response = requests.post(f"{BASE_URL}/search/{barcode}/import")
        print(import_response.json())
    else:
        print("Import sequence aborted.")

# Main loop for menu-based interaction.
def main():
    while True:
        try:
            show_menu()
            choice = input("Choose an option: ")

            if choice == "1":
                get_all_items()
            elif choice == "2":
                get_one_item()
            elif choice == "3":
                add_item()
            elif choice == "4":
                update_item()
            elif choice == "5":
                delete_item()
            elif choice == "6":
                search_product()
            elif choice == "0":
                print("Exiting CLI...")
                break
            else:
                print("Invalid choice. Try again.")
        except requests.exceptions.ConnectionError:
            print("Error: Inventory API is not running. Start it with 'python app.py' in another terminal.")
        except KeyboardInterrupt:
            print("\nExiting CLI...")
            break


if __name__ == "__main__":
    main()