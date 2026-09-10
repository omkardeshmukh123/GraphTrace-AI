"""Auth service — handles JWT-based authentication."""

import hashlib


class AuthService:
    """Manages user login, logout, and token verification."""

    def __init__(self, user_repository, jwt_service):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    def login(self, username: str, password: str) -> str:
        user = self.user_repository.find_by_username(username)
        if not user or not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return self.jwt_service.generate_token(user.id)

    def logout(self, token: str) -> None:
        self.jwt_service.invalidate_token(token)

    def verify_token(self, token: str) -> dict:
        return self.jwt_service.decode_token(token)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return hashlib.sha256(plain.encode()).hexdigest() == hashed


class JWTService:
    """Handles JWT token generation and validation."""

    SECRET_KEY = "graphtrace-sample-secret"

    def generate_token(self, user_id: str) -> str:
        return f"jwt.{user_id}.signed"

    def invalidate_token(self, token: str) -> None:
        pass  # In production: add to a blocklist

    def decode_token(self, token: str) -> dict:
        parts = token.split(".")
        return {"user_id": parts[1] if len(parts) > 1 else None}
