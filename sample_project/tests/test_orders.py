"""Unit tests for order placement and lifecycle transitions."""

from src.order_service import OrderService, OrderRepository


class MockPaymentService:
    def charge(self, total, method):
        return {"success": True, "charge_id": "ch_mock_123"}


def test_order_service_creation_and_payment():
    order_repo = OrderRepository()
    payment_service = MockPaymentService()
    service = OrderService(order_repo, payment_service)

    items = [{"product_id": "PROD-001", "price": 100.0, "qty": 2}]
    order = service.create_order("user-42", items)

    assert order["id"] == "1"
    assert order["total"] == 200.0

    payment = service.process_payment(order["id"], "card")
    assert payment["success"] is True
    assert order_repo.find(order["id"])["status"] == "PAID"
