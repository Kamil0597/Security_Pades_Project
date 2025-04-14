import hashlib
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def generate_private_key_RSA():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096           # rozmiar klucza w bitach
    )
    return private_key

def generate_public_key_from_private_RSA(private_key):
    public_key = private_key.public_key()
    return public_key

def hash_user_pin(pin):
    return hashlib.sha256(pin.encode()).digest()

def encrypt_private_key(private_key, hash_pin):

    private_key_bytes = private_key.private_bytes(          # serializacja na bajty
        encoding=serialization.Encoding.PEM,                # format kodowania
        format=serialization.PrivateFormat.PKCS8,           # format dla kluczy prywatnych - klucz razem z informacją o algorytmie
        encryption_algorithm=serialization.NoEncryption()   # brak szyfrowania
    )

    padder = padding.PKCS7(128).padder()                    # dopełnienie do wielkości 16 bajtów
    padded_data = padder.update(private_key_bytes) + padder.finalize()  # dopełnienie danych

    iv = os.urandom(16)                                     # generowanie losowego Initialization Vector

    cipher = Cipher(algorithms.AES(hash_pin), modes.CBC(iv))    #   tworzenie obiektu szyfrującego Cipher używa AES CBC
    encryptor = cipher.encryptor()                              #   obiekt szyfrujący
    encrypted_key = encryptor.update(padded_data) + encryptor.finalize()    #   Szyfruje dane i dodaje końcówkę

    return encrypted_key, iv            # IV potrzebne do odkodowania

def generate_RSA_keys_and_hash_private(PIN):
    private_key = generate_private_key_RSA()
    public_key = generate_public_key_from_private_RSA(private_key)
    hash_PIN = hash_user_pin(PIN)
    encrypted_private_key, iv = encrypt_private_key(private_key, hash_PIN)

    return encrypted_private_key, public_key, iv