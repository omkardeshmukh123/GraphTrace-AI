"""
Generate hand-authored ArtifactGraph fixtures and a sample project ZIP.

Usage:
    python -m scripts.make_demo

Outputs:
    .data/demo_graph.json               — minimal 12-node fixture for unit tests
    .data/sample_ecommerce_graph.json   — rich enterprise graph (65+ nodes, 8 reqs)
    .data/sample_project.zip            — ZIP of sample_project/ for POST /projects/analyze
    .data/graphs/graph-*.json           — pre-seeded graphs for LocalGraphStore
"""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from backend.app.graph.store import LocalGraphStore
from backend.app.models import ArtifactGraph, Node, Relationship


def demo_graph() -> ArtifactGraph:
    """
    Hand-authored ArtifactGraph fixture for API and adapter tests.
    Import via: POST /projects/import
    """
    nodes = [
        Node(id="demo", type="PROJECT", name="Authentication demo", properties={"source": "hand_authored_demo"}),
        Node(id="file-controller", type="FILE", name="controller.py", properties={"reference": "controller.py"}),
        Node(id="file-auth", type="FILE", name="auth.py", properties={"reference": "auth.py"}),
        Node(id="file-repository", type="FILE", name="repository.py", properties={"reference": "repository.py"}),
        Node(id="class-auth", type="CLASS", name="AuthService", properties={"reference": "auth.py::AuthService", "path": "auth.py", "line_start": 4}),
        Node(id="class-repository", type="CLASS", name="UserRepository", properties={"reference": "repository.py::UserRepository", "path": "repository.py", "line_start": 1}),
        Node(id="function-login", type="FUNCTION", name="login_user", properties={"reference": "controller.py::login_user", "path": "controller.py", "line_start": 5}),
        Node(id="method-login", type="METHOD", name="AuthService.login", properties={"reference": "auth.py::AuthService.login", "path": "auth.py", "line_start": 8}),
        Node(id="method-find", type="METHOD", name="UserRepository.find", properties={"reference": "repository.py::UserRepository.find", "path": "repository.py", "line_start": 2}),
        Node(id="req-login", type="REQUIREMENT", name="REQ-001: User lookup", properties={"reference": "REQ-001", "category": "functional", "description": "Check whether a username exists through the login entry point.", "actor": "User"}),
        Node(id="req-audit", type="REQUIREMENT", name="REQ-002: Audit history", properties={"reference": "REQ-002", "category": "functional", "description": "Record each login attempt.", "actor": "Administrator"}),
        Node(id="readme", type="DOCUMENT", name="README.md", properties={"path": "README.md"}),
    ]

    triples = [
        ("demo", "CONTAINS", "file-controller"),
        ("demo", "CONTAINS", "file-auth"),
        ("demo", "CONTAINS", "file-repository"),
        ("demo", "CONTAINS", "req-login"),
        ("demo", "CONTAINS", "req-audit"),
        ("demo", "CONTAINS", "readme"),
        ("file-controller", "CONTAINS", "function-login"),
        ("file-auth", "CONTAINS", "class-auth"),
        ("file-repository", "CONTAINS", "class-repository"),
        ("class-auth", "CONTAINS", "method-login"),
        ("class-repository", "CONTAINS", "method-find"),
        ("file-controller", "IMPORTS", "file-auth"),
        ("file-controller", "IMPORTS", "file-repository"),
        ("file-auth", "IMPORTS", "file-repository"),
        ("function-login", "CALLS", "method-login"),
        ("method-login", "CALLS", "method-find"),
        ("class-auth", "DEPENDS_ON", "class-repository"),
        ("req-login", "IMPLEMENTED_BY", "function-login"),
    ]

    edges = [
        Relationship(
            source=src,
            target=tgt,
            type=kind,
            properties={"provenance": "manual" if kind == "IMPLEMENTED_BY" else "hand_authored_demo"},
        )
        for src, kind, tgt in triples
    ]

    return ArtifactGraph(project_id="demo", nodes=nodes, relationships=edges)


def sample_ecommerce_graph() -> ArtifactGraph:
    """
    Rich enterprise e-commerce ArtifactGraph fixture representing sample_project/.
    Features 8 formal requirements, 5 backend services, REST controllers,
    frontend client components, and multi-hop call/dependency paths.
    """
    nodes = [
        # Project & Documents
        Node(id="ecommerce-platform", type="PROJECT", name="CloudScale E-Commerce Platform", properties={"source": "repository", "description": "Enterprise microservice platform with auth, orders, payments, inventory, and audit logging."}),
        Node(id="readme", type="DOCUMENT", name="README.md", properties={"path": "README.md"}),
        Node(id="arch-doc", type="DOCUMENT", name="architecture.md", properties={"path": "architecture.md"}),
        Node(id="req-doc", type="DOCUMENT", name="requirements.md", properties={"path": "requirements.md"}),

        # Requirements (SRS REQ-001 through REQ-008)
        Node(id="req-001", type="REQUIREMENT", name="REQ-001: User Authentication & JWT Session Security", properties={"reference": "REQ-001", "category": "security", "actor": "Customer"}),
        Node(id="req-002", type="REQUIREMENT", name="REQ-002: Order Placement & State Machine Verification", properties={"reference": "REQ-002", "category": "core", "actor": "Customer"}),
        Node(id="req-003", type="REQUIREMENT", name="REQ-003: Payment Gateway Processing & Idempotency", properties={"reference": "REQ-003", "category": "finance", "actor": "Payment Gateway"}),
        Node(id="req-004", type="REQUIREMENT", name="REQ-004: Inventory Reservation & Warehouse Stock Control", properties={"reference": "REQ-004", "category": "warehouse", "actor": "Fulfillment"}),
        Node(id="req-005", type="REQUIREMENT", name="REQ-005: Multi-Channel Customer Notification Dispatch", properties={"reference": "REQ-005", "category": "communications", "actor": "Customer"}),
        Node(id="req-006", type="REQUIREMENT", name="REQ-006: Audit Logging & Security Compliance Tracking", properties={"reference": "REQ-006", "category": "compliance", "actor": "Auditor"}),
        Node(id="req-007", type="REQUIREMENT", name="REQ-007: Shopping Cart State Management & Total Calculation", properties={"reference": "REQ-007", "category": "frontend", "actor": "Shopper"}),
        Node(id="req-008", type="REQUIREMENT", name="REQ-008: API Gateway Routing & Rate Limiting", properties={"reference": "REQ-008", "category": "infrastructure", "actor": "Client"}),

        # Packages
        Node(id="pkg-src", type="PACKAGE", name="src", properties={"path": "src"}),
        Node(id="pkg-frontend", type="PACKAGE", name="frontend", properties={"path": "frontend"}),
        Node(id="pkg-tests", type="PACKAGE", name="tests", properties={"path": "tests"}),

        # Backend Files
        Node(id="file-controllers", type="FILE", name="controllers.py", properties={"path": "src/controllers.py", "language": "Python"}),
        Node(id="file-auth-service", type="FILE", name="auth_service.py", properties={"path": "src/auth_service.py", "language": "Python"}),
        Node(id="file-order-service", type="FILE", name="order_service.py", properties={"path": "src/order_service.py", "language": "Python"}),
        Node(id="file-inventory-service", type="FILE", name="inventory_service.py", properties={"path": "src/inventory_service.py", "language": "Python"}),
        Node(id="file-payment-gateway", type="FILE", name="payment_gateway.py", properties={"path": "src/payment_gateway.py", "language": "Python"}),
        Node(id="file-notification-service", type="FILE", name="notification_service.py", properties={"path": "src/notification_service.py", "language": "Python"}),
        Node(id="file-audit-logger", type="FILE", name="audit_logger.py", properties={"path": "src/audit_logger.py", "language": "Python"}),
        Node(id="file-api-gateway", type="FILE", name="api_gateway.py", properties={"path": "src/api_gateway.py", "language": "Python"}),
        Node(id="file-user-repo", type="FILE", name="user_repository.py", properties={"path": "src/user_repository.py", "language": "Python"}),
        Node(id="file-product-repo", type="FILE", name="product_repository.py", properties={"path": "src/product_repository.py", "language": "Python"}),

        # Frontend Files
        Node(id="file-api-client-js", type="FILE", name="api_client.js", properties={"path": "frontend/api_client.js", "language": "JavaScript"}),
        Node(id="file-payment-service-js", type="FILE", name="payment_service.js", properties={"path": "frontend/payment_service.js", "language": "JavaScript"}),
        Node(id="file-checkout-flow-js", type="FILE", name="checkout_flow.js", properties={"path": "frontend/checkout_flow.js", "language": "JavaScript"}),
        Node(id="file-auth-context-js", type="FILE", name="auth_context.js", properties={"path": "frontend/auth_context.js", "language": "JavaScript"}),

        # Test Files
        Node(id="file-test-auth", type="FILE", name="test_auth.py", properties={"path": "tests/test_auth.py", "language": "Python"}),
        Node(id="file-test-orders", type="FILE", name="test_orders.py", properties={"path": "tests/test_orders.py", "language": "Python"}),
        Node(id="file-test-inventory", type="FILE", name="test_inventory.py", properties={"path": "tests/test_inventory.py", "language": "Python"}),

        # Classes
        Node(id="class-auth-ctrl", type="CLASS", name="AuthController", properties={"path": "src/controllers.py", "reference": "src/controllers.py::AuthController"}),
        Node(id="class-order-ctrl", type="CLASS", name="OrderController", properties={"path": "src/controllers.py", "reference": "src/controllers.py::OrderController"}),
        Node(id="class-pay-ctrl", type="CLASS", name="PaymentController", properties={"path": "src/controllers.py", "reference": "src/controllers.py::PaymentController"}),
        Node(id="class-inv-ctrl", type="CLASS", name="InventoryController", properties={"path": "src/controllers.py", "reference": "src/controllers.py::InventoryController"}),
        Node(id="class-auth-svc", type="CLASS", name="AuthService", properties={"path": "src/auth_service.py", "reference": "src/auth_service.py::AuthService"}),
        Node(id="class-jwt-svc", type="CLASS", name="JWTService", properties={"path": "src/auth_service.py", "reference": "src/auth_service.py::JWTService"}),
        Node(id="class-order-svc", type="CLASS", name="OrderService", properties={"path": "src/order_service.py", "reference": "src/order_service.py::OrderService"}),
        Node(id="class-order-repo", type="CLASS", name="OrderRepository", properties={"path": "src/order_service.py", "reference": "src/order_service.py::OrderRepository"}),
        Node(id="class-inv-svc", type="CLASS", name="InventoryService", properties={"path": "src/inventory_service.py", "reference": "src/inventory_service.py::InventoryService"}),
        Node(id="class-wh-client", type="CLASS", name="WarehouseClient", properties={"path": "src/inventory_service.py", "reference": "src/inventory_service.py::WarehouseClient"}),
        Node(id="class-pay-gw", type="CLASS", name="PaymentGateway", properties={"path": "src/payment_gateway.py", "reference": "src/payment_gateway.py::PaymentGateway"}),
        Node(id="class-stripe-client", type="CLASS", name="StripeClient", properties={"path": "src/payment_gateway.py", "reference": "src/payment_gateway.py::StripeClient"}),
        Node(id="class-paypal-client", type="CLASS", name="PayPalClient", properties={"path": "src/payment_gateway.py", "reference": "src/payment_gateway.py::PayPalClient"}),
        Node(id="class-notif-disp", type="CLASS", name="NotificationDispatcher", properties={"path": "src/notification_service.py", "reference": "src/notification_service.py::NotificationDispatcher"}),
        Node(id="class-audit-logger", type="CLASS", name="AuditLogger", properties={"path": "src/audit_logger.py", "reference": "src/audit_logger.py::AuditLogger"}),
        Node(id="class-sec-auditor", type="CLASS", name="SecurityAuditor", properties={"path": "src/audit_logger.py", "reference": "src/audit_logger.py::SecurityAuditor"}),
        Node(id="class-api-gw", type="CLASS", name="APIGateway", properties={"path": "src/api_gateway.py", "reference": "src/api_gateway.py::APIGateway"}),
        Node(id="class-rate-limiter", type="CLASS", name="RateLimiter", properties={"path": "src/api_gateway.py", "reference": "src/api_gateway.py::RateLimiter"}),
        Node(id="class-user-repo", type="CLASS", name="UserRepository", properties={"path": "src/user_repository.py", "reference": "src/user_repository.py::UserRepository"}),
        Node(id="class-product-repo", type="CLASS", name="ProductRepository", properties={"path": "src/product_repository.py", "reference": "src/product_repository.py::ProductRepository"}),
        Node(id="class-cart-mgr", type="CLASS", name="CartManager", properties={"path": "frontend/payment_service.js", "reference": "frontend/payment_service.js::CartManager"}),
        Node(id="class-checkout-flow", type="CLASS", name="CheckoutFlow", properties={"path": "frontend/checkout_flow.js", "reference": "frontend/checkout_flow.js::CheckoutFlow"}),
        Node(id="class-auth-ctx", type="CLASS", name="AuthContext", properties={"path": "frontend/auth_context.js", "reference": "frontend/auth_context.js::AuthContext"}),
        Node(id="class-api-client", type="CLASS", name="APIClient", properties={"path": "frontend/api_client.js", "reference": "frontend/api_client.js::APIClient"}),

        # Methods and Functions
        Node(id="m-auth-login", type="METHOD", name="AuthController.handle_login", properties={"reference": "src/controllers.py::AuthController.handle_login", "path": "src/controllers.py"}),
        Node(id="m-order-checkout", type="METHOD", name="OrderController.handle_checkout", properties={"reference": "src/controllers.py::OrderController.handle_checkout", "path": "src/controllers.py"}),
        Node(id="m-order-cancel", type="METHOD", name="OrderController.handle_cancel", properties={"reference": "src/controllers.py::OrderController.handle_cancel", "path": "src/controllers.py"}),
        Node(id="m-pay-charge", type="METHOD", name="PaymentController.handle_payment", properties={"reference": "src/controllers.py::PaymentController.handle_payment", "path": "src/controllers.py"}),
        Node(id="m-inv-query", type="METHOD", name="InventoryController.handle_stock_query", properties={"reference": "src/controllers.py::InventoryController.handle_stock_query", "path": "src/controllers.py"}),

        Node(id="m-auth-do-login", type="METHOD", name="AuthService.login", properties={"reference": "src/auth_service.py::AuthService.login", "path": "src/auth_service.py"}),
        Node(id="m-auth-verify", type="METHOD", name="AuthService.verify_token", properties={"reference": "src/auth_service.py::AuthService.verify_token", "path": "src/auth_service.py"}),
        Node(id="m-jwt-gen", type="METHOD", name="JWTService.generate_token", properties={"reference": "src/auth_service.py::JWTService.generate_token", "path": "src/auth_service.py"}),
        Node(id="f-hash-pw", type="FUNCTION", name="hash_password", properties={"reference": "src/user_repository.py::hash_password", "path": "src/user_repository.py"}),
        Node(id="f-validate-email", type="FUNCTION", name="validate_email", properties={"reference": "src/user_repository.py::validate_email", "path": "src/user_repository.py"}),

        Node(id="m-order-create", type="METHOD", name="OrderService.create_order", properties={"reference": "src/order_service.py::OrderService.create_order", "path": "src/order_service.py"}),
        Node(id="m-order-cancel-svc", type="METHOD", name="OrderService.cancel_order", properties={"reference": "src/order_service.py::OrderService.cancel_order", "path": "src/order_service.py"}),
        Node(id="m-order-save", type="METHOD", name="OrderRepository.save", properties={"reference": "src/order_service.py::OrderRepository.save", "path": "src/order_service.py"}),
        Node(id="m-order-update", type="METHOD", name="OrderRepository.update_status", properties={"reference": "src/order_service.py::OrderRepository.update_status", "path": "src/order_service.py"}),

        Node(id="m-inv-check", type="METHOD", name="InventoryService.check_stock", properties={"reference": "src/inventory_service.py::InventoryService.check_stock", "path": "src/inventory_service.py"}),
        Node(id="m-inv-reserve", type="METHOD", name="InventoryService.reserve_stock", properties={"reference": "src/inventory_service.py::InventoryService.reserve_stock", "path": "src/inventory_service.py"}),
        Node(id="m-prod-stock", type="METHOD", name="ProductRepository.get_available_stock", properties={"reference": "src/product_repository.py::ProductRepository.get_available_stock", "path": "src/product_repository.py"}),
        Node(id="m-prod-decrement", type="METHOD", name="ProductRepository.decrement_stock", properties={"reference": "src/product_repository.py::ProductRepository.decrement_stock", "path": "src/product_repository.py"}),

        Node(id="m-pay-exec-charge", type="METHOD", name="PaymentGateway.charge", properties={"reference": "src/payment_gateway.py::PaymentGateway.charge", "path": "src/payment_gateway.py"}),
        Node(id="m-pay-refund", type="METHOD", name="PaymentGateway.refund", properties={"reference": "src/payment_gateway.py::PaymentGateway.refund", "path": "src/payment_gateway.py"}),
        Node(id="m-stripe-intent", type="METHOD", name="StripeClient.create_payment_intent", properties={"reference": "src/payment_gateway.py::StripeClient.create_payment_intent", "path": "src/payment_gateway.py"}),

        Node(id="m-notif-send-order", type="METHOD", name="NotificationDispatcher.send_order_confirmation", properties={"reference": "src/notification_service.py::NotificationDispatcher.send_order_confirmation", "path": "src/notification_service.py"}),
        Node(id="m-notif-send-alert", type="METHOD", name="NotificationDispatcher.send_stock_alert", properties={"reference": "src/notification_service.py::NotificationDispatcher.send_stock_alert", "path": "src/notification_service.py"}),

        Node(id="m-audit-log", type="METHOD", name="AuditLogger.log_event", properties={"reference": "src/audit_logger.py::AuditLogger.log_event", "path": "src/audit_logger.py"}),
        Node(id="m-audit-login-attempt", type="METHOD", name="AuditLogger.record_login_attempt", properties={"reference": "src/audit_logger.py::AuditLogger.record_login_attempt", "path": "src/audit_logger.py"}),

        Node(id="m-gw-route", type="METHOD", name="APIGateway.route_request", properties={"reference": "src/api_gateway.py::APIGateway.route_request", "path": "src/api_gateway.py"}),
        Node(id="m-gw-limit", type="METHOD", name="RateLimiter.apply_rate_limit", properties={"reference": "src/api_gateway.py::RateLimiter.apply_rate_limit", "path": "src/api_gateway.py"}),
        Node(id="m-user-find", type="METHOD", name="UserRepository.find_by_username", properties={"reference": "src/user_repository.py::UserRepository.find_by_username", "path": "src/user_repository.py"}),

        Node(id="m-js-add-item", type="METHOD", name="CartManager.addItem", properties={"reference": "frontend/payment_service.js::CartManager.addItem", "path": "frontend/payment_service.js"}),
        Node(id="m-js-checkout", type="METHOD", name="CheckoutFlow.startCheckout", properties={"reference": "frontend/checkout_flow.js::CheckoutFlow.startCheckout", "path": "frontend/checkout_flow.js"}),
        Node(id="m-js-auth-login", type="METHOD", name="AuthContext.login", properties={"reference": "frontend/auth_context.js::AuthContext.login", "path": "frontend/auth_context.js"}),
    ]

    triples = [
        # Project contains packages, documents, requirements
        ("ecommerce-platform", "CONTAINS", "pkg-src"),
        ("ecommerce-platform", "CONTAINS", "pkg-frontend"),
        ("ecommerce-platform", "CONTAINS", "pkg-tests"),
        ("ecommerce-platform", "CONTAINS", "readme"),
        ("ecommerce-platform", "CONTAINS", "arch-doc"),
        ("ecommerce-platform", "CONTAINS", "req-doc"),
        ("ecommerce-platform", "CONTAINS", "req-001"),
        ("ecommerce-platform", "CONTAINS", "req-002"),
        ("ecommerce-platform", "CONTAINS", "req-003"),
        ("ecommerce-platform", "CONTAINS", "req-004"),
        ("ecommerce-platform", "CONTAINS", "req-005"),
        ("ecommerce-platform", "CONTAINS", "req-006"),
        ("ecommerce-platform", "CONTAINS", "req-007"),
        ("ecommerce-platform", "CONTAINS", "req-008"),

        # Packages contain files
        ("pkg-src", "CONTAINS", "file-controllers"),
        ("pkg-src", "CONTAINS", "file-auth-service"),
        ("pkg-src", "CONTAINS", "file-order-service"),
        ("pkg-src", "CONTAINS", "file-inventory-service"),
        ("pkg-src", "CONTAINS", "file-payment-gateway"),
        ("pkg-src", "CONTAINS", "file-notification-service"),
        ("pkg-src", "CONTAINS", "file-audit-logger"),
        ("pkg-src", "CONTAINS", "file-api-gateway"),
        ("pkg-src", "CONTAINS", "file-user-repo"),
        ("pkg-src", "CONTAINS", "file-product-repo"),

        ("pkg-frontend", "CONTAINS", "file-api-client-js"),
        ("pkg-frontend", "CONTAINS", "file-payment-service-js"),
        ("pkg-frontend", "CONTAINS", "file-checkout-flow-js"),
        ("pkg-frontend", "CONTAINS", "file-auth-context-js"),

        ("pkg-tests", "CONTAINS", "file-test-auth"),
        ("pkg-tests", "CONTAINS", "file-test-orders"),
        ("pkg-tests", "CONTAINS", "file-test-inventory"),

        # Files contain classes & functions
        ("file-controllers", "CONTAINS", "class-auth-ctrl"),
        ("file-controllers", "CONTAINS", "class-order-ctrl"),
        ("file-controllers", "CONTAINS", "class-pay-ctrl"),
        ("file-controllers", "CONTAINS", "class-inv-ctrl"),

        ("file-auth-service", "CONTAINS", "class-auth-svc"),
        ("file-auth-service", "CONTAINS", "class-jwt-svc"),

        ("file-order-service", "CONTAINS", "class-order-svc"),
        ("file-order-service", "CONTAINS", "class-order-repo"),

        ("file-inventory-service", "CONTAINS", "class-inv-svc"),
        ("file-inventory-service", "CONTAINS", "class-wh-client"),

        ("file-payment-gateway", "CONTAINS", "class-pay-gw"),
        ("file-payment-gateway", "CONTAINS", "class-stripe-client"),
        ("file-payment-gateway", "CONTAINS", "class-paypal-client"),

        ("file-notification-service", "CONTAINS", "class-notif-disp"),
        ("file-audit-logger", "CONTAINS", "class-audit-logger"),
        ("file-audit-logger", "CONTAINS", "class-sec-auditor"),

        ("file-api-gateway", "CONTAINS", "class-api-gw"),
        ("file-api-gateway", "CONTAINS", "class-rate-limiter"),

        ("file-user-repo", "CONTAINS", "class-user-repo"),
        ("file-user-repo", "CONTAINS", "f-hash-pw"),
        ("file-user-repo", "CONTAINS", "f-validate-email"),

        ("file-product-repo", "CONTAINS", "class-product-repo"),

        ("file-payment-service-js", "CONTAINS", "class-cart-mgr"),
        ("file-checkout-flow-js", "CONTAINS", "class-checkout-flow"),
        ("file-auth-context-js", "CONTAINS", "class-auth-ctx"),
        ("file-api-client-js", "CONTAINS", "class-api-client"),

        # Classes contain methods
        ("class-auth-ctrl", "CONTAINS", "m-auth-login"),
        ("class-order-ctrl", "CONTAINS", "m-order-checkout"),
        ("class-order-ctrl", "CONTAINS", "m-order-cancel"),
        ("class-pay-ctrl", "CONTAINS", "m-pay-charge"),
        ("class-inv-ctrl", "CONTAINS", "m-inv-query"),

        ("class-auth-svc", "CONTAINS", "m-auth-do-login"),
        ("class-auth-svc", "CONTAINS", "m-auth-verify"),
        ("class-jwt-svc", "CONTAINS", "m-jwt-gen"),

        ("class-order-svc", "CONTAINS", "m-order-create"),
        ("class-order-svc", "CONTAINS", "m-order-cancel-svc"),
        ("class-order-repo", "CONTAINS", "m-order-save"),
        ("class-order-repo", "CONTAINS", "m-order-update"),

        ("class-inv-svc", "CONTAINS", "m-inv-check"),
        ("class-inv-svc", "CONTAINS", "m-inv-reserve"),
        ("class-product-repo", "CONTAINS", "m-prod-stock"),
        ("class-product-repo", "CONTAINS", "m-prod-decrement"),

        ("class-pay-gw", "CONTAINS", "m-pay-exec-charge"),
        ("class-pay-gw", "CONTAINS", "m-pay-refund"),
        ("class-stripe-client", "CONTAINS", "m-stripe-intent"),

        ("class-notif-disp", "CONTAINS", "m-notif-send-order"),
        ("class-notif-disp", "CONTAINS", "m-notif-send-alert"),

        ("class-audit-logger", "CONTAINS", "m-audit-log"),
        ("class-audit-logger", "CONTAINS", "m-audit-login-attempt"),

        ("class-api-gw", "CONTAINS", "m-gw-route"),
        ("class-rate-limiter", "CONTAINS", "m-gw-limit"),
        ("class-user-repo", "CONTAINS", "m-user-find"),

        ("class-cart-mgr", "CONTAINS", "m-js-add-item"),
        ("class-checkout-flow", "CONTAINS", "m-js-checkout"),
        ("class-auth-ctx", "CONTAINS", "m-js-auth-login"),

        # Traceability Mappings: Requirements -> Code (IMPLEMENTED_BY)
        ("req-001", "IMPLEMENTED_BY", "m-auth-do-login"),
        ("req-002", "IMPLEMENTED_BY", "m-order-create"),
        ("req-003", "IMPLEMENTED_BY", "m-pay-exec-charge"),
        ("req-004", "IMPLEMENTED_BY", "m-inv-reserve"),
        ("req-005", "IMPLEMENTED_BY", "m-notif-send-order"),
        ("req-006", "IMPLEMENTED_BY", "m-audit-log"),
        ("req-007", "IMPLEMENTED_BY", "m-js-add-item"),
        ("req-008", "IMPLEMENTED_BY", "m-gw-route"),

        # Method Execution Call Chains (CALLS)
        ("m-js-auth-login", "CALLS", "m-auth-login"),
        ("m-auth-login", "CALLS", "m-auth-do-login"),
        ("m-auth-login", "CALLS", "m-audit-login-attempt"),
        ("m-audit-login-attempt", "CALLS", "m-audit-log"),
        ("m-auth-do-login", "CALLS", "m-user-find"),
        ("m-auth-do-login", "CALLS", "m-jwt-gen"),
        ("m-auth-do-login", "CALLS", "f-hash-pw"),

        ("m-js-checkout", "CALLS", "m-order-checkout"),
        ("m-order-checkout", "CALLS", "m-order-create"),
        ("m-order-create", "CALLS", "m-order-save"),
        ("m-order-checkout", "CALLS", "m-inv-reserve"),
        ("m-inv-reserve", "CALLS", "m-inv-check"),
        ("m-inv-check", "CALLS", "m-prod-stock"),
        ("m-inv-reserve", "CALLS", "m-prod-decrement"),
        ("m-order-checkout", "CALLS", "m-notif-send-order"),

        ("m-pay-charge", "CALLS", "m-pay-exec-charge"),
        ("m-pay-exec-charge", "CALLS", "m-stripe-intent"),
        ("m-pay-charge", "CALLS", "m-audit-log"),

        ("m-gw-route", "CALLS", "m-gw-limit"),
        ("m-gw-route", "CALLS", "m-auth-verify"),

        # Class Dependencies (DEPENDS_ON)
        ("class-auth-ctrl", "DEPENDS_ON", "class-auth-svc"),
        ("class-auth-ctrl", "DEPENDS_ON", "class-audit-logger"),
        ("class-auth-svc", "DEPENDS_ON", "class-user-repo"),
        ("class-auth-svc", "DEPENDS_ON", "class-jwt-svc"),
        ("class-order-ctrl", "DEPENDS_ON", "class-order-svc"),
        ("class-order-ctrl", "DEPENDS_ON", "class-inv-svc"),
        ("class-order-ctrl", "DEPENDS_ON", "class-notif-disp"),
        ("class-order-svc", "DEPENDS_ON", "class-order-repo"),
        ("class-inv-svc", "DEPENDS_ON", "class-product-repo"),
        ("class-pay-ctrl", "DEPENDS_ON", "class-pay-gw"),
        ("class-pay-gw", "DEPENDS_ON", "class-stripe-client"),
        ("class-api-gw", "DEPENDS_ON", "class-rate-limiter"),
        ("class-checkout-flow", "DEPENDS_ON", "class-cart-mgr"),

        # File Imports (IMPORTS)
        ("file-controllers", "IMPORTS", "file-auth-service"),
        ("file-controllers", "IMPORTS", "file-order-service"),
        ("file-controllers", "IMPORTS", "file-inventory-service"),
        ("file-controllers", "IMPORTS", "file-payment-gateway"),
        ("file-controllers", "IMPORTS", "file-audit-logger"),
        ("file-controllers", "IMPORTS", "file-notification-service"),
        ("file-auth-service", "IMPORTS", "file-user-repo"),
        ("file-order-service", "IMPORTS", "file-payment-gateway"),
        ("file-inventory-service", "IMPORTS", "file-product-repo"),
        ("file-checkout-flow-js", "IMPORTS", "file-payment-service-js"),
        ("file-checkout-flow-js", "IMPORTS", "file-api-client-js"),
        ("file-auth-context-js", "IMPORTS", "file-api-client-js"),

        # Documentation Links
        ("ecommerce-platform", "DOCUMENTED_BY", "readme"),
        ("ecommerce-platform", "DOCUMENTED_BY", "arch-doc"),
        ("ecommerce-platform", "DOCUMENTED_BY", "req-doc"),
    ]

    edges = [
        Relationship(
            source=src,
            target=tgt,
            type=kind,
            properties={"provenance": "manual" if kind == "IMPLEMENTED_BY" else "repository"},
        )
        for src, kind, tgt in triples
    ]

    return ArtifactGraph(project_id="ecommerce-platform", nodes=nodes, relationships=edges)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    output_dir = root / ".data"
    output_dir.mkdir(exist_ok=True)

    # 1. Write demo graph JSON (for minimal fixture import)
    graph_path = output_dir / "demo_graph.json"
    graph_path.write_text(demo_graph().model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Created {graph_path.relative_to(root)}")

    # 2. Write sample enterprise e-commerce graph JSON
    ecom_graph_path = output_dir / "sample_ecommerce_graph.json"
    ecom_graph = sample_ecommerce_graph()
    ecom_graph_path.write_text(ecom_graph.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Created {ecom_graph_path.relative_to(root)}")

    # 3. Write sample_project ZIP (for analyze endpoint)
    zip_path = output_dir / "sample_project.zip"
    sample_dir = root / "sample_project"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(sample_dir.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(sample_dir).as_posix())
    print(f"Created {zip_path.relative_to(root)}")

    # 4. Pre-seed both graphs directly into LocalGraphStore (.data/graphs/)
    store = LocalGraphStore(output_dir)
    for g in (demo_graph(), ecom_graph):
        target_path = store._path(g.project_id)
        # Safely remove previous pre-seeded file if present
        target_path.unlink(missing_ok=True)
        store.save(g)
        print(f"Pre-seeded project '{g.project_id}' into LocalGraphStore: {target_path.name}")

    print("\nReady! Both projects ('demo' and 'ecommerce-platform') are pre-seeded in LocalGraphStore.")
