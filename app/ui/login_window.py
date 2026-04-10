from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from database.db_connector import Database
from ui.captcha_widget import CaptchaWidget
from entities.user import User


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.captcha_passed = False
        self.captcha_attempts = 0

        self.setWindowTitle("Авторизация — Информационная система")

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.try_login)

        self.captcha = CaptchaWidget()
        self.captcha.setParent(self)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите логин и пароль"))
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.captcha)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

        self.setFixedSize(self.sizeHint())


    def try_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Поля логин и пароль обязательны")
            return

        if not self.captcha_passed:
            QMessageBox.warning(self, "Ошибка", "Пройдите капчу")
            return

        # PostgreSQL использует %s вместо ?
        user_data = self.db.fetchone(
            "SELECT id, login, password, role, is_blocked, attempts FROM users WHERE login = %s",
            (login,)
        )

        if not user_data:
            QMessageBox.warning(self, "Ошибка", "Вы ввели неверный логин или пароль.")
            return

        user = User(*user_data)

        # Проверка блокировки
        if user.is_blocked:
            QMessageBox.critical(self, "Блокировка", "Вы заблокированы. Обратитесь к администратору.")
            return

        # Сравнение пароля (strip() нужен, если в БД есть пробелы)
        if user.password.strip() != password.strip():
            user.attempts += 1

            if user.attempts >= 3:
                self.db.execute("UPDATE users SET is_blocked = TRUE WHERE id = %s", (user.id,))
                QMessageBox.critical(self, "Блокировка", "Вы заблокированы. Обратитесь к администратору.")
            else:
                self.db.execute(
                    "UPDATE users SET attempts = %s WHERE id = %s",
                    (user.attempts, user.id)
                )
                QMessageBox.warning(self, "Ошибка", "Вы ввели неверный логин или пароль.")

            return


        self.db.execute("UPDATE users SET attempts = 0 WHERE id = %s", (user.id,))
        QMessageBox.information(self, "Успех", "Вы успешно авторизовались")

        if user.role == "Администратор":
            from ui.admin_window import AdminWindow
            self.admin = AdminWindow()
            self.admin.show()
        else:
            from ui.user_window import UserWindow
            self.user = UserWindow()
            self.user.show()

        self.close()
