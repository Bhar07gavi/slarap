#!/usr/bin/env python3

"""Initialize the SLARAP project database."""

from backend import config
from backend.storage import db


def main() -> None:
    db.initialize_database()

    print("SLARAP initialization completed.")
    print(f"Database: {config.DB_PATH}")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Export directory: {config.EXPORT_DIR}")
    print(f"Workflow directory: {config.WORKFLOW_DIR}\n")


if __name__ == "__main__":
    main()
