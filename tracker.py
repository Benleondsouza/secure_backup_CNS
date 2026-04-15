import hashlib
import os

def get_file_hash(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_directory(folder):
    file_hashes = {}
    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            file_hashes[path] = get_file_hash(path)
    return file_hashes

def get_changed_files(old, new):
    changed = []
    for path, hash_val in new.items():
        if path not in old or old[path] != hash_val:
            changed.append(path)
    return changed