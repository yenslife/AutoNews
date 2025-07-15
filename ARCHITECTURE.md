# Project Architecture Plan: Monorepo with Independent Services

This document outlines a future architecture for the `AutoNews` project, transitioning it into a monorepo that houses multiple independent services. This approach allows for centralized code management while maintaining clear separation between the different parts of the application.

## 1. Core Philosophy

The project will be structured as a **Monorepo**, containing two primary, independent applications:

1.  **`AutoNews`**: The main application, structured as a standard Python package (`src` layout).
2.  **`Whisper Service`**: A self-contained microservice for audio transcription, with its own dependencies and runtime environment.

Each application will manage its own dependencies using a dedicated `pyproject.toml` file and the `uv` toolchain, ensuring complete isolation and reproducibility.

## 2. Proposed Directory Structure

```
/
├── whisper_service/            # Project A: Whisper Service (Microservice)
│   ├── pyproject.toml          # Manages dependencies for the Whisper service
│   ├── uv.lock                 # Lock file for the Whisper service
│   ├── Dockerfile              # Defines how to build the service container
│   └── app/                    # Source code for the service (FastAPI, Celery)
│       ├── main.py
│       └── tasks.py
│
├── src/                        # Project B: AutoNews (Main Application)
│   ├── api/
│   └── main.py
│
├── pyproject.toml              # Manages dependencies for the AutoNews application
├── uv.lock                     # Lock file for the AutoNews application
├── docker-compose.yml          # (Optional) Orchestrates all services for local development
└── .gitignore
```

## 3. Dependency Management

We will **not** use `requirements.txt`. Each service is a first-class citizen with its own `pyproject.toml`.

### `whisper_service/pyproject.toml` Example

This file defines all dependencies required by the Whisper service, completely separate from the main application.

```toml
[project]
name = "whisper-service"
version = "0.1.0"
description = "A FastAPI and Celery service for Whisper inference."
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "celery",
    "redis",
    "openai-whisper",
    "pydantic-settings",
]

[tool.uv]
# Workspace configuration for uv can be defined here if needed
```

## 4. Containerization with Docker

The `whisper_service` is designed to be run as a Docker container. Its `Dockerfile` will use `uv` to install dependencies from its own `pyproject.toml`.

### `whisper_service/Dockerfile` Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv, the project manager and installer
RUN pip install uv

# Copy only the dependency definition files first to leverage Docker's cache
COPY pyproject.toml uv.lock* ./

# Install dependencies into the system's Python environment
# This is a common and clean practice for containers.
RUN uv pip install --system .

# Copy the application source code
COPY ./app/ .

# The command to run the service (e.g., uvicorn or celery)
# will be specified in the docker-compose.yml file.
# Example: CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## 5. Orchestration

A `docker-compose.yml` file in the root directory can be used to define and run the multi-container application stack (e.g., `whisper_api`, `whisper_worker`, `redis`). This makes it simple to spin up the entire development environment with a single command.
