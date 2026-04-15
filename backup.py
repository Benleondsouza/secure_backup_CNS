import os
import tarfile
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
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

def create_backup(input_path, output_file, password):
    archive = "temp.tar"

    with tarfile.open(archive, "w") as tar:
        tar.add(input_path, arcname=os.path.basename(input_path))

    with open(archive, "rb") as f:
        data = f.read()

    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)

    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)

    with open(output_file, "wb") as f:
        f.write(salt + nonce + encrypted)

    os.remove(archive)