"""Inventory service — manages warehouse stock, reservations, and inventory health."""


class InventoryService:
    """Provides inventory stock verification, reservation, and restocking logic."""

    def __init__(self, product_repository, warehouse_client):
        self.product_repository = product_repository
        self.warehouse_client = warehouse_client
        self.low_stock_threshold = 10

    def check_stock(self, product_id: str, quantity: int) -> bool:
        """Check if sufficient quantity is available for an item."""
        stock = self.product_repository.get_available_stock(product_id)
        return stock >= quantity

    def reserve_stock(self, order_id: str, items: list) -> dict:
        """Reserve items for a pending order to prevent overselling."""
        for item in items:
            if not self.check_stock(item["product_id"], item["qty"]):
                return {"success": False, "reason": f"Insufficient stock for {item['product_id']}"}
        
        for item in items:
            self.product_repository.decrement_stock(item["product_id"], item["qty"])
        
        return {"success": True, "order_id": order_id, "reserved_items": len(items)}

    def release_stock(self, order_id: str, items: list) -> bool:
        """Release reserved items back to available inventory on cancellation."""
        for item in items:
            self.product_repository.increment_stock(item["product_id"], item["qty"])
        return True

    def restock_item(self, product_id: str, quantity: int) -> int:
        """Add new units of inventory for a given product."""
        return self.product_repository.increment_stock(product_id, quantity)


class WarehouseClient:
    """Interacts with physical fulfillment facilities."""

    def locate_warehouse(self, region: str) -> str:
        """Determine nearest active warehouse facility for dispatch."""
        warehouses = {"us-east": "WH-NEWYORK-01", "us-west": "WH-SEATTLE-02", "eu-central": "WH-FRANKFURT-01"}
        return warehouses.get(region, "WH-CENTRAL-00")

    def dispatch_fulfillment(self, order_id: str, warehouse_id: str) -> dict:
        """Notify warehouse automation to begin item picking and packing."""
        return {"status": "DISPATCHED", "order_id": order_id, "facility": warehouse_id}
