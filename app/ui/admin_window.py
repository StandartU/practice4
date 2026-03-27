from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView
)
from database.db_connector import Database


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.setWindowTitle("Панель администратора")

        main_layout = QVBoxLayout()

        # Таблица пользователей
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Логин", "Роль", "Блокирован", "Попытки"])
        self.table.cellClicked.connect(self.on_row_selected)
        main_layout.addWidget(self.table)

        # Форма редактирования / добавления
        form_layout = QHBoxLayout()

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")

        self.role_input = QComboBox()
        self.role_input.addItems(["Пользователь", "Администратор"])

        form_layout.addWidget(QLabel("Логин:"))
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(QLabel("Пароль:"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(QLabel("Роль:"))
        form_layout.addWidget(self.role_input)

        main_layout.addLayout(form_layout)

        # Кнопки действий
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_user)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_user)

        self.unblock_btn = QPushButton("Снять блокировку")
        self.unblock_btn.clicked.connect(self.unblock_user)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.unblock_btn)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        self.selected_user_id = None
        self.load_users()

    def load_users(self):
        self.table.setRowCount(0)
        users = self.db.fetchall(
            "SELECT id, login, role, is_blocked, attempts FROM users ORDER BY id"
        ) or []

        for row_idx, (user_id, login, role, is_blocked, attempts) in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(login))
            self.table.setItem(row_idx, 2, QTableWidgetItem(role))
            self.table.setItem(row_idx, 3, QTableWidgetItem("Да" if is_blocked else "Нет"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(attempts)))

    def on_row_selected(self, row, column):
        item_id = self.table.item(row, 0)
        item_login = self.table.item(row, 1)
        item_role = self.table.item(row, 2)

        if not item_id:
            return

        self.selected_user_id = int(item_id.text())
        self.login_input.setText(item_login.text())
        self.role_input.setCurrentText(item_role.text())
        self.password_input.clear()  # пароль не показываем

    def add_user(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_input.currentText()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Логин и пароль обязательны")
            return

        # проверка на существование логина
        exists = self.db.fetchone("SELECT id FROM users WHERE login = %s", (login,))
        if exists:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
            return

        self.db.execute(
            "INSERT INTO users (login, password, role, is_blocked, attempts) VALUES (%s, %s, %s, FALSE, 0)",
            (login, password, role)
        )

        QMessageBox.information(self, "Успех", "Пользователь добавлен")
        self.login_input.clear()
        self.password_input.clear()
        self.load_users()

    def update_user(self):
        if not self.selected_user_id:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя в таблице")
            return

        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_input.currentText()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Логин обязателен")
            return

        # проверка уникальности логина (кроме текущего пользователя)
        exists = self.db.fetchone(
            "SELECT id FROM users WHERE login = %s AND id <> %s",
            (login, self.selected_user_id)
        )
        if exists:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
            return

        if password:
            # меняем и логин, и пароль
            self.db.execute(
                "UPDATE users SET login = %s, password = %s, role = %s WHERE id = %s",
                (login, password, role, self.selected_user_id)
            )
        else:
            # меняем только логин и роль
            self.db.execute(
                "UPDATE users SET login = %s, role = %s WHERE id = %s",
                (login, role, self.selected_user_id)
            )

        QMessageBox.information(self, "Успех", "Данные пользователя обновлены")
        self.load_users()

    def unblock_user(self):
        if not self.selected_user_id:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя в таблице")
            return

        self.db.execute(
            "UPDATE users SET is_blocked = FALSE, attempts = 0 WHERE id = %s",
            (self.selected_user_id,)
        )

        QMessageBox.information(self, "Успех", "Блокировка снята")
        self.load_users()
