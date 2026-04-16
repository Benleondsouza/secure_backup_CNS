import os
import tarfile
import secrets
import json
import hashlib
from datetime import datetime

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


def get_file_hash(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_all_versions(backup_root):
    """Return sorted list of all backup version folders."""
    if not os.path.exists(backup_root):
        return []
    versions = []
    for name in sorted(os.listdir(backup_root)):
        folder = os.path.join(backup_root, name)
        meta_path = os.path.join(folder, "metadata.json")
        if os.path.isdir(folder) and os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            meta["folder"] = name
            meta["backup_file"] = os.path.join(folder, "backup.sbak")
            versions.append(meta)
    return versions


def create_backup(input_path, backup_root, password):
    current_hash = get_file_hash(input_path)

    # Check existing versions for incremental logic
    existing_versions = get_all_versions(backup_root)

    previous_hash = None
    version_number = 1

    if existing_versions:
        latest = existing_versions[-1]
        previous_hash = latest.get("hash")
        version_number = latest.get("version", len(existing_versions)) + 1

        # Incremental: skip if no changes
        if previous_hash == current_hash:
            return "no_change"

    # Determine backup type
    backup_type = "full" if version_number == 1 else "incremental"

    # Create versioned folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"v{version_number:03d}_{timestamp}"
    backup_folder = os.path.join(backup_root, folder_name)
    os.makedirs(backup_folder, exist_ok=True)

    # Compress
    archive = os.path.join(backup_folder, "temp.tar")
    with tarfile.open(archive, "w") as tar:
        tar.add(input_path, arcname=os.path.basename(input_path))

    with open(archive, "rb") as f:
        data = f.read()

    # Encrypt
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)

    backup_file = os.path.join(backup_folder, "backup.sbak")
    with open(backup_file, "wb") as f:
        f.write(salt + nonce + encrypted)

    os.remove(archive)

    # Save rich metadata
    metadata = {
        "version": version_number,
        "timestamp": timestamp,
        "original_name": os.path.basename(input_path),
        "size": os.path.getsize(input_path),
        "hash": current_hash,
        "previous_hash": previous_hash,
        "backup_type": backup_type,
        "folder": folder_name
    }

    with open(os.path.join(backup_folder, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    return {"status": "created", "version": version_number, "type": backup_type, "folder": folder_name}