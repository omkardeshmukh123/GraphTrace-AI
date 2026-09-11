"""Unit tests for inventory reservation and threshold alerts."""

from src.inventory_service import InventoryService, WarehouseClient
from src.product_repository import ProductRepository


def test_inventory_reservation_success():
    repo = ProductRepository()
    warehouse = WarehouseClient()
    service = InventoryService(repo, warehouse)

    items = [{"product_id": "PROD-001", "qty": 5}]
    result = service.reserve_stock("ORD-999", items)

    assert result["success"] is True
    assert repo.get_available_stock("PROD-001") == 45


def test_inventory_reservation_insufficient_stock():
    repo = ProductRepository()
    warehouse = WarehouseClient()
    service = InventoryService(repo, warehouse)

    items = [{"product_id": "PROD-003", "qty": 1}]  # Out of stock
    result = service.reserve_stock("ORD-999", items)

    assert result["success"] is False
    assert "Insufficient stock" in result["reason"]
