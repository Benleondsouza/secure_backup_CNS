import os
import tarfile
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
import secrets

from tracker import scan_directory

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

def create_backup(source_folder, output_file, password):
    # Step 1: Compress
    archive_name = "temp_backup.tar"
    with tarfile.open(archive_name, "w") as tar:
        tar.add(source_folder, arcname=os.path.basename(source_folder))

    # Step 2: Read compressed data
    with open(archive_name, "rb") as f:
        data = f.read()

    # Step 3: Key generation
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    nonce = secrets.token_bytes(12)

    # Step 4: Encrypt
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)

    # Step 5: Save output
    with open(output_file, "wb") as f:
        f.write(salt + nonce + encrypted)

    os.remove(archive_name)
    print("✅ Backup created successfully!")