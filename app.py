from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Temporary in-memory database
inventory = [
    {
        "id": 1,
        "name": "Milk",
        "barcode": "737628064502",
        "quantity": 10,
        "price": 120.0
    }
]


# Home Route
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
            "GET /search/<barcode>"
        ]
    })


# ==========================
# GET ALL ITEMS
# ==========================
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(inventory), 200


# ==========================
# GET ONE ITEM
# ==========================
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):

    for item in inventory:
        if item["id"] == item_id:
            return jsonify(item), 200

    return jsonify({"error": "Item not found"}), 404


# ==========================
# ADD ITEM
# ==========================
@app.route("/items", methods=["POST"])
def add_item():

    data = request.get_json()

    required_fields = ["id", "name", "barcode", "quantity", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # Prevent duplicate IDs
    for item in inventory:
        if item["id"] == data["id"]:
            return jsonify({"error": "Item ID already exists"}), 400

    inventory.append(data)

    return jsonify({
        "message": "Item added successfully",
        "item": data
    }), 201


# ==========================
# UPDATE ITEM
# ==========================
@app.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):

    data = request.get_json()

    for item in inventory:

        if item["id"] == item_id:

            item.update(data)

            return jsonify({
                "message": "Item updated",
                "item": item
            }), 200

    return jsonify({"error": "Item not found"}), 404


# ==========================
# DELETE ITEM
# ==========================
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):

    global inventory

    for item in inventory:

        if item["id"] == item_id:

            inventory.remove(item)

            return jsonify({
                "message": "Item deleted successfully"
            }), 200

    return jsonify({"error": "Item not found"}), 404


# ==========================
# SEARCH PRODUCT USING
# OPEN FOOD FACTS API
# ==========================
@app.route("/search/<barcode>", methods=["GET"])
def search_product(barcode):

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Unable to contact OpenFoodFacts"}), 500

    product = response.json()

    if product.get("status") == 0:
        return jsonify({"error": "Product not found"}), 404

    product_data = product["product"]

    return jsonify({
        "barcode": barcode,
        "name": product_data.get("product_name"),
        "brand": product_data.get("brands"),
        "category": product_data.get("categories"),
        "quantity": product_data.get("quantity")
    })


if __name__ == "__main__":
    app.run(debug=True)