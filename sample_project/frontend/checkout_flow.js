// Checkout Flow — coordinates cart submission, address validation, and payment settlement

class OrderSummary {
  computeBreakdown(items) {
    const subtotal = items.reduce((acc, item) => acc + item.price * item.qty, 0);
    const tax = subtotal * 0.08;
    const shipping = subtotal > 50 ? 0 : 9.99;
    const total = subtotal + tax + shipping;

    return {
      subtotal: Math.round(subtotal * 100) / 100,
      tax: Math.round(tax * 100) / 100,
      shipping: Math.round(shipping * 100) / 100,
      total: Math.round(total * 100) / 100,
    };
  }
}

class CheckoutFlow {
  constructor(apiClient, paymentService) {
    this.apiClient = apiClient;
    this.paymentService = paymentService;
    this.summaryCalculator = new OrderSummary();
  }

  async startCheckout(cartItems) {
    const summary = this.summaryCalculator.computeBreakdown(cartItems);
    const orderPayload = {
      items: cartItems,
      ...summary,
    };
    const response = await this.apiClient.post("/api/orders/checkout", orderPayload);
    return response;
  }

  async processOrder(orderId, amount, paymentMethod) {
    const chargeResult = await this.paymentService.initiatePayment(orderId, amount, paymentMethod);
    return chargeResult;
  }

  async confirmReceipt(orderId) {
    return this.apiClient.get(`/api/orders/${orderId}/receipt`);
  }
}

module.exports = { CheckoutFlow, OrderSummary };
