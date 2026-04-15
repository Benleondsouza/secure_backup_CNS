import os
import tarfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from argon2.low_level import hash_secret_raw, Type

def derive_key(password, salt):
    return hash_secret_raw(
        password.encode(),
        salt,
        time_cost=2,
        memory_cost=65536,
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )

def restore_backup(input_file, output_folder, password):
    with open(input_file, "rb") as f:
        data = f.read()

    salt = data[:16]
    nonce = data[16:28]
    encrypted = data[28:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        decrypted = aesgcm.decrypt(nonce, encrypted, None)
    except InvalidTag:
        return False  # IMPORTANT FIX

    temp = "temp_restore.tar"
    with open(temp, "wb") as f:
        f.write(decrypted)

    with tarfile.open(temp, "r") as tar:
        tar.extractall(output_folder)

    os.remove(temp)
    return True