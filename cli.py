import requests

BASE_URL = "http://127.0.0.1:5000"


def show_menu():
    print("\n===== INVENTORY CLI =====")
    print("1. View all items")
    print("2. View one item")
    print("3. Add item")
    print("4. Update item")
    print("5. Delete item")
    print("6. Search product (barcode)")
    print("0. Exit")


def get_all_items():
    response = requests.get(f"{BASE_URL}/items")
    print(response.json())


def get_one_item():
    item_id = input("Enter item ID: ")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    print(response.json())


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


def delete_item():
    item_id = input("Enter item ID to delete: ")
    response = requests.delete(f"{BASE_URL}/items/{item_id}")
    print(response.json())


def search_product():
    barcode = input("Enter barcode: ")
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


def main():
    while True:
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


if __name__ == "__main__":
    main()