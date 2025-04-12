from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class PIN_window(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.PIN = None

        self.setWindowTitle("PIN")
        self.setFixedSize(400, 400)

        layout =QVBoxLayout()

        self.label = QLabel("Podaj kod PIN", self)
        layout.addWidget(self.label)

        self.pin_field = QLineEdit(self)
        self.pin_field.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pin_field)

        self.button = QPushButton("Save PIN", self)
        self.button.clicked.connect(self.save_pin)
        layout.addWidget(self.button)

        self.setLayout(layout)


    def save_pin(self):
        self.PIN = self.pin_field.text()
        self.accept()

    def get_pin(self):
        return self.PIN