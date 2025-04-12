import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel

from cryptography_functions import generate_private_key_RSA, generate_public_key_from_private_RSA
from GUI import BasicApp

if __name__ == '__main__':
    private_key = generate_private_key_RSA()
    public_key = generate_public_key_from_private_RSA(private_key)
    app = QApplication(sys.argv)
    window = BasicApp()
    window.show()
    sys.exit(app.exec())

