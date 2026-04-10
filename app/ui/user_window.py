from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView
)
from database.db_connector import Database


class UserWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.setWindowTitle("Панель обычного пользователя")

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        self.setFixedSize(self.size())
