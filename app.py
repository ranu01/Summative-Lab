# Import Flask so the app can serve JSON routes.
from flask import Flask, jsonify, request
# Import requests so the app can call the Open Food Facts API.
import requests

# Create the Flask app instance.
app = Flask(__name__)

# Define the inventory manager class.
class Inventory:
    # Explain what this class does.
    """Handles CRUD operations in memory to isolate data layers."""
    # Initialize the list of inventory items.
    def __init__(self):
        # Store items as dictionaries in a list.
        self.items = [
            {
                # Product ID.
                "id": 1,
                # Product name.
                "name": "Milk",
                # Barcode used for search/import.
                "barcode": "737628064502",
                # Current stock count.
                "quantity": 10,
                # Product price.
                "price": 120.0
            }
        ]

    # Return all stored items.
    def get_all_items(self):
        return self.items

    # Get one item using its ID.
    def get_item(self, item_id):
        # Loop through each item.
        for item in self.items:
            # If IDs match, return the item.
            if int(item["id"]) == int(item_id):
                return item
        # No item found.
        return None

    # Add a new inventory item.
    def add_item(self, item):
        # Check for duplicate IDs.
        for existing in self.items:
            if int(existing["id"]) == int(item["id"]):
                return {"error": "Item ID already exists"}
        
        # Normalize values before storing to keep data consistent.
        typed_item = {
            "id": int(item["id"]),
            "name": str(item["name"]),
            "barcode": str(item["barcode"]),
            "quantity": int(item["quantity"]),
            "price": float(item["price"])
        }
        # Save the new item.
        self.items.append(typed_item)
        return typed_item

    # Update an item with partial incoming data.
    def update_item(self, item_id, data):
        # Search the item by ID.
        for item in self.items:
            if int(item["id"]) == int(item_id):
                # Update only provided fields.
                if "name" in data: item["name"] = str(data["name"])
                if "barcode" in data: item["barcode"] = str(data["barcode"])
                if "quantity" in data: item["quantity"] = int(data["quantity"])
                if "price" in data: item["price"] = float(data["price"])
                return item
        return None

    # Delete one matching item.
    def delete_item(self, item_id):
        # Search the list.
        for item in self.items:
            if int(item["id"]) == int(item_id):
                self.items.remove(item)
                return True
        return False

# Create a global database object for the app.
# This allows the Flask routes to access the inventory manager.(creates shared in-memory inventory)
db = Inventory()

# Attach database to app for testing access.(exposes that obect to the app can be conivinent for testing )
# This is useful for unit tests to reset or inspect the inventory.
app.inventory = db

# Root route showing API description.
# Return all items in the inventory as JSON.
@app.route("/")
def home():
    return jsonify({
        "message": "Inventory Management REST API",
        "endpoints": [
            "GET /items",
            "GET /items/<id>",
            "POST /items",
            "PATCH /items/<id>",
            "DELETE /items/<id>",
            "GET /search?name=<product name>",
            "POST /search/<barcode>/import"
        ]
    })


# Get all items.
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(db.get_all_items()), 200

# Get one item by ID.
@app.route("/items/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    item = db.get_item(item_id)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

# Create a new item.
@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json() or {}
    required_fields = ["id", "name", "barcode", "quantity", "price"]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    result = db.add_item(data)
    if "error" in result:
        return jsonify(result), 400
        
    return jsonify({"message": "Item added successfully", "item": result}), 201

# Update an item by ID.
@app.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json() or {}
    updated_item = db.update_item(item_id, data)
    if updated_item:
        return jsonify({"message": "Item updated", "item": updated_item}), 200
    return jsonify({"error": "Item not found"}), 404

# Delete an item by ID.
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if db.delete_item(item_id):
        return jsonify({"message": "Item deleted successfully"}), 200
    return jsonify({"error": "Item not found"}), 404

# Find local inventory items matching a product name.
def search_local_inventory(product_name):
    query = product_name.casefold()
    return [
        {
            "barcode": str(item["barcode"]),
            "name": item["name"],
            "brand": "In your inventory",
            "category": "Local inventory",
            "in_inventory": True
        }
        for item in db.get_all_items()
        if query in str(item["name"]).casefold()
    ]

# Search for products by name or barcode in the external catalog.
@app.route("/search", methods=["GET"])
def search_product():
    barcode = request.args.get("barcode", "").strip()
    product_name = request.args.get("name", "").strip()

    if barcode:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        headers = {"User-Agent": "StudentInventoryLab/1.0 (Flask REST API School Project)"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                local_products = search_local_inventory(barcode)
                if local_products:
                    return jsonify({
                        "products": local_products,
                        "warning": "External catalog unavailable; showing local inventory matches."
                    }), 200
                return jsonify({
                    "error": "OpenFoodFacts barcode lookup failed",
                    "upstream_status": response.status_code
                }), 502

            product_payload = response.json()
            if product_payload.get("status") == 0:
                return jsonify({"error": "No matching product found"}), 404

            product = product_payload.get("product", {})
            products = [{
                "barcode": str(product.get("code") or barcode),
                "name": product.get("product_name") or "Unknown Product",
                "brand": product.get("brands") or "Generic Brand",
                "category": product.get("categories") or "Uncategorized"
            }]
            return jsonify({"products": products}), 200
        except (requests.exceptions.RequestException, ValueError):
            local_products = search_local_inventory(barcode)
            if local_products:
                return jsonify({
                    "products": local_products,
                    "warning": "External catalog unavailable; showing local inventory matches."
                }), 200
            return jsonify({"error": "Network pipeline error"}), 500

    if not product_name:
        return jsonify({"error": "Product name or barcode is required"}), 400
    
# Use the Open Food Facts API to search for products by name.
    url = "https://world.openfoodfacts.org/api/v2/search"

    # Identify the application to the external API.
    headers = {"User-Agent": "StudentInventoryLab/1.0 (Flask REST API School Project)"}
    
    try:
        # Ask Open Food Facts for a small set of name matches.
        response = requests.get(
            url,
            params={
                "search_terms": product_name,
                "fields": "code,product_name,brands,categories",
                "page_size": 10
            },
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            local_products = search_local_inventory(product_name)
            if local_products:
                return jsonify({
                    "products": local_products,
                    "warning": "External catalog unavailable; showing local inventory matches."
                }), 200
            return jsonify({
                "error": "OpenFoodFacts search failed",
                "upstream_status": response.status_code
            }), 502

        catalog_products = response.json().get("products", [])
        products = [
            {
                "barcode": str(product["code"]),
                "name": product.get("product_name") or "Unknown Product",
                "brand": product.get("brands") or "Generic Brand",
                "category": product.get("categories") or "Uncategorized"
            }
            for product in catalog_products
            if product.get("code")
        ]
        if not products:
            return jsonify({"error": "No matching products found"}), 404

        return jsonify({"products": products}), 200
    except (requests.exceptions.RequestException, ValueError):
        local_products = search_local_inventory(product_name)
        if local_products:
            return jsonify({
                "products": local_products,
                "warning": "External catalog unavailable; showing local inventory matches."
            }), 200
        return jsonify({"error": "Network pipeline error"}), 500

# Import a product from the remote API and save it into local inventory.
@app.route("/search/<barcode>/import", methods=["POST"])
def import_product(barcode):
    # Reject duplicate barcode imports.
    if any(str(item["barcode"]) == str(barcode) for item in db.get_all_items()):
        return jsonify({"error": "Product with this barcode already exists in inventory"}), 400

#Build the URL to fetch product details from Open Food Facts using the barcode.
# It uses barcode to lookup for a specific product in the Open Food Facts database.

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {"User-Agent": "StudentInventoryLab/1.0 (Flask REST API School Project)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        product = response.json()
        if response.status_code != 200 or product.get("status") == 0:
            return jsonify({"error": "Product not found on remote server catalog"}), 404

#create the next inventory ID and builds a new item if the product is found, then adds it to the local inventory.
        product_data = product["product"]
        next_id = max([item["id"] for item in db.get_all_items()], default=0) + 1
        
        new_entry = {
            "id": next_id,
            "name": product_data.get("product_name", "Imported Product"),
            "barcode": str(barcode),
            "quantity": 1,
            "price": 9.99
        }
        db.add_item(new_entry)
        return jsonify({"message": "Successfully auto-saved to DB array!", "item": new_entry}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app when launched directly.
if __name__ == "__main__":
    app.run(debug=True, port=5000)