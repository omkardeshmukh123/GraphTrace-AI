"""REST API controllers — mapping HTTP endpoints to business services."""


class AuthController:
    """Handles authentication and session requests."""

    def __init__(self, auth_service, audit_logger):
        self.auth_service = auth_service
        self.audit_logger = audit_logger

    def handle_login(self, request_data: dict) -> dict:
        """Endpoint: POST /api/auth/login"""
        username = request_data.get("username", "")
        password = request_data.get("password", "")
        ip_address = request_data.get("ip_address", "127.0.0.1")

        try:
            token = self.auth_service.login(username, password)
            self.audit_logger.record_login_attempt(username, True, ip_address)
            return {"success": True, "token": token}
        except ValueError as err:
            self.audit_logger.record_login_attempt(username, False, ip_address)
            return {"success": False, "error": str(err)}

    def handle_logout(self, token: str) -> dict:
        """Endpoint: POST /api/auth/logout"""
        self.auth_service.logout(token)
        return {"success": True, "message": "Logged out successfully"}


class OrderController:
    """Handles customer shopping cart checkout and order operations."""

    def __init__(self, order_service, inventory_service, notification_dispatcher):
        self.order_service = order_service
        self.inventory_service = inventory_service
        self.notification_dispatcher = notification_dispatcher

    def handle_checkout(self, user_id: str, cart_data: dict) -> dict:
        """Endpoint: POST /api/orders/checkout"""
        items = cart_data.get("items", [])
        if not items:
            return {"error": "Cart is empty"}

        order = self.order_service.create_order(user_id, items)
        reservation = self.inventory_service.reserve_stock(order["id"], items)
        if not reservation["success"]:
            self.order_service.cancel_order(order["id"])
            return {"error": "Out of stock", "details": reservation}

        # Trigger notification
        self.notification_dispatcher.send_order_confirmation(
            recipient_email=f"user-{user_id}@example.com",
            order=order,
        )
        return {"success": True, "order": order}

    def handle_cancel(self, order_id: str) -> dict:
        """Endpoint: POST /api/orders/{order_id}/cancel"""
        success = self.order_service.cancel_order(order_id)
        return {"success": success, "order_id": order_id}


class PaymentController:
    """Handles payment settlement and webhook ingestion."""

    def __init__(self, payment_gateway, audit_logger):
        self.payment_gateway = payment_gateway
        self.audit_logger = audit_logger

    def handle_payment(self, payload: dict) -> dict:
        """Endpoint: POST /api/payments/charge"""
        amount = payload.get("amount", 0.0)
        currency = payload.get("currency", "USD")
        token = payload.get("token", "")
        idempotency_key = payload.get("idempotency_key", "")

        result = self.payment_gateway.charge(amount, currency, token, idempotency_key)
        self.audit_logger.log_event("PAYMENT_CHARGED", token, result)
        return result

    def handle_webhook(self, raw_body: str, signature: str) -> dict:
        """Endpoint: POST /api/payments/webhook"""
        if not self.payment_gateway.verify_signature(raw_body, signature):
            return {"status": 400, "error": "Invalid signature"}
        return {"status": 200, "received": True}


class InventoryController:
    """Handles catalog stock availability queries."""

    def __init__(self, inventory_service):
        self.inventory_service = inventory_service

    def handle_stock_query(self, product_id: str) -> dict:
        """Endpoint: GET /api/inventory/{product_id}/availability"""
        available = self.inventory_service.check_stock(product_id, 1)
        return {"product_id": product_id, "in_stock": available}
