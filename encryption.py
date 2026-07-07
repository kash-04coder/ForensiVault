from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"


def generate_key():

    if not os.path.exists(KEY_FILE):

        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as f:
            f.write(key)


def load_key():

    with open(KEY_FILE, "rb") as f:
        return f.read()


generate_key()

cipher = Fernet(load_key())


def encrypt_file(filepath):

    with open(filepath, "rb") as f:
        data = f.read()

    encrypted_data = cipher.encrypt(data)

    encrypted_path = filepath + ".enc"

    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    return encrypted_path


def decrypt_file(filepath):

    with open(filepath, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    return decrypted_data