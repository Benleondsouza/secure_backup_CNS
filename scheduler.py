import time
from backup import create_backup

def start_scheduler(source, destination, password, interval_hours):
    interval = interval_hours * 3600

    print("⏳ Scheduler started... Press Ctrl+C to stop.")
    try:
        while True:
            filename = f"{destination}/backup_{int(time.time())}.sbak"
            create_backup(source, filename, password)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("🛑 Scheduler stopped.")