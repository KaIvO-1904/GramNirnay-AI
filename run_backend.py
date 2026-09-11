"""
GramNirnay.ai — Backend Launcher Script
"""
import sys
import os
from pathlib import Path

# Ensure local backend directory has absolute top precedence
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BASE_DIR))

import main
import uvicorn

if __name__ == "__main__":
    print("==================================================")
    print("   GramNirnay.ai Backend Starting on Port 8000    ")
    print(f"   Loaded App: {main.app.title}")
    print(f"   Routes: {[r.path for r in main.app.routes]}")
    print("   API Docs available at: http://127.0.0.1:8000/docs")
    print("==================================================")
    uvicorn.run(
        main.app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
