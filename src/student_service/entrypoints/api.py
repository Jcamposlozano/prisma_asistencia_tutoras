from __future__ import annotations
from fastapi import FastAPI
from student_service.shared.config import load_config

cfg = load_config()
SERVICE_NAME = cfg.get("project", {}).get("name", "student-service")
app = FastAPI(title=SERVICE_NAME, version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}
