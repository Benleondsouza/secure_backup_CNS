import argparse
from backup import create_backup
from restore import restore_backup
from scheduler import start_scheduler

def main():
    parser = argparse.ArgumentParser(description="Secure Backup System")

    subparsers = parser.add_subparsers(dest="command")

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("source")
    backup_parser.add_argument("output")
    backup_parser.add_argument("--password", required=True)

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("input")
    restore_parser.add_argument("output")
    restore_parser.add_argument("--password", required=True)

    schedule_parser = subparsers.add_parser("schedule")
    schedule_parser.add_argument("source")
    schedule_parser.add_argument("output")
    schedule_parser.add_argument("--password", required=True)
    schedule_parser.add_argument("--interval", type=int, required=True)

    args = parser.parse_args()

    if args.command == "backup":
        create_backup(args.source, args.output, args.password)

    elif args.command == "restore":
        restore_backup(args.input, args.output, args.password)

    elif args.command == "schedule":
        start_scheduler(args.source, args.output, args.password, args.interval)

if __name__ == "__main__":
    main()