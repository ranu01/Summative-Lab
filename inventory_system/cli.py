# Import the requests library so the CLI can communicate with the Flask API.
import requests
# Import the sys library in case the program needs to interact with Python runtime features.
import sys

# Store the local API URL used for all requests.
BASE_URL = "http://127.0.0.1:5000"

# Define the menu function that prints all available options.
def show_menu():
    # Print the main menu header.
    print("\n===== INVENTORY MANAGEMENT CLI =====")
    # Show option 1 for listing all items.
    print("1. View all items")
    # Show option 2 for viewing a single item.
    print("2. View one item")
    # Show option 3 for adding a product manually.
    print("3. Add item manually")
    # Show option 4 for changing item fields.
    print("4. Update item fields")
    # Show option 5 for deleting an item record.
    print("5. Delete item tracking")
    # Show option 6 for searching products by name.
    print("6. Search product by name (External API)")
    # Show option 0 for exiting the menu.
    print("0. Exit")

# Fetch every item from the backend and print the result.
def get_all_items():
    # Wrap the API call in try/except to catch connection problems.
    try:
        # Send a GET request to list all items.
        response = requests.get(f"{BASE_URL}/items")
        # Print a heading before showing the current data.
        print("\n--- Current Inventory Array Matrix ---")
        # Print the JSON returned by the server.
        print(response.json())
    # If the backend is not running, show a helpful message.
    except requests.exceptions.ConnectionError:
        # Inform the user that the backend is offline.
        print("Error: Backend Flask application is not running.")

# Fetch one item by ID and print the server response.
def get_one_item():
    # Ask for the ID of the item to view.
    item_id = input("Enter item ID: ")
    # Try to contact the API.
    try:
        # Send the GET request for one item.
        response = requests.get(f"{BASE_URL}/items/{item_id}")
        # Print the response JSON.
        print(response.json())
    # Handle backend offline errors.
    except requests.exceptions.ConnectionError:
        # Explain that the backend service is not running.
        print("Error: Backend Flask application is not running.")

# Collect a new item entry from the user and send it to the backend.
def add_item():
    # Use try/except to validate user input and network access.
    try:
        # Build the product dictionary from user input.
        item = {
            # Convert the ID to an integer.
            "id": int(input("ID: ")),
            # Read the product name.
            "name": input("Name: "),
            # Read the barcode string.
            "barcode": input("Barcode: "),
            # Convert the quantity to an integer.
            "quantity": int(input("Quantity: ")),
            # Convert the price to a float.
            "price": float(input("Price: "))
        }
        # Send the item via POST to create it in the backend.
        response = requests.post(f"{BASE_URL}/items", json=item)
        # Print the response from the server.
        print(response.json())
    # Catch invalid numeric values.
    except ValueError:
        # Tell the user that numeric fields require whole numbers or floats.
        print("Invalid data format input. Numbers required for ID, Quantity, and Price.")
    # Catch offline backend errors.
    except requests.exceptions.ConnectionError:
        # Explain the backend is not available.
        print("Error: Backend Flask application is not running.")

# Ask for updated fields and send them as a partial patch request.
def update_item():
    # Ask which item to update.
    item_id = input("Enter item ID to update: ")
    # Tell the user that leaving fields blank keeps them unchanged.
    print("Leave blank if you don't want to change a field")

    # Create an empty data dictionary for modifications.
    data = {}
    # Ask for a new name and save it only if provided.
    name = input("New name: ")
    if name: data["name"] = name

    # Ask for a new barcode and save it only if provided.
    barcode = input("New barcode: ")
    if barcode: data["barcode"] = barcode

    # Ask for a new quantity and convert it to int if provided.
    quantity = input("New quantity: ")
    if quantity: data["quantity"] = int(quantity)

    # Ask for a new price and convert it to float if provided.
    price = input("New price: ")
    if price: data["price"] = float(price)

    # Try to send the patch request to the backend.
    try:
        # Send the update payload to the item route.
        response = requests.patch(f"{BASE_URL}/items/{item_id}", json=data)
        # Print the JSON response from the server.
        print(response.json())
    # If the backend is offline, show an error.
    except requests.exceptions.ConnectionError:
        # Inform the user that the backend is not running.
        print("Error: Backend Flask application is not running.")

# Delete an item from the inventory by ID.
def delete_item():
    # Ask for the item ID to remove.
    item_id = input("Enter item ID to delete: ")
    # Try to contact the backend.
    try:
        # Send a DELETE request for the specified item.
        response = requests.delete(f"{BASE_URL}/items/{item_id}")
        # Print the API's response.
        print(response.json())
    # Handle backend connectivity issues.
    except requests.exceptions.ConnectionError:
        # Explain that the backend application is not available.
        print("Error: Backend Flask application is not running.")

# Search products by name and optionally import one of the matches.
def search_product():
    # Ask the user for the product name or barcode to search.
    product_name = input("Enter product name or barcode: ").strip()
    if not product_name:
        print("Product name or barcode cannot be blank.")
        return

    # Try to contact the backend search endpoint.
    try:
        # If the input is numeric, treat it as a barcode lookup.
        params = {"barcode": product_name} if product_name.isdigit() else {"name": product_name}
        response = requests.get(
            f"{BASE_URL}/search",
            params=params
        )
        # If the response is not successful, print the JSON error and stop.
        if response.status_code != 200:
            # Show the server error payload.
            print(response.json())
            # Return early so the function ends.
            return

        # Parse and display the matching products.
        products = response.json().get("products", [])
        if not products:
            print("No matching products found.")
            return

        print("\n--- Matching Products ---")
        for index, product in enumerate(products, start=1):
            print(
                f"{index}. {product.get('name')} | "
                f"Brand: {product.get('brand')} | "
                f"Category: {product.get('category')} | "
                f"Barcode: {product.get('barcode')}"
            )

        selection = input("Choose a product number to import (0 to cancel): ").strip()
        if selection == "0":
            print("Import sequence aborted.")
            return
        if not selection.isdigit() or not 1 <= int(selection) <= len(products):
            print("Invalid product selection.")
            return

        barcode = products[int(selection) - 1]["barcode"]
        # Ask the user if they want to import the item into the inventory.
        import_choice = input("\nWould you like to import this item to the database? (y/n): ").strip().lower()
        # If the user chooses yes, send the import request.
        if import_choice == 'y':
            # Post the import request to the backend.
            import_response = requests.post(f"{BASE_URL}/search/{barcode}/import")
            # Print the server response for the import action.
            print(import_response.json())
        # Otherwise, explain that no import happened.
        else:
            # Tell the user the import was canceled.
            print("Import sequence aborted.")
    # Catch a connection problem to the backend.
    except requests.exceptions.ConnectionError:
        # Explain the backend is not running.
        print("Error: Backend Flask application is not running.")

# Keep the CLI alive until the user chooses to exit.
def main():
    # Run an infinite loop for the menu system.
    while True:
        # Display the menu every time the loop repeats.
        show_menu()
        # Ask the user for the next action.
        choice = input("Choose an option: ")
        # If the user chooses option 1, show all items.
        if choice == "1": get_all_items()
        # Else if the user chooses option 2, show one item.
        elif choice == "2": get_one_item()
        # Else if the user chooses option 3, add an item.
        elif choice == "3": add_item()
        # Else if the user chooses option 4, update an item.
        elif choice == "4": update_item()
        # Else if the user chooses option 5, delete an item.
        elif choice == "5": delete_item()
        # Else if the user chooses option 6, search by barcode.
        elif choice == "6": search_product()
        # Else if the user chooses 0, exit the loop.
        elif choice == "0":
            # Print a closing message.
            print("Exiting CLI...")
            # Exit the while loop.
            break
        # If the input does not match any valid menu option, show an error.
        else:
            # Tell the user their choice was invalid.
            print("Invalid choice. Try again.")

# Run the CLI when this file is executed directly.
if __name__ == "__main__":
    # Start the command-line application.
    main()
