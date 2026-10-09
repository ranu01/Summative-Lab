import unittest
import json
from unittest.mock import patch
from app import app


class InventoryAPITest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        app.inventory.items = []

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_all_items(self):
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

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

    def test_external_api_route(self):
        response = self.client.get("/search/737628064502")
        self.assertIn(response.status_code, [200, 404, 500])

    @patch("cli.requests.post")
    @patch("cli.requests.get")
    @patch("builtins.input", side_effect=["123456", "y"])
    def test_search_product_import_prompt(self, mock_input, mock_get, mock_post):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "barcode": "123456",
            "name": "Milk",
            "brand": "Farm",
            "category": "Dairy"
        }
        mock_post.return_value.json.return_value = {
            "message": "Successfully auto-saved!",
            "item": {"id": 10, "name": "Milk", "barcode": "123456", "quantity": 1, "price": 9.99}
        }

        from cli import search_product
        search_product()

        mock_post.assert_called_once_with("http://127.0.0.1:5000/search/123456/import")


if __name__ == "__main__":
    unittest.main()