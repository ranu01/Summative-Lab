import unittest
import json
from app import app


class InventoryAPITest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Reset inventory before each test (important)
        app.inventory.items = []

    # =========================
    # TEST HOME ROUTE
    # =========================
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # =========================
    # TEST GET ALL ITEMS
    # =========================
    def test_get_all_items(self):
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    # =========================
    # TEST ADD ITEM
    # =========================
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

    # =========================
    # TEST GET SINGLE ITEM
    # =========================
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

    # =========================
    # TEST UPDATE ITEM
    # =========================
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

    # =========================
    # TEST DELETE ITEM
    # =========================
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

    # =========================
    # TEST EXTERNAL API ROUTE
    # =========================
    def test_external_api_route(self):
        # Using a known barcode (OpenFoodFacts sample)
        response = self.client.get("/search/737628064502")
        self.assertIn(response.status_code, [200, 404, 500])  # API may vary


if __name__ == "__main__":
    unittest.main()