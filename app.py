from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from backup import create_backup, get_all_versions
from restore import restore_backup

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backups"
RESTORE_FOLDER = "restored"

for folder in [UPLOAD_FOLDER, BACKUP_FOLDER, RESTORE_FOLDER]:
    os.makedirs(folder, exist_ok=True)


# ─── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/backup")
def backup_page():
    return render_template("backup.html")

@app.route("/versions")
def versions_page():
    return render_template("versions.html")

@app.route("/restore")
def restore_page():
    return render_template("restore.html")


# ─── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/backup", methods=["POST"])
def api_backup():
    file = request.files.get("file")
    password = request.form.get("password")

    if not file or not password:
        return jsonify({"error": "File and password are required."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = create_backup(filepath, BACKUP_FOLDER, password)

    if result == "no_change":
        return jsonify({"status": "no_change", "message": "No changes detected. Backup skipped."})

    return jsonify({
        "status": "created",
        "message": f"Backup v{result['version']} created ({result['type']})",
        "version": result["version"],
        "type": result["type"],
        "folder": result["folder"]
    })


@app.route("/api/versions")
def api_versions():
    versions = get_all_versions(BACKUP_FOLDER)
    # Enrich with sbak file existence
    for v in versions:
        sbak = os.path.join(BACKUP_FOLDER, v["folder"], "backup.sbak")
        v["has_backup_file"] = os.path.exists(sbak)
    return jsonify(versions)


@app.route("/api/restore", methods=["POST"])
def api_restore():
    data = request.get_json()
    folder = data.get("folder")
    password = data.get("password")

    if not folder or not password:
        return jsonify({"error": "Folder and password required."}), 400

    sbak_path = os.path.join(BACKUP_FOLDER, folder, "backup.sbak")

    if not os.path.exists(sbak_path):
        return jsonify({"error": "Backup file not found."}), 404

    success = restore_backup(sbak_path, RESTORE_FOLDER, password)

    if not success:
        return jsonify({"error": "Wrong password or corrupted file."}), 401

    return jsonify({"status": "ok", "message": "Restore completed successfully."})


@app.route("/api/stats")
def api_stats():
    versions = get_all_versions(BACKUP_FOLDER)
    total_size = sum(v.get("size", 0) for v in versions)
    full_count = sum(1 for v in versions if v.get("backup_type") == "full")
    incremental_count = sum(1 for v in versions if v.get("backup_type") == "incremental")

    return jsonify({
        "total_versions": len(versions),
        "full_backups": full_count,
        "incremental_backups": incremental_count,
        "total_original_size": total_size,
        "latest": versions[-1] if versions else None
    })


if __name__ == "__main__":
    app.run(debug=True)