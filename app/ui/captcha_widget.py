from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QMessageBox
from PyQt6.QtGui import QPixmap, QDrag, QIcon
from PyQt6.QtCore import Qt, QMimeData, QByteArray
import random


class PuzzlePiece(QLabel):
    """Один фрагмент пазла, поддерживает drag & drop."""
    def __init__(self, img_name):
        super().__init__()
        self.img_name = img_name
        self.setPixmap(QPixmap(f"resources/{img_name}").scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        self.setFixedSize(120, 120)
        self.setStyleSheet("border: 1px solid gray;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.img_name)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)


class DropCell(QLabel):
    """Ячейка, куда можно бросать фрагменты."""
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedSize(120, 120)
        self.setStyleSheet("border: 2px dashed gray;")
        self.piece = None

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        img_name = event.mimeData().text()
        self.set_piece(img_name)
        event.acceptProposedAction()

    def set_piece(self, img_name):
        self.piece = img_name
        self.setPixmap(QPixmap(f"resources/{img_name}").scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        self.setStyleSheet("border: 2px solid green;")


class CaptchaWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.correct_order = ["1.png", "2.png", "3.png", "4.png"]

        layout = QGridLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # создаём 4 ячейки для пазла
        self.cells = []
        for i in range(4):
            cell = DropCell()
            self.cells.append(cell)
            layout.addWidget(cell, i // 2, i % 2)

        # создаём перемешанные фрагменты
        shuffled = self.correct_order.copy()
        random.shuffle(shuffled)

        self.pieces = []
        for img in shuffled:
            piece = PuzzlePiece(img)
            self.pieces.append(piece)
            layout.addWidget(piece, 2 + shuffled.index(img) // 2, shuffled.index(img) % 2)

        # кнопка проверки
        self.check_btn = QPushButton("Проверить капчу")
        self.check_btn.clicked.connect(self.check_captcha)
        layout.addWidget(self.check_btn, 4, 0, 1, 2)

        self.setFixedSize(self.sizeHint())


    def check_captcha(self):
        user_order = [cell.piece for cell in self.cells]

        if None in user_order:
            QMessageBox.warning(self, "Ошибка", "Пазл не полностью собран")
            return

        if user_order == self.correct_order:
            QMessageBox.information(self, "Капча", "Пазл собран верно!")
            self.parent().captcha_passed = True
        else:
            QMessageBox.warning(self, "Ошибка", "Пазл собран неверно!")
            self.parent().captcha_attempts += 1
