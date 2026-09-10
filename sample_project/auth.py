from repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def login(self, username: str) -> bool:
        return self.repository.find(username) is not None
