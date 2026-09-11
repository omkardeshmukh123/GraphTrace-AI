// Auth Context — client-side session state and credential management

class TokenStorage {
  constructor() {
    this._token = null;
  }

  saveToken(token) {
    this._token = token;
  }

  getToken() {
    return this._token;
  }

  removeToken() {
    this._token = null;
  }
}

class AuthContext {
  constructor(apiClient, storage) {
    this.apiClient = apiClient;
    this.storage = storage || new TokenStorage();
    this.currentUser = null;
  }

  async login(username, password) {
    const res = await this.apiClient.post("/api/auth/login", { username, password });
    if (res.success && res.token) {
      this.storage.saveToken(res.token);
      this.apiClient.setToken(res.token);
      this.currentUser = { username };
      return true;
    }
    return false;
  }

  async logout() {
    const token = this.storage.getToken();
    if (token) {
      await this.apiClient.post("/api/auth/logout", { token });
    }
    this.storage.removeToken();
    this.apiClient.clearToken();
    this.currentUser = null;
  }

  isAuthenticated() {
    return !!this.storage.getToken();
  }
}

module.exports = { TokenStorage, AuthContext };
