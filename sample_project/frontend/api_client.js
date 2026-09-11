// API Client — standard HTTP communications client with JWT injection

class HTTPTransport {
  constructor(baseUrl = "https://api.cloudscale.example.com") {
    this.baseUrl = baseUrl;
  }

  async sendRequest(endpoint, method = "GET", headers = {}, payload = null) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
    };
    if (payload && (method === "POST" || method === "PUT" || method === "PATCH")) {
      config.body = JSON.stringify(payload);
    }
    const res = await fetch(url, config);
    return res.json();
  }
}

class APIClient {
  constructor(transport) {
    this.transport = transport || new HTTPTransport();
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  getHeaders() {
    const headers = {};
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async get(endpoint) {
    return this.transport.sendRequest(endpoint, "GET", this.getHeaders());
  }

  async post(endpoint, body) {
    return this.transport.sendRequest(endpoint, "POST", this.getHeaders(), body);
  }
}

module.exports = { HTTPTransport, APIClient };
