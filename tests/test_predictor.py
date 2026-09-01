#!/usr/bin/env python3

"""
Test for the Predictive Analytics module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config
from backend.analytics import predictor
from backend.storage import db
from backend.monitor.resources import ResourceMonitor


def main() -> None:
    db.initialize_database()

    # Start monitor to collect some in-memory data
    monitor = ResourceMonitor(interval=1.0, persist=True)
    monitor.start()

    import time
    time.sleep(3)  # let it collect 3 samples

    # Predict using monitor's in-memory data
    predictions = predictor.predict_all(monitor, hours=1)

    print(predictor.format_predictions(predictions))

    monitor.stop()
    monitor.join(timeout=3)


if __name__ == "__main__":
    main()
