from auth import AuthService
from repository import UserRepository


def login_user(username: str) -> bool:
    return AuthService(UserRepository()).login(username)
