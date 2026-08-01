from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# ========================================================
# BUSINESS LOGIC LAYER: INVENTORY STATE MANAGER
# ========================================================
class Inventory:
    """Handles CRUD operations in memory to isolate data layers."""
    def __init__(self):
        self.items = [
            {
                "id": 1,
                "name": "Milk",
                "barcode": "737628064502",
                "quantity": 10,
                "price": 120.0
            }
        ]

    def get_all_items(self):
        return self.items

    def get_item(self, item_id):
        for item in self.items:
            if int(item["id"]) == int(item_id):
                return item
        return None

    def add_item(self, item):
        for existing in self.items:
            if int(existing["id"]) == int(item["id"]):
                return {"error": "Item ID already exists"}
        
        typed_item = {
            "id": int(item["id"]),
            "name": str(item["name"]),
            "barcode": str(item["barcode"]),
            "quantity": int(item["quantity"]),
            "price": float(item["price"])
        }
        self.items.append(typed_item)
        return typed_item

    def update_item(self, item_id, data):
        for item in self.items:
            if int(item["id"]) == int(item_id):
                if "name" in data: item["name"] = str(data["name"])
                if "barcode" in data: item["barcode"] = str(data["barcode"])
                if "quantity" in data: item["quantity"] = int(data["quantity"])
                if "price" in data: item["price"] = float(data["price"])
                return item
        return None

    def delete_item(self, item_id):
        for item in self.items:
            if int(item["id"]) == int(item_id):
                self.items.remove(item)
                return True
        return False

# Instantiate our class data container globally & attach to app for testing
db = Inventory()
app.inventory = db

# ========================================================
# TRANSPORT ROUTING LAYER: FLASK ENDPOINTS
# ========================================================
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
            "GET /search/<barcode>",
            "POST /search/<barcode>/import"
        ]
    })

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(db.get_all_items()), 200

@app.route("/items/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    item = db.get_item(item_id)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

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

@app.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json() or {}
    updated_item = db.update_item(item_id, data)
    if updated_item:
        return jsonify({"message": "Item updated", "item": updated_item}), 200
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if db.delete_item(item_id):
        return jsonify({"message": "Item deleted successfully"}), 200
    return jsonify({"error": "Item not found"}), 404

@app.route("/search/<barcode>", methods=["GET"])
def search_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {"User-Agent": "StudentInventoryLab/1.0 (Flask REST API School Project)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return jsonify({"error": "Unable to contact OpenFoodFacts"}), 500
        
        product = response.json()
        if product.get("status") == 0:
            return jsonify({"error": "Product not found"}), 404

        product_data = product["product"]
        return jsonify({
            "barcode": barcode,
            "name": product_data.get("product_name", "Unknown Product"),
            "brand": product_data.get("brands", "Generic Brand"),
            "category": product_data.get("categories", "Uncategorized")
        }), 200
    except requests.exceptions.RequestException:
        return jsonify({"error": "Network pipeline error"}), 500

@app.route("/search/<barcode>/import", methods=["POST"])
def import_product(barcode):
    if any(str(item["barcode"]) == str(barcode) for item in db.get_all_items()):
        return jsonify({"error": "Product with this barcode already exists in inventory"}), 400

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {"User-Agent": "StudentInventoryLab/1.0 (Flask REST API School Project)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        product = response.json()
        if response.status_code != 200 or product.get("status") == 0:
            return jsonify({"error": "Product not found on remote server catalog"}), 404

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)