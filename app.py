from flask import Flask, render_template, request
import os
from backup import create_backup
from restore import restore_backup

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backups"
RESTORE_FOLDER = "restored"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)
os.makedirs(RESTORE_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

# BACKUP
@app.route("/backup", methods=["GET", "POST"])
def backup():
    if request.method == "POST":
        file = request.files["file"]
        password = request.form["password"]

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        output_file = os.path.join(BACKUP_FOLDER, file.filename + ".sbak")

        create_backup(filepath, output_file, password)

        return "✅ Backup Created Successfully!"

    return render_template("backup.html")

# LIST BACKUPS
@app.route("/backups")
def backups():
    files = os.listdir(BACKUP_FOLDER)
    return render_template("backups.html", files=files)

# RESTORE FROM SERVER FILE
@app.route("/restore/<filename>", methods=["POST"])
def restore_file(filename):
    password = request.form["password"]
    filepath = os.path.join(BACKUP_FOLDER, filename)

    success = restore_backup(filepath, RESTORE_FOLDER, password)

    if not success:
        return "❌ Wrong password or corrupted file!"

    return "✅ Restore Completed!"

if __name__ == "__main__":
    app.run(debug=True)