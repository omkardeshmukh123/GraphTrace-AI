"""Product repository — data access for catalog items and stock counts."""


class ProductRepository:
    """Provides inventory storage and stock update queries."""

    def __init__(self):
        self._inventory: dict[str, int] = {
            "PROD-001": 50,
            "PROD-002": 15,
            "PROD-003": 0,
            "PROD-004": 120,
        }
        self._products: dict[str, dict] = {
            "PROD-001": {"id": "PROD-001", "name": "Wireless Mechanical Keyboard", "price": 129.99},
            "PROD-002": {"id": "PROD-002", "name": "4K Ultra-Wide Monitor", "price": 499.99},
            "PROD-003": {"id": "PROD-003", "name": "USB-C Dual Dock", "price": 89.99},
            "PROD-004": {"id": "PROD-004", "name": "Ergonomic Desk Mat", "price": 29.99},
        }

    def get_available_stock(self, product_id: str) -> int:
        """Fetch current warehouse inventory count."""
        return self._inventory.get(product_id, 0)

    def decrement_stock(self, product_id: str, quantity: int) -> int:
        """Safely deduct quantity upon order fulfillment."""
        current = self._inventory.get(product_id, 0)
        new_level = max(0, current - quantity)
        self._inventory[product_id] = new_level
        return new_level

    def increment_stock(self, product_id: str, quantity: int) -> int:
        """Increase quantity during replenishment or restock."""
        current = self._inventory.get(product_id, 0)
        new_level = current + quantity
        self._inventory[product_id] = new_level
        return new_level

    def find_by_sku(self, sku: str) -> dict | None:
        """Locate product metadata by stock keeping unit."""
        return self._products.get(sku)
