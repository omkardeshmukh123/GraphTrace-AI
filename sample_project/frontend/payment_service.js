// Payment service — frontend utility for payment UI interactions

class PaymentService {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.supportedMethods = ["card", "upi", "netbanking"];
  }

  async initiatePayment(orderId, amount, method) {
    if (!this.supportedMethods.includes(method)) {
      throw new Error(`Unsupported payment method: ${method}`);
    }
    const response = await this.apiClient.post("/payments/initiate", {
      order_id: orderId,
      amount,
      method,
    });
    return response.data;
  }

  async getPaymentStatus(paymentId) {
    const response = await this.apiClient.get(`/payments/${paymentId}`);
    return response.data;
  }

  formatAmount(amount, currency = "INR") {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency,
    }).format(amount);
  }
}

class CartManager {
  constructor() {
    this.items = [];
  }

  addItem(product) {
    const existing = this.items.find((i) => i.id === product.id);
    if (existing) {
      existing.qty += 1;
    } else {
      this.items.push({ ...product, qty: 1 });
    }
  }

  removeItem(productId) {
    this.items = this.items.filter((i) => i.id !== productId);
  }

  getTotal() {
    return this.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  }

  clear() {
    this.items = [];
  }
}

function formatOrderSummary(order) {
  return `Order #${order.id} — ${order.items.length} items — Total: ${order.total}`;
}

module.exports = { PaymentService, CartManager, formatOrderSummary };
