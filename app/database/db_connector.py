import psycopg2
from psycopg2 import OperationalError


class Database:
    def __init__(self,
                 host="localhost",
                 port=5432,
                 database="postgres",
                 user="postgres",
                 password="postgres"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        self._create_connection()
        self._ensure_users_table()
        self._insert_test_data()

    def _create_connection(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
        except OperationalError as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            self.conn = None
            self.cursor = None

    def execute(self, query: str, params: tuple = ()):
        if not self.cursor:
            print("Нет соединения с базой данных")
            return None

        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.conn.rollback()
            return None

    def fetchone(self, query: str, params: tuple = ()):
        cur = self.execute(query, params)
        return cur.fetchone() if cur else None

    def fetchall(self, query: str, params: tuple = ()):
        cur = self.execute(query, params)
        return cur.fetchall() if cur else None


    def _ensure_users_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            is_blocked BOOLEAN DEFAULT FALSE,
            attempts INTEGER DEFAULT 0
        );
        """
        self.execute(create_table_query)


    def _insert_test_data(self):
        count = self.fetchone("SELECT COUNT(*) FROM users")
        if count and count[0] > 0:
            return

        test_users = [
            ("admin", "admin123", "Администратор", False, 0),
            ("user1", "pass1", "Пользователь", False, 0),
            ("user2", "pass2", "Пользователь", False, 0),
            ("blocked_user", "qwerty", "Пользователь", True, 3),
            ("fail_user", "1111", "Пользователь", False, 2),
        ]

        for login, password, role, is_blocked, attempts in test_users:
            self.execute(
                "INSERT INTO users (login, password, role, is_blocked, attempts) VALUES (%s, %s, %s, %s, %s)",
                (login, password, role, is_blocked, attempts)
            )

