"""Notification service — handles multi-channel communication (email, SMS, alerts)."""


class NotificationDispatcher:
    """Dispatches lifecycle notifications to customers and staff."""

    def __init__(self, email_client, sms_notifier):
        self.email_client = email_client
        self.sms_notifier = sms_notifier

    def send_order_confirmation(self, recipient_email: str, order: dict) -> bool:
        """Send order confirmation email to customer upon successful payment."""
        subject = f"Your CloudScale Order #{order.get('id', 'N/A')} is Confirmed!"
        body = f"Thank you for shopping. Your total is {order.get('total', 0)}. Items: {len(order.get('items', []))}."
        return self.email_client.send_mail(recipient_email, subject, body)

    def send_stock_alert(self, product_id: str, remaining_stock: int) -> bool:
        """Alert inventory staff when stock breaches minimum safety levels."""
        subject = f"WARNING: Low Stock on Product {product_id}"
        body = f"Remaining quantity is currently {remaining_stock} units. Restocking required."
        return self.email_client.send_mail("inventory-ops@cloudscale.example.com", subject, body)

    def send_receipt(self, recipient_email: str, receipt: dict) -> bool:
        """Deliver tax invoice and receipt payload."""
        subject = f"Payment Receipt for Invoice #{receipt.get('invoice_no', '000')}"
        body = f"Amount charged: {receipt.get('amount', 0)} via {receipt.get('method', 'card')}."
        return self.email_client.send_mail(recipient_email, subject, body)


class EmailClient:
    """SMTP / transactional email adapter."""

    def send_mail(self, to: str, subject: str, body: str) -> bool:
        """Dispatch email message over outbound transport."""
        return True


class SMSNotifier:
    """Twilio / SMS cellular notification gateway."""

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Deliver short text notification to registered phone number."""
        return True
