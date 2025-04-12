import os
import sys
import threading
import time
from glob import glob
from subprocess import check_output

import psutil
import wmi as wmi
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox
from cryptography.hazmat.primitives import serialization

from PIN_window import PIN_window
from cryptography_functions import generate_RSA_keys_and_hash_private
from other_functions import convert_private_key_to_string, convert_public_key_to_string
from PyPDF2 import PdfReader, PdfWriter

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
        self.initUI()

    def initUI(self):

        devices = self.get_usb_devices()

        self.setWindowTitle("Podstawowa aplikacja")
        self.setGeometry(300, 300, 600, 400)

        self.layout = QVBoxLayout()

        # Etykiety informacyjna
        self.label = QLabel("Wybierz plik:", self)
        self.layout.addWidget(self.label)

        self.combo = QComboBox()
        for device in devices:
            self.combo.addItem(device)
        self.layout.addWidget(self.combo)


        # Przycisk
        self.btn_action = QPushButton("Dodaj klucz", self)
        self.btn_action.setFixedSize(120, 60)
        self.btn_action.clicked.connect(self.add_key)
        self.layout.addWidget(self.btn_action)

        self.test_btn = QPushButton("save_key_on_pendrive", self)
        self.test_btn.setFixedSize(120,60)
        self.test_btn.clicked.connect(self.save_key_on_pendrive)
        self.layout.addWidget(self.test_btn)

        self.setLayout(self.layout)

        self.previous_devices = []
        self.update_usb_devices()  # Wczytaj pierwszy raz

        # Timer do sprawdzania zmian co 2000 ms (2 sekundy)
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
        pin_window = PIN_window(self)
        if pin_window.exec():  # Otwieranie okna i czekanie na wynik
            pin_code = pin_window.get_pin()
            print(f"Wprowadzony PIN: {pin_code}")  # Możesz zapisać go gdzieś dalej
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
