"""User repository — data access layer for users."""


class UserRepository:
    """Provides CRUD operations on the users table."""

    def find_by_username(self, username: str) -> dict | None:
        # Stub: returns dummy user for sample project
        if username == "admin":
            return {"id": "1", "username": "admin", "password_hash": "abc123"}
        return None

    def find_by_id(self, user_id: str) -> dict | None:
        if user_id == "1":
            return {"id": "1", "username": "admin"}
        return None

    def create_user(self, username: str, password_hash: str) -> dict:
        return {"id": "new_id", "username": username}

    def delete_user(self, user_id: str) -> bool:
        return True


def hash_password(plain: str) -> str:
    """Utility function — hash a plain text password."""
    import hashlib
    return hashlib.sha256(plain.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Utility function — basic email format validation."""
    return "@" in email and "." in email.split("@")[-1]
