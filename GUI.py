import os
import wmi as wmi
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QComboBox, QHBoxLayout, QGroupBox, QFormLayout
from cryptography.hazmat.primitives import serialization

from cryptography_functions import generate_RSA_keys_and_hash_private

folder = "/private_key/"
private_key_filename = "encrypted_private_key.pem"

public_key_path = "C:/public_key/"
public_key_file_name = "public_key.pem"

class BasicApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_value = None
        self.encrypted_private_key = None
        self.public_key = None
        self.iv = None
        self.PIN = None

        self.previous_devices = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Generator klucza RSA")
        self.setGeometry(300, 300, 500, 300)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        usb_group = QGroupBox("Wybór pendrive'a")
        usb_layout = QFormLayout()

        self.combo = QComboBox()
        usb_layout.addRow("Wykryte urządzenia USB:", self.combo)
        usb_group.setLayout(usb_layout)

        main_layout.addWidget(usb_group)

        pin_group = QGroupBox("Kod PIN użytkownika")
        pin_layout = QFormLayout()

        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("Wpisz PIN")
        pin_layout.addRow("PIN:", self.pin_input)
        pin_group.setLayout(pin_layout)

        main_layout.addWidget(pin_group)

        button_layout = QHBoxLayout()

        self.btn_generate = QPushButton("Generuj klucz z Pinu")
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.clicked.connect(self.add_key)

        self.btn_save = QPushButton("Zapisz na pendrive")
        self.btn_save.setFixedHeight(50)
        self.btn_save.clicked.connect(self.save_key_on_pendrive)

        button_layout.addWidget(self.btn_generate)
        button_layout.addWidget(self.btn_save)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.update_usb_devices()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_changes)
        self.timer.start(2000)

    def save_key_on_pendrive(self):
        path = os.path.join(self.selected_value, folder)

        os.makedirs(path, exist_ok=True)

        path = os.path.join(path, private_key_filename)

        with open(path, "wb") as file:
            file.write(self.iv)
            file.write(self.encrypted_private_key)
            print("saved to pendrive")

        os.makedirs(public_key_path, exist_ok=True)

        path = os.path.join(public_key_path, public_key_file_name)

        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(path, "wb") as file:
            file.write(public_key_bytes)
            print("saved on disk")

    def add_key(self):
        pin_code = self.pin_input.text()
        print(pin_code)
        self.encrypted_private_key, self.public_key, self.iv = generate_RSA_keys_and_hash_private(pin_code)


    def get_usb_devices(self):
        c = wmi.WMI()
        usb_devices = []
        usb_devices_paths = []
        for disk in c.Win32_DiskDrive():
            if 'USB' in disk.InterfaceType:
                for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                    for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                        usb_devices_paths.append(logical_disk.DeviceID)
                        usb_devices.append((logical_disk.DeviceID, disk.Model))
        return usb_devices_paths

    def update_usb_devices(self):
        self.combo.blockSignals(True)
        self.combo.clear()
        for device in self.previous_devices:
            self.combo.addItem(device)
        self.combo.blockSignals(False)

    def check_for_changes(self):
        self.selected_value = self.combo.currentText()
        current_devices = self.get_usb_devices()
        if current_devices != self.previous_devices:
            print("Zmiana w liście pendrive’ów!")
            self.previous_devices = current_devices
            self.update_usb_devices()
