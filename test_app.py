# Import the unittest framework for automated testing.
import unittest
# Import the JSON module for request payload handling.
import json
# Import patch to mock external API calls in the CLI test.
#Its used to replace parts in the code during testing
from unittest.mock import patch
# Import the Flask app from the project entry file.
from app import app


# Define the test suite for the API.
class InventoryAPITest(unittest.TestCase):

    # Setup code runs before each test.
    def setUp(self):
        # Create a Flask test client.
        self.client = app.test_client()
        # Turn testing mode on.
        self.client.testing = True

        # Reset the inventory before each test.
        app.inventory.items = []

    # Test the root route.
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # Test listing items when inventory is empty.
    def test_get_all_items(self):
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    # Test creating an item.
    def test_add_item(self):
        item = {
            "id": 1,
            "name": "Milk",
            "barcode": "123456",
            "quantity": 5,
            "price": 100.0
        }

        response = self.client.post(
            "/items",
            data=json.dumps(item),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)

    # Test fetching a single item by ID.
    def test_get_single_item(self):
        self.client.post(
            "/items",
            data=json.dumps({
                "id": 2,
                "name": "Sugar",
                "barcode": "999",
                "quantity": 2,
                "price": 50.0
            }),
            content_type="application/json"
        )

        response = self.client.get("/items/2")
        self.assertEqual(response.status_code, 200)

    # Test updating an item with a patch request.
    def test_update_item(self):
        self.client.post(
            "/items",
            data=json.dumps({
                "id": 3,
                "name": "Bread",
                "barcode": "111",
                "quantity": 1,
                "price": 40.0
            }),
            content_type="application/json"
        )

        response = self.client.patch(
            "/items/3",
            data=json.dumps({"price": 60.0}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

    # Test deleting an item.
    def test_delete_item(self):
        self.client.post(
            "/items",
            data=json.dumps({
                "id": 4,
                "name": "Rice",
                "barcode": "222",
                "quantity": 10,
                "price": 200.0
            }),
            content_type="application/json"
        )

        response = self.client.delete("/items/4")
        self.assertEqual(response.status_code, 200)

    # Test searching the external catalog by product name.
    @patch("app.requests.get")
    def test_external_api_route(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "products": [{
                "code": "123456",
                "product_name": "Milk",
                "brands": "Farm",
                "categories": "Dairy"
            }]
        }

        response = self.client.get("/search", query_string={"name": "Milk"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products"][0]["name"], "Milk")

    # Fall back to matching local items when the external catalog is unavailable.
    @patch("app.requests.get")
    def test_external_search_falls_back_to_local_inventory(self, mock_get):
        app.inventory.items = [{
            "id": 3,
            "name": "Water",
            "barcode": "383883903002",
            "quantity": 1,
            "price": 400.0
        }]
        mock_get.return_value.status_code = 503

        response = self.client.get("/search", query_string={"name": "water"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products"][0]["name"], "Water")
        self.assertTrue(response.json["products"][0]["in_inventory"])
        self.assertIn("External catalog unavailable", response.json["warning"])

    # Test the CLI import prompt flow after barcode lookup.
    @patch("cli.requests.post")
    @patch("cli.requests.get")
    @patch("builtins.input", side_effect=["Milk", "1", "y"])
    def test_search_product_import_prompt(self, mock_input, mock_get, mock_post):
        # Simulate a name search that returns one catalog match.
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "products": [{
                "barcode": "123456",
                "name": "Milk",
                "brand": "Farm",
                "category": "Dairy"
            }]
        }
        # Simulate a valid import response.
        mock_post.return_value.json.return_value = {
            "message": "Successfully auto-saved!",
            "item": {"id": 10, "name": "Milk", "barcode": "123456", "quantity": 1, "price": 9.99}
        }

        from cli import search_product
        search_product()

        # Confirm the CLI searches by name and imports the selected match.
        mock_get.assert_called_once_with(
            "http://127.0.0.1:5000/search",
            params={"name": "Milk"}
        )
        mock_post.assert_called_once_with("http://127.0.0.1:5000/search/123456/import")


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    unittest.main()