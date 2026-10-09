# Import the unittest framework so we can build automated API tests.
import unittest
# Import JSON support to serialize request data and parse response payloads.
import json
from unittest.mock import patch
# Import the Flask app instance from the main application module.
from app import app

# Create a test class that exercises the Inventory REST API.
class InventoryAPITest(unittest.TestCase):

    # Set up the test environment before each test method runs.
    def setUp(self):
        # Create a test client object to send simulated HTTP requests.
        self.client = app.test_client()
        # Toggle testing mode so Flask raises detailed exceptions during tests.
        self.client.testing = True

        # Reset the in-memory inventory before each test case to keep them isolated.
        app.inventory.items = []

    # Verify the home route is reachable.
    def test_home(self):
        # Send a GET request to the server root.
        response = self.client.get("/")
        # Assert that the root page responds successfully.
        self.assertEqual(response.status_code, 200)

    # Verify the route that lists all items returns an empty array when inventory is empty.
    def test_get_all_items(self):
        # Send a GET request to /items.
        response = self.client.get("/items")
        # Confirm the endpoint succeeds.
        self.assertEqual(response.status_code, 200)
        # Confirm the response body is an empty list.
        self.assertEqual(json.loads(response.data), [])

    # Verify that a new item can be created through the API.
    def test_add_item(self):
        # Build the sample item payload.
        item = {
            # Set the primary identifier.
            "id": 1,
            # Set the product name.
            "name": "Milk",
            # Set the barcode field.
            "barcode": "123456",
            # Set the amount in stock.
            "quantity": 5,
            # Set the price.
            "price": 100.0
        }

        # Send a POST request to create the item.
        response = self.client.post(
            # Hit the /items endpoint.
            "/items",
            # Encode the item as JSON.
            data=json.dumps(item),
            # Mark the request content type as JSON.
            content_type="application/json"
        )

        # Assert that the API accepted the item creation request.
        self.assertEqual(response.status_code, 201)

    # Verify the API can return a single item by ID.
    def test_get_single_item(self):
        # Create a sample item before trying to fetch it.
        self.client.post(
            # Use the create endpoint.
            "/items",
            # Encode the item data in JSON.
            data=json.dumps({
                # Set the second item ID.
                "id": 2,
                # Set the item name.
                "name": "Sugar",
                # Set the barcode.
                "barcode": "999",
                # Set the quantity.
                "quantity": 2,
                # Set the price.
                "price": 50.0
            }),
            # Indicate the request uses JSON.
            content_type="application/json"
        )

        # Request the just-created item by ID.
        response = self.client.get("/items/2")
        # Verify the fetch succeeded.
        self.assertEqual(response.status_code, 200)

    # Verify the PATCH route updates an existing item.
    def test_update_item(self):
        # Create the item being updated.
        self.client.post(
            # Use the item creation route.
            "/items",
            # Encode the item data in JSON.
            data=json.dumps({
                # Set the item ID.
                "id": 3,
                # Set the item name.
                "name": "Bread",
                # Set the barcode.
                "barcode": "111",
                # Set the quantity.
                "quantity": 1,
                # Set the price.
                "price": 40.0
            }),
            # Indicate the request payload is JSON.
            content_type="application/json"
        )

        # Send a partial update to change the price.
        response = self.client.patch(
            # Target the item with ID 3.
            "/items/3",
            # Send an update payload with a new price.
            data=json.dumps({"price": 60.0}),
            # Mark the request type as JSON.
            content_type="application/json"
        )

        # Verify the update request succeeded.
        self.assertEqual(response.status_code, 200)

    # Verify that an item can be removed from the inventory.
    def test_delete_item(self):
        # Create an item before deleting it.
        self.client.post(
            # Call the create route.
            "/items",
            # Encode the item payload as JSON.
            data=json.dumps({
                # Set the item ID.
                "id": 4,
                # Set the name.
                "name": "Rice",
                # Set the barcode.
                "barcode": "222",
                # Set the quantity.
                "quantity": 10,
                # Set the price.
                "price": 200.0
            }),
            # Mark the request as JSON.
            content_type="application/json"
        )

        # Delete the item using the API.
        response = self.client.delete("/items/4")
        # Confirm the delete endpoint returned success.
        self.assertEqual(response.status_code, 200)

    # Verify that the external product search accepts a product name.
    @patch("app.requests.get")
    def test_external_api_route(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "products": [{
                "code": "737628064502",
                "product_name": "Milk",
                "brands": "Farm",
                "categories": "Dairy"
            }]
        }

        response = self.client.get("/search", query_string={"name": "Milk"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products"][0]["barcode"], "737628064502")

    @patch("app.requests.get")
    def test_external_api_route_by_barcode(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": 1,
            "product": {
                "code": "6111266962187",
                "product_name": "Lait frais naturel demi écrémé",
                "brands": "Jaouda",
                "categories": "Meals"
            }
        }

        response = self.client.get("/search", query_string={"barcode": "6111266962187"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products"][0]["barcode"], "6111266962187")
        self.assertEqual(response.json["products"][0]["name"], "Lait frais naturel demi écrémé")


# Run the test suite when this file is executed directly.
if __name__ == "__main__":
    # Launch unittest, which runs all test cases in this file.
    unittest.main()

