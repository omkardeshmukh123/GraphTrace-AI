# CloudScale E-Commerce Platform

A production-grade Python and JavaScript enterprise e-commerce platform utilized as the primary testbed and demonstration repository for GraphTrace AI.

## Technologies

Python, FastAPI, JavaScript, React, Neo4j, PostgreSQL, Docker, Redis

## Architecture

CloudScale E-Commerce is structured as a modular tiered service architecture:

- **Ingress & Gateway Layer**: `APIGateway` with sliding-window `RateLimiter` and JWT bearer security.
- **Controller Layer** (`src/controllers.py`): RESTful endpoints for `AuthController`, `OrderController`, `PaymentController`, and `InventoryController`.
- **Business Domain Services**:
  - `AuthService` & `JWTService` (`src/auth_service.py`) — Credential verification, session tokens, and cryptographic password hashing.
  - `OrderService` (`src/order_service.py`) — Multi-state order lifecycle management and checkout orchestration.
  - `PaymentGateway` (`src/payment_gateway.py`) — Stripe and PayPal provider integration, payment webhooks, and idempotent billing.
  - `InventoryService` (`src/inventory_service.py`) — Real-time warehouse reservations, decrement logic, and restocking alerts.
  - `NotificationDispatcher` (`src/notification_service.py`) — Multi-channel transactional emails, SMS, and invoice receipts.
  - `AuditLogger` (`src/audit_logger.py`) — Cryptographically signed audit journaling for compliance and fraud detection.
- **Persistence & Repositories**:
  - `UserRepository` (`src/user_repository.py`) — Customer records and credential lookup.
  - `OrderRepository` (`src/order_service.py`) — Order status transitions and persistence.
  - `ProductRepository` (`src/product_repository.py`) — Catalog metadata and inventory counts.
- **Frontend Client** (`frontend/`):
  - `APIClient` (`frontend/api_client.js`) — HTTP transport client with bearer token injection.
  - `PaymentService` & `CartManager` (`frontend/payment_service.js`) — Reactive shopping cart state and currency formatting.
  - `CheckoutFlow` (`frontend/checkout_flow.js`) — Multi-step checkout state machine.
  - `AuthContext` (`frontend/auth_context.js`) — Session persistence and authentication context.
- **Test Suite** (`tests/`):
  - `test_auth.py`, `test_orders.py`, `test_inventory.py` covering core business flows.

## Traceability & Requirements (SRS)

All functional modules are explicitly linked to requirements specified in `requirements.md`:
- `REQ-001`: User Authentication & JWT Session Security
- `REQ-002`: Order Placement & State Machine Verification
- `REQ-003`: Payment Gateway Processing & Idempotency
- `REQ-004`: Inventory Reservation & Warehouse Stock Control
- `REQ-005`: Multi-Channel Customer Notification Dispatch
- `REQ-006`: Audit Logging & Security Compliance Tracking
- `REQ-007`: Shopping Cart State Management & Total Calculation
- `REQ-008`: API Gateway Routing & Rate Limiting

## Setup & Execution

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run test suite:
   ```bash
   pytest tests/
   ```
3. Start backend service:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
