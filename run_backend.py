"""
GramNirnay.ai — Backend Launcher Script
"""
import sys
import os
from pathlib import Path

# Ensure local backend directory has absolute top precedence
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"

# Ensure local root directory is in path
sys.path.insert(0, str(BASE_DIR))

import backend.main as main
import uvicorn

if __name__ == "__main__":
    # Render provides the PORT environment variable; default to 8000 for local dev
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print("==================================================")
    print(f"   GramNirnay.ai Backend Starting on {host}:{port}   ")
    print(f"   Loaded App: {main.app.title}")
    print(f"   Routes: {[r.path for r in main.app.routes]}")
    print(f"   API Docs available at: http://{host}:{port}/docs")
    print("==================================================")

    uvicorn.run(
        main.app,
        host=host,
        port=port,
        log_level="info",
    )
