"""
SLARAP FastAPI Integration Application.

Connects the React frontend to:
1. Real Linux Administration & Resource Monitoring (psutil, fork, exec, pipes)
2. Interactive Educational OS Simulation Engines (Scheduling, Sync, Deadlocks, Memory, Disk, Filesystem)
3. Persistent Gamification & Academy Progression (Units 1-6, Quizzes, Badges, XP)
"""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend import config
from backend.storage import db
from backend.procmgr import manager
from backend.monitor.resources import calculate_health_score, human_uptime
from backend.analytics import predictor, recommender, logs
from backend.reports import generator
from backend.automation.engine import Task, Workflow

from backend.api.service import ServiceManager
from backend.simulations import (
    scheduling,
    synchronization,
    deadlock,
    memory,
    disk,
    filesys,
    academy,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start singleton monitoring services
    service = ServiceManager.get_instance()
    service.start()
    # Allow 1 second for first telemetry sample
    await asyncio.sleep(1.0)
    yield
    # Shutdown: Cleanly stop background threads
    service.stop()


app = FastAPI(
    title="SLARAP API",
    description="Smart Linux Automation & Resource Analytics Platform API",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Pydantic Request Models
# =========================================================

class KillProcessRequest(BaseModel):
    pid: int
    force: bool = False
    confirmed: bool = False


class RunCommandRequest(BaseModel):
    command: str
    timeout: float = 30.0


class RunPipelineRequest(BaseModel):
    command_a: str
    command_b: str
    timeout: float = 30.0


class BackgroundCommandRequest(BaseModel):
    command: str


class AddScheduledJobRequest(BaseModel):
    name: str
    command: str
    interval_seconds: int
    retries: int = 1


class RunWorkflowRequest(BaseModel):
    workflow_name: Optional[str] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    mode: str = "sequential"
    max_workers: int = 4


class SchedulingSimulationRequest(BaseModel):
    algorithm: str
    processes: List[Dict[str, Any]]
    time_quantum: int = 2
    mlfq_config: Optional[Dict[str, Any]] = None


class RaceConditionRequest(BaseModel):
    iterations: int = 10
    threads_count: int = 2
    use_mutex: bool = False


class BankersSafetyRequest(BaseModel):
    available: List[int]
    allocation: List[List[int]]
    max_matrix: List[List[int]]
    process_names: Optional[List[str]] = None
    resource_names: Optional[List[str]] = None


class BankersResourceRequest(BaseModel):
    available: List[int]
    allocation: List[List[int]]
    max_matrix: List[List[int]]
    process_index: int
    request: List[int]
    process_names: Optional[List[str]] = None
    resource_names: Optional[List[str]] = None


class MemoryAllocationRequest(BaseModel):
    algorithm: str
    blocks: List[int]
    processes: List[Dict[str, Any]]


class PageReplacementRequest(BaseModel):
    algorithm: str
    reference_string: List[int]
    frame_count: int = 3


class DiskSchedulingRequest(BaseModel):
    algorithm: str
    requests: List[int]
    initial_head: int = 53
    disk_size: int = 200
    direction: str = "UP"


class AwardXpRequest(BaseModel):
    activity_id: str
    activity_type: str
    unit_id: str
    title: str
    xp: int
    details: Optional[str] = ""


class QuizSubmissionRequest(BaseModel):
    answers: Dict[str, int]  # question_id -> selected_option_index


# =========================================================
# SECTION 1: SYSTEM CONTROL CENTER ENDPOINTS
# =========================================================

@app.get("/api/system/snapshot")
def get_system_snapshot():
    service = ServiceManager.get_instance()
    sample = service.monitor.get_snapshot()
    score, label = calculate_health_score(sample)
    return {
        "sample": sample,
        "health_score": score,
        "health_label": label,
        "human_uptime": human_uptime(sample.get("uptime", 0)) if sample else "0m",
    }


@app.get("/api/system/history")
def get_system_history():
    service = ServiceManager.get_instance()
    try:
        return {
            "timestamp": service.monitor.get_series("timestamp"),
            "cpu": service.monitor.get_series("cpu"),
            "memory": service.monitor.get_series("memory"),
            "swap": service.monitor.get_series("swap"),
            "disk": service.monitor.get_series("disk"),
            "network_upload": service.monitor.get_series("network_upload"),
            "network_download": service.monitor.get_series("network_download"),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/system/aggregate")
def get_system_aggregate(hours: int = 24, bucket: str = "hour"):
    rows = db.aggregate(hours * 3600, bucket)
    return {"bucket": bucket, "hours": hours, "data": rows}


@app.get("/api/system/thresholds")
def get_system_thresholds():
    return config.THRESHOLDS


@app.get("/api/system/top-processes")
def get_top_processes(count: int = 15, sort_by: str = "cpu"):
    return manager.top_processes(count, sort_by)


@app.get("/api/alerts/recent")
def get_recent_alerts(limit: int = 50):
    service = ServiceManager.get_instance()
    in_memory = service.alerts.get_recent_alerts(limit)
    db_alerts = db.recent_alerts(limit)
    return {
        "recent_in_memory": in_memory,
        "history": db_alerts,
    }


@app.get("/api/analytics/predictions")
def get_predictions(hours: int = 24):
    service = ServiceManager.get_instance()
    predictions = predictor.predict_all(service.monitor, hours=hours)
    return predictions


@app.get("/api/analytics/recommendations")
def get_recommendations():
    service = ServiceManager.get_instance()
    recs = recommender.generate_recommendations(service.monitor, persist=False)
    return recs


@app.get("/api/analytics/logs")
def get_log_analysis(persist: bool = False):
    report = logs.analyze(persist=persist)
    return report


@app.get("/api/reports/all")
def generate_reports():
    service = ServiceManager.get_instance()
    paths = generator.generate_all_reports(service.monitor)
    return paths


@app.get("/api/reports/download/{report_type}")
def download_report(report_type: str):
    service = ServiceManager.get_instance()
    if report_type == "txt":
        path = generator.save_txt_report(service.monitor)
        media_type = "text/plain"
    elif report_type == "csv_metrics":
        path, _ = generator.export_metrics_csv(24)
        media_type = "text/csv"
    elif report_type == "csv_tasks":
        path, _ = generator.export_tasks_csv()
        media_type = "text/csv"
    elif report_type == "csv_alerts":
        path, _ = generator.export_alerts_csv()
        media_type = "text/csv"
    elif report_type == "pdf":
        path, error = generator.export_pdf_report(service.monitor)
        if not path:
            raise HTTPException(status_code=500, detail=error or "PDF generation failed")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Generated report file not found")

    return FileResponse(path=path, filename=Path(path).name, media_type=media_type)


# =========================================================
# SECTION 2: PROCESS MANAGER & COMMAND PLAYGROUND
# =========================================================

@app.get("/api/processes")
def list_processes(
    search: Optional[str] = None,
    sort_by: str = "cpu",
    limit: int = 100,
):
    procs = manager.top_processes(count=limit, sort_by=sort_by)
    if search:
        s_lower = search.lower()
        procs = [
            p for p in procs
            if s_lower in str(p.get("pid", "")).lower()
            or s_lower in str(p.get("name", "")).lower()
            or s_lower in str(p.get("username", "")).lower()
        ]
    return procs


@app.get("/api/processes/tree")
def get_process_tree(root_pid: Optional[int] = None, max_depth: int = 3):
    return manager.process_tree(root_pid=root_pid, max_depth=max_depth)


@app.post("/api/processes/kill")
def kill_process(req: KillProcessRequest):
    if not req.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Process termination requires explicit confirmation (confirmed: true).",
        )
    if req.pid <= 1:
        raise HTTPException(status_code=403, detail="Terminating system PID <= 1 is forbidden.")

    success, message = manager.kill_process(req.pid, force=req.force)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message, "pid": req.pid}


@app.post("/api/command/run")
def run_command(req: RunCommandRequest):
    # Security restriction: validate input command
    cmd = req.command.strip()
    if not cmd:
        raise HTTPException(status_code=400, detail="Command cannot be empty.")

    # Guard against destructive system commands
    blocked_commands = ["rm -rf /", "mkfs", "dd if=/dev/zero", ":(){ :|:& };:"]
    for b in blocked_commands:
        if b in cmd:
            raise HTTPException(status_code=403, detail=f"Command rejected for safety: {b}")

    res = manager.run_with_pipe(cmd, timeout=min(req.timeout, 120.0))
    return res


@app.post("/api/command/pipeline")
def run_pipeline(req: RunPipelineRequest):
    res = manager.pipeline(req.command_a, req.command_b, timeout=req.timeout)
    return res


@app.get("/api/command/background")
def list_background():
    # Reap any finished first
    manager.reap_background_processes()
    return manager.list_background_processes()


@app.post("/api/command/background/start")
def start_background(req: BackgroundCommandRequest):
    cmd = req.command.strip()
    if not cmd:
        raise HTTPException(status_code=400, detail="Command cannot be empty.")
    pid = manager.run_background(cmd)
    return {"pid": pid, "command": cmd, "message": f"Started background process with PID {pid}."}


# =========================================================
# SECTION 3: AUTOMATION & SCHEDULER
# =========================================================

@app.get("/api/automation/workflows")
def list_workflows():
    workflow_dir = Path(config.WORKFLOW_DIR)
    workflows = []
    for wf in workflow_dir.glob("*.json"):
        try:
            with open(wf, "r") as f:
                data = json.load(f)
            workflows.append({
                "file_name": wf.name,
                "name": data.get("name", wf.stem),
                "mode": data.get("mode", "sequential"),
                "tasks": data.get("tasks", []),
            })
        except Exception:
            pass
    return workflows


@app.post("/api/automation/workflows/run")
def run_workflow_endpoint(req: RunWorkflowRequest):
    service = ServiceManager.get_instance()
    if req.workflow_name:
        wf_path = Path(config.WORKFLOW_DIR) / f"{req.workflow_name}.json"
        if not wf_path.exists():
            wf_path = Path(config.WORKFLOW_DIR) / req.workflow_name
        if not wf_path.exists():
            raise HTTPException(status_code=404, detail="Workflow file not found.")
        workflow = Workflow.from_file(wf_path)
    elif req.tasks:
        tasks = [Task.from_dict(t) for t in req.tasks]
        workflow = Workflow(
            name="adhoc_workflow",
            tasks=tasks,
            mode=req.mode,
            max_workers=req.max_workers,
        )
    else:
        raise HTTPException(status_code=400, detail="Must provide workflow_name or tasks list.")

    results = service.engine.run_workflow(workflow)
    return {
        "workflow": workflow.name,
        "mode": workflow.mode,
        "results": results,
    }


@app.get("/api/automation/runs")
def get_automation_history(limit: int = 50):
    return db.recent_task_runs(limit)


@app.get("/api/automation/scheduler/jobs")
def list_scheduled_jobs():
    service = ServiceManager.get_instance()
    return list(service.scheduler.list_jobs())


@app.post("/api/automation/scheduler/jobs")
def add_scheduled_job(req: AddScheduledJobRequest):
    service = ServiceManager.get_instance()
    job = service.scheduler.add_job(
        name=req.name,
        command=req.command,
        interval_seconds=req.interval_seconds,
        retries=req.retries,
    )
    return job


@app.delete("/api/automation/scheduler/jobs/{job_id}")
def remove_scheduled_job(job_id: str):
    service = ServiceManager.get_instance()
    service.scheduler.remove_job(job_id)
    return {"success": True, "job_id": job_id}


@app.post("/api/automation/scheduler/jobs/{job_id}/toggle")
def toggle_scheduled_job(job_id: str):
    service = ServiceManager.get_instance()
    service.scheduler.toggle_job(job_id)
    return {"success": True, "job_id": job_id}


# =========================================================
# SECTION 4: EDUCATIONAL SIMULATIONS
# =========================================================

@app.post("/api/simulations/scheduling")
def run_cpu_scheduling(req: SchedulingSimulationRequest):
    try:
        return scheduling.simulate_cpu_scheduling(
            algorithm=req.algorithm,
            processes=req.processes,
            time_quantum=req.time_quantum,
            mlfq_config=req.mlfq_config,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulations/synchronization/race")
def run_race_condition(req: RaceConditionRequest):
    return synchronization.simulate_race_condition(
        iterations=req.iterations,
        threads_count=req.threads_count,
        use_mutex=req.use_mutex,
    )


@app.post("/api/simulations/synchronization/peterson")
def run_peterson():
    return synchronization.simulate_petersons_algorithm()


@app.post("/api/simulations/synchronization/producer-consumer")
def run_producer_consumer(capacity: int = 5, events: int = 12):
    return synchronization.simulate_producer_consumer(
        buffer_capacity=capacity, events_count=events
    )


@app.post("/api/simulations/synchronization/dining-philosophers")
def run_dining_philosophers(strategy: str = "asymmetric"):
    return synchronization.simulate_dining_philosophers(strategy=strategy)


@app.post("/api/simulations/synchronization/readers-writers")
def run_readers_writers(events: int = 8):
    return synchronization.simulate_readers_writers(events_count=events)


@app.post("/api/simulations/deadlock/coffman")
def run_coffman(
    mutual_exclusion: bool = True,
    hold_and_wait: bool = True,
    no_preemption: bool = True,
    circular_wait: bool = True,
):
    return deadlock.analyze_coffman_conditions(
        mutual_exclusion=mutual_exclusion,
        hold_and_wait=hold_and_wait,
        no_preemption=no_preemption,
        circular_wait=circular_wait,
    )


@app.post("/api/simulations/deadlock/rag")
def run_rag(data: Dict[str, Any] = Body(...)):
    return deadlock.analyze_rag(
        processes=data.get("processes", ["P1", "P2"]),
        resources=data.get("resources", {"R1": 1, "R2": 1}),
        allocations=data.get("allocations", []),
        requests=data.get("requests", []),
    )


@app.post("/api/simulations/deadlock/bankers/safety")
def run_bankers_safety(req: BankersSafetyRequest):
    try:
        return deadlock.bankers_safety_algorithm(
            available=req.available,
            allocation=req.allocation,
            max_matrix=req.max_matrix,
            process_names=req.process_names,
            resource_names=req.resource_names,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulations/deadlock/bankers/request")
def run_bankers_request(req: BankersResourceRequest):
    try:
        return deadlock.bankers_resource_request(
            available=req.available,
            allocation=req.allocation,
            max_matrix=req.max_matrix,
            process_index=req.process_index,
            request=req.request,
            process_names=req.process_names,
            resource_names=req.resource_names,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulations/memory/allocation")
def run_memory_allocation(req: MemoryAllocationRequest):
    try:
        return memory.simulate_contiguous_allocation(
            algorithm=req.algorithm,
            blocks=req.blocks,
            processes=req.processes,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulations/memory/paging")
def run_paging(
    logical_address: int = Query(..., ge=0),
    page_size: int = Query(1024, ge=1),
):
    return memory.translate_paging_address(
        logical_address=logical_address, page_size=page_size
    )


@app.post("/api/simulations/memory/segmentation")
def run_segmentation(
    segment_number: int = Query(..., ge=0),
    offset: int = Query(..., ge=0),
):
    return memory.translate_segmentation_address(
        segment_number=segment_number, offset=offset
    )


@app.post("/api/simulations/memory/page-replacement")
def run_page_replacement(req: PageReplacementRequest):
    try:
        return memory.simulate_page_replacement(
            algorithm=req.algorithm,
            reference_string=req.reference_string,
            frame_count=req.frame_count,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulations/memory/buddy")
def run_buddy(total_memory: int = 1024):
    return memory.simulate_buddy_allocation(total_memory=total_memory)


@app.post("/api/simulations/disk/schedule")
def run_disk_schedule(req: DiskSchedulingRequest):
    try:
        return disk.simulate_disk_scheduling(
            algorithm=req.algorithm,
            requests=req.requests,
            initial_head=req.initial_head,
            disk_size=req.disk_size,
            direction=req.direction,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulations/disk/compare")
def compare_disk(req: DiskSchedulingRequest):
    return disk.compare_all_disk_algorithms(
        requests=req.requests,
        initial_head=req.initial_head,
        disk_size=req.disk_size,
        direction=req.direction,
    )


@app.post("/api/simulations/filesys/allocation")
def run_file_allocation(method: str = "CONTIGUOUS", total_blocks: int = 32):
    return filesys.simulate_file_allocation(
        method=method, total_blocks=total_blocks
    )


@app.get("/api/simulations/filesys/freespace")
def run_freespace(total_blocks: int = 16):
    return filesys.simulate_free_space_management(total_blocks=total_blocks)


@app.get("/api/simulations/filesys/buffering")
def run_buffering(model: str = "DOUBLE"):
    return filesys.simulate_io_buffering(model=model)


# =========================================================
# SECTION 5: GAMIFICATION & ACADEMY
# =========================================================

@app.get("/api/academy/units")
def get_syllabus_units():
    return academy.SYLLABUS_UNITS


@app.get("/api/academy/missions")
def get_missions():
    return academy.MISSIONS_CATALOG


@app.get("/api/academy/badges")
def get_badges():
    return academy.BADGES_CATALOG


@app.get("/api/academy/quiz/{unit_id}")
def get_unit_quiz(unit_id: str):
    quiz = academy.KNOWLEDGE_CHECKS.get(unit_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found for unit")
    # Mask correct answers when presenting quiz
    masked = [
        {
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
        }
        for q in quiz
    ]
    return masked


@app.post("/api/academy/quiz/{unit_id}/submit")
def submit_unit_quiz(unit_id: str, req: QuizSubmissionRequest):
    quiz = academy.KNOWLEDGE_CHECKS.get(unit_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found for unit")

    total_questions = len(quiz)
    correct_count = 0
    feedback = []

    for q in quiz:
        qid = q["id"]
        chosen = req.answers.get(qid)
        is_correct = (chosen == q["correct_index"])
        if is_correct:
            correct_count += 1
        feedback.append({
            "id": qid,
            "question": q["question"],
            "chosen_index": chosen,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    score_pct = round((correct_count / total_questions * 100) if total_questions > 0 else 0, 1)

    # Award XP if passed (>= 50%)
    xp_awarded = 0
    if score_pct >= 50:
        xp = int(score_pct)  # Up to 100 XP
        res = db.award_xp(
            activity_id=f"quiz_{unit_id}",
            activity_type="quiz",
            unit_id=unit_id,
            title=f"Passed {unit_id.upper()} Knowledge Check ({score_pct}%)",
            xp=xp,
            details=f"Score: {correct_count}/{total_questions}",
        )
        xp_awarded = res["xp_awarded"]

    return {
        "unit_id": unit_id,
        "score_percent": score_pct,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "passed": score_pct >= 50,
        "xp_awarded": xp_awarded,
        "feedback": feedback,
    }


@app.get("/api/gamification/profile")
def get_profile():
    return db.get_or_create_profile()


@app.get("/api/gamification/progress")
def get_progress():
    return db.get_user_progress()


@app.post("/api/gamification/award-xp")
def award_xp_endpoint(req: AwardXpRequest):
    res = db.award_xp(
        activity_id=req.activity_id,
        activity_type=req.activity_type,
        unit_id=req.unit_id,
        title=req.title,
        xp=req.xp,
        details=req.details or "",
    )
    return res


@app.post("/api/gamification/reset")
def reset_gamification():
    db.reset_gamification()
    return {"success": True, "message": "Gamification progress reset successfully."}


# =========================================================
# SECTION 6: WEBSOCKET LIVE TELEMETRY
# =========================================================

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    service = ServiceManager.get_instance()
    try:
        while True:
            sample = service.monitor.get_snapshot()
            if sample:
                score, label = calculate_health_score(sample)
                data = {
                    "sample": sample,
                    "health_score": score,
                    "health_label": label,
                    "human_uptime": human_uptime(sample.get("uptime", 0)),
                }
                await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
