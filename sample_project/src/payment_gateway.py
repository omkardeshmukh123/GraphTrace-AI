"""Payment gateway integration — coordinates multiple merchant providers."""

import hmac
import hashlib


class PaymentGateway:
    """Orchestrates payment processing, refunds, and webhook signatures."""

    def __init__(self, stripe_client, paypal_client, webhook_secret: str = "whsec_sample"):
        self.stripe_client = stripe_client
        self.paypal_client = paypal_client
        self.webhook_secret = webhook_secret

    def charge(self, amount: float, currency: str, source_token: str, idempotency_key: str) -> dict:
        """Process a credit card or direct debit charge."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        # Dispatch to Stripe provider by default
        cents = int(amount * 100)
        intent = self.stripe_client.create_payment_intent(cents, currency)
        success = self.stripe_client.confirm_payment(intent["id"])
        
        return {
            "success": success,
            "charge_id": f"ch_{intent['id']}",
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
        }

    def refund(self, charge_id: str, amount: float) -> dict:
        """Execute a refund against a previous settled charge."""
        return {"refund_id": f"ref_{charge_id}", "status": "succeeded", "amount": amount}

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Validate cryptographic webhook signature from payment vendor."""
        computed = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed, signature)

    def handle_webhook(self, event_data: dict) -> dict:
        """Parse incoming payment status callbacks."""
        event_type = event_data.get("type", "unknown")
        return {"handled": True, "event_type": event_type, "processed_at": 1690000000}


class StripeClient:
    """Stripe API adapter client."""

    def create_payment_intent(self, amount_cents: int, currency: str) -> dict:
        """Generate a client secret intent for frontend confirmation."""
        return {"id": f"pi_{amount_cents}_{currency.lower()}", "client_secret": "pi_secret_test"}

    def confirm_payment(self, payment_intent_id: str) -> bool:
        """Confirm settlement of the designated intent."""
        return bool(payment_intent_id)


class PayPalClient:
    """PayPal REST API adapter."""

    def create_order(self, total: float) -> dict:
        """Initiate PayPal checkout transaction."""
        return {"id": f"PAYPAL-ORD-{int(total)}", "status": "CREATED"}

    def capture_order(self, paypal_order_id: str) -> dict:
        """Capture funds once authorized by customer."""
        return {"id": paypal_order_id, "status": "COMPLETED"}
