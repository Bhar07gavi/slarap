SLARAP — Smart Linux Automation & Resource Analytics Platform

SLARAP is a web-based Linux administration and Operating Systems learning platform. It combines Linux system-resource monitoring and supported system operations with interactive simulations that help students understand core Operating System (OS) concepts.

The project brings practical Linux operations and visual demonstrations of OS algorithms into one interface.


Features

1. Dashboard

Summary of CPU utilization, memory utilization, disk usage, and active-process count.

CPU and RAM telemetry visualization.

Active-process information and system-health/alert information.

2. Live Monitoring

Per-core CPU utilization and CPU utilization history.

RAM and swap utilization.

Network input/output traffic.

Storage-partition utilization.

3. Process Manager

Inspect running-process information and resource usage.

Access the process-related operations supported by the application.

Explore process identification and process-control concepts.

4. Automation & Linux Command Playground

Execute supported Linux commands in the configured WSL2 Ubuntu environment.

Explore pipe-based Inter-Process Communication (IPC).

Access background-job and workflow features provided by the application.

The command playground describes Linux operations involving concepts such as fork(), execvp(), waitpid(), and pipes. The exact operations available depend on the running application and its configuration.

5. Interactive OS Labs

SLARAP includes learning modules for key Operating System topics:

OS Overview: OS responsibilities, kernel architecture, user space, kernel space, and Linux system information.

-Process & CPU Scheduling: FCFS, SJF, SRTF, Priority Scheduling, Round Robin, and Multilevel Feedback Queue (MLFQ), with scheduling timelines and Gantt charts.

-Synchronization & Deadlocks: Process-synchronization concepts, deadlocks, and deadlock avoidance using the Banker’s algorithm.

— Memory Management: Contiguous allocation, paging, segmentation, address translation, page replacement, and buddy allocation.

— File & I/O Management: Disk scheduling, file allocation, free-space management, and I/O buffering.

— Linux Kernel & Android OS: Learning material related to the Linux kernel, system calls, and Android architecture.

Note: OS Labs are educational simulations. They demonstrate algorithm behaviour and do not replace or modify the Linux kernel's actual scheduling or memory-management policies.

Technology Stack

->Component

->Technology

->Purpose

->Frontend

->React, TypeScript

->Interactive user interface

->Frontend tooling

->Vite, Node.js, npm

->Development server, build tooling, and package management

->Backend

->Python, FastAPI

->API endpoints and application logic

->Data storage

->SQLite

->Supported persistent application data

->Operating environment

->Ubuntu on WSL2

->Linux commands and supported Linux system operations

System Architecture

                    USER
                     |
                     v
          React + TypeScript Frontend
                     |
             HTTP API Requests
                     |
                     v
                FastAPI API
                     |
                     v
             Python Backend Modules
             /         |           \
            v          v            v
     System Metrics  OS Labs    Automation /
     & Processes   Simulations   Analytics
            |          |            |
            +----------+------------+
                       |
             +---------+---------+
             |                   |
             v                   v
       SQLite Database     Ubuntu / WSL2
       Supported data      Linux metrics and
                           supported operations
                       |
                       v
              Results returned to UI

The frontend sends requests to FastAPI endpoints when backend processing is required. The Python backend routes requests to the appropriate functionality and returns results for display in the frontend. SQLite stores supported application data that needs persistence, while the Linux environment provides system information and executes supported Linux operations.

->Requirements

Before running SLARAP, ensure that you have:

Windows with WSL2 and an Ubuntu distribution.

The project files available in the configured Windows and WSL2 directories.

Python and the backend dependencies installed in the configured virtual environment.

Node.js and npm installed on Windows.

Git, if cloning the repository.

The commands below use the project paths configured for this setup:

WSL2 project directory: /home/asus/slarap_project

Python virtual environment: /home/asus/.venvs/slarap

Windows frontend directory: D:\Projects\OS\slarap\web

If your project is stored elsewhere, update the paths before running the commands.

->How to Run the Application

SLARAP uses a FastAPI backend running in WSL2 Ubuntu and a React frontend running on Windows. Start the backend first, then start the frontend in a separate terminal.

Step 1: Start the Backend (WSL2 Ubuntu)

->Open PowerShell and run:

wsl -d Ubuntu -e bash -lc "cd /home/asus/slarap_project && /home/asus/.venvs/slarap/bin/python -m uvicorn backend.api.app:app --host 0.0.0.0 --port 8000"

->Keep this terminal open while using the application.

When the server starts, the backend endpoints are available at:

API server: http://127.0.0.1:8000

Swagger API documentation: http://127.0.0.1:8000/docs

The Swagger page allows you to inspect and try the API endpoints exposed by the running backend.

Step 2: Start the Frontend (Windows)

Open a second PowerShell terminal and run:

cd D:\Projects\OS\slarap\web
npm run dev

Wait for Vite to display the local development address. The default address is usually:

Frontend: http://localhost:5173

If the frontend dependencies have not been installed yet, run npm install inside the web directory before npm run dev.

Step 3: Open and Use SLARAP

Open http://localhost:5173 in your browser after both servers are running.

You can then explore the dashboard, live monitoring, process management, automation features, and OS Labs.

Troubleshooting

Frontend API/proxy connection errors: Check that the backend is running on port 8000 and that the frontend's API/proxy configuration points to the correct backend address.

Backend command fails: Confirm that /home/asus/slarap_project exists in WSL2 and that /home/asus/.venvs/slarap/bin/python is available.

Missing frontend packages: Run npm install from D:\Projects\OS\slarap\web.

Port already in use: Stop the process using the required port or configure the application to use an available port and update the corresponding frontend API/proxy settings.

Testing

The project includes tests for supported backend functionality and OS algorithm logic. To run a Python test suite, activate the project's Python environment in WSL2 and run the following from the project directory:

cd /home/asus/slarap_project
/home/asus/.venvs/slarap/bin/python -m pytest

Test results can change as the code changes. Run the tests against the current version before reporting a pass count.

Example Linux Commands

If supported by the command playground, these commands can be used to inspect system information:

uname -a
free -h
df -h
ps -eo pid,comm | head -10

uname -a displays system and kernel information.

free -h displays memory usage.

df -h displays filesystem space usage.

ps -eo pid,comm | head -10 displays a short list of process IDs and command names using a pipe.

Only execute commands supported and permitted by the configured environment. Avoid destructive commands or commands that change system configuration during demonstrations.

Project Structure

The main project files and directories include:

slarap/
├── backend/        # Python backend and API
├── web/            # React + TypeScript frontend
├── tests/           # Automated tests, if included
├── requirements.txt # Python dependencies
└── README.md        # Project documentation

Additional folders may be present for simulation modules, data, exports, workflows, and application configuration.

->OS Concepts Covered

SLARAP supports practical learning and demonstrations related to:

Operating System functions and kernel architecture.

Process states, PIDs, process control, and CPU scheduling.

Process synchronization, IPC, deadlocks, and Banker’s algorithm.

Memory allocation, fragmentation, paging, segmentation, and page replacement.

File allocation, free-space management, disk scheduling, and I/O buffering.

Linux commands, system calls, and Linux/Android architecture concepts.

System resource monitoring and automation.

->Limitations

The Linux operations available depend on the host environment, user permissions, and the functionality implemented in the application.

Live metrics reflect the environment in which the backend runs. Under WSL2, the metrics may describe the Linux environment rather than the complete Windows host.

OS Labs are simulations and do not change the host operating system’s internal scheduler or memory-management policies.

The exact automation, alert, and process-management operations depend on the current application configuration.

->Future Enhancements

Potential improvements include:

Additional resource metrics and historical analytics.

More interactive OS algorithm demonstrations.

Expanded workflow scheduling and alert configuration.

Improved error handling, input validation, and automated testing.

Deployment support for additional Linux environments.
