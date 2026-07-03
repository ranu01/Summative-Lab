import requests

BASE_URL = "https://world.openfoodfacts.org/api/v0/product"


def get_product_by_barcode(barcode):
    """
    Fetch product information from OpenFoodFacts using a barcode.
    Returns a dictionary with selected product details or None if not found.
    """

    url = f"{BASE_URL}/{barcode}.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("status") == 0:
            return None

        product = data.get("product", {})

        return {
            "barcode": barcode,
            "name": product.get("product_name", "Unknown"),
            "brand": product.get("brands", "Unknown"),
            "category": product.get("categories", "Unknown"),
            "quantity": product.get("quantity", "Unknown")
        }

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to OpenFoodFacts: {e}")
        return None


def search_product_by_name(product_name):
    """
    Search products by name using the OpenFoodFacts search API.
    Returns a list of matching products.
    """

    url = (
        "https://world.openfoodfacts.org/cgi/search.pl"
        "?search_terms={}&search_simple=1&action=process&json=1"
    ).format(product_name)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        products = []

        for product in data.get("products", [])[:10]:
            products.append({
                "barcode": product.get("code", ""),
                "name": product.get("product_name", "Unknown"),
                "brand": product.get("brands", "Unknown")
            })

        return products

    except requests.exceptions.RequestException as e:
        print(f"Search failed: {e}")
        return []


if __name__ == "__main__":
    barcode = input("Enter barcode: ")

    product = get_product_by_barcode(barcode)

    if product:
        print("\nProduct Found")
        print("-----------------------")
        for key, value in product.items():
            print(f"{key.capitalize()}: {value}")
    else:
        print("Product not found.")