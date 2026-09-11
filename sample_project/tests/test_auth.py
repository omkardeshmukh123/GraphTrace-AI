"""Unit tests for user authentication and token verification."""

from src.auth_service import AuthService, JWTService
from src.user_repository import UserRepository


def test_auth_service_successful_login():
    repo = UserRepository()
    jwt = JWTService()
    service = AuthService(repo, jwt)

    token = service.login("admin", "abc123")
    assert token.startswith("jwt.")
    assert service.verify_token(token)["user_id"] == "1"


def test_auth_service_invalid_credentials():
    repo = UserRepository()
    jwt = JWTService()
    service = AuthService(repo, jwt)

    try:
        service.login("admin", "wrongpassword")
        assert False, "Expected ValueError"
    except ValueError:
        pass
