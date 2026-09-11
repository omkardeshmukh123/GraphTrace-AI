"""Order service — manages order lifecycle."""


class OrderService:
    """Handles order creation, update, and payment triggering."""

    def __init__(self, order_repository, payment_service):
        self.order_repository = order_repository
        self.payment_service = payment_service

    def create_order(self, user_id: str, items: list) -> dict:
        total = sum(item["price"] * item["qty"] for item in items)
        order = self.order_repository.save({"user_id": user_id, "items": items, "total": total})
        return order

    def cancel_order(self, order_id: str) -> bool:
        order = self.order_repository.find(order_id)
        if not order:
            return False
        self.order_repository.update_status(order_id, "CANCELLED")
        return True

    def process_payment(self, order_id: str, payment_method: str) -> dict:
        order = self.order_repository.find(order_id)
        result = self.payment_service.charge(order["total"], payment_method)
        if result["success"]:
            self.order_repository.update_status(order_id, "PAID")
        return result


class OrderRepository:
    """Data access layer for orders."""

    def __init__(self):
        self._store: dict = {}

    def save(self, order: dict) -> dict:
        order_id = str(len(self._store) + 1)
        order["id"] = order_id
        self._store[order_id] = order
        return order

    def find(self, order_id: str) -> dict | None:
        return self._store.get(order_id)

    def update_status(self, order_id: str, status: str) -> None:
        if order_id in self._store:
            self._store[order_id]["status"] = status
