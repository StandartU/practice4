class User:
    def __init__(self, user_id, login, password, role, is_blocked, attempts):
        self.id = user_id
        self.login = login
        self.password = password
        self.role = role
        self.is_blocked = is_blocked
        self.attempts = attempts
