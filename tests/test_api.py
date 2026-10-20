"""
Tests for SLARAP FastAPI Integration Layer.
Tests all primary API routes:
- /api/system/snapshot
- /api/system/top-processes
- /api/processes
- /api/command/run
- /api/simulations/scheduling
- /api/simulations/deadlock/bankers/safety
- /api/simulations/memory/page-replacement
- /api/academy/units
- /api/gamification/profile
"""

import sys
from pathlib import Path
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.app import app


def test_api_routes():
    with TestClient(app) as client:
        # 1. System Snapshot
        r = client.get("/api/system/snapshot")
        assert r.status_code == 200
        data = r.json()
        assert "sample" in data
        assert "health_score" in data

        # 2. Top Processes
        r = client.get("/api/system/top-processes?count=5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        # 3. Process Listing
        r = client.get("/api/processes?limit=10")
        assert r.status_code == 200
        assert len(r.json()) > 0

        # 4. Safe Command Execution
        r = client.post("/api/command/run", json={"command": "echo 'API Works!'"})
        assert r.status_code == 200
        cmd_res = r.json()
        assert cmd_res["exit_code"] == 0
        assert "API Works!" in cmd_res["output"]

        # 5. Scheduling Simulation
        r = client.post(
            "/api/simulations/scheduling",
            json={
                "algorithm": "FCFS",
                "processes": [
                    {"id": "P1", "arrival_time": 0, "burst_time": 3},
                    {"id": "P2", "arrival_time": 1, "burst_time": 2},
                ],
            },
        )
        assert r.status_code == 200
        sched_res = r.json()
        assert sched_res["algorithm"] == "FCFS"
        assert len(sched_res["gantt"]) > 0

        # 6. Banker's Algorithm
        r = client.post(
            "/api/simulations/deadlock/bankers/safety",
            json={
                "available": [3, 3, 2],
                "allocation": [[0, 1, 0], [2, 0, 0]],
                "max_matrix": [[7, 5, 3], [3, 2, 2]],
            },
        )
        assert r.status_code == 200
        assert "is_safe" in r.json()

        # 7. Page Replacement
        r = client.post(
            "/api/simulations/memory/page-replacement",
            json={
                "algorithm": "FIFO",
                "reference_string": [1, 2, 3, 1, 4],
                "frame_count": 3,
            },
        )
        assert r.status_code == 200
        assert r.json()["total_faults"] > 0

        # 8. Academy Syllabus
        r = client.get("/api/academy/units")
        assert r.status_code == 200
        assert len(r.json()) == 6

        # 9. Gamification Profile & Progress
        r = client.get("/api/gamification/profile")
        assert r.status_code == 200
        assert "total_xp" in r.json()

        # 10. Award XP (Idempotent)
        r = client.post(
            "/api/gamification/award-xp",
            json={
                "activity_id": "test_activity_1",
                "activity_type": "test",
                "unit_id": "unit1",
                "title": "Test Activity",
                "xp": 25,
            },
        )
        assert r.status_code == 200
        award_res = r.json()
        assert award_res["awarded"] in (True, False)


def main():
    print("Testing FastAPI integration endpoints...")
    test_api_routes()
    print("ALL API INTEGRATION TESTS PASSED!")


if __name__ == "__main__":
    main()
