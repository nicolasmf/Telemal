class User:
    def __init__(
        self,
        id: int,
        is_bot: bool,
        status: str,
        first_name: str,
        username: str | None,
        is_anonymous: bool,
    ):
        self.id = id
        self.is_bot = is_bot
        self.status = status
        self.first_name = first_name
        self.username = username
        self.is_anonymous = is_anonymous

    def __str__(self):
        if self.username:
            return f"id: {self.id}, first_name: {self.first_name}, username: {self.username}, status: {self.status}, is_bot: {self.is_bot}, is_anonymous: {self.is_anonymous}"
        else:
            return f"id: {self.id}, first_name: {self.first_name}, status: {self.status}, is_bot: {self.is_bot}, is_anonymous: {self.is_anonymous}"
