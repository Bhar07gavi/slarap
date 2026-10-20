#!/usr/bin/env python3

"""
Test for the Recommendation Engine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.analytics import recommender
from backend.monitor.resources import ResourceMonitor
from backend.storage import db


def main() -> None:
    db.initialize_database()

    monitor = ResourceMonitor(interval=1.0, persist=True)
    monitor.start()

    import time
    time.sleep(2)

    recommendations = recommender.generate_recommendations(monitor, persist=False)
    print(recommender.format_recommendations(recommendations))

    monitor.stop()
    monitor.join(timeout=3)


if __name__ == "__main__":
    main()
