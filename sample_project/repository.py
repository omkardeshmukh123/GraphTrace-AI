class UserRepository:
    def find(self, username: str):
        return {"username": username} if username == "demo" else None
