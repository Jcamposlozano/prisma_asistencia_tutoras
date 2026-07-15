from __future__ import annotations
import os
import uvicorn
from student_service.shared.config import load_config

def main():
    cfg = load_config()
    uvicorn.run("student_service.entrypoints.api:app",
                host=cfg["service"]["host"],
                port=cfg["service"]["port"],
                reload=(os.getenv("ENV","dev")=="dev"))

if __name__ == "__main__":
    main()
