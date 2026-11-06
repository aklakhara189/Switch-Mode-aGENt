"""Application startup script."""

import uvicorn
import os

if __name__ == "__main__":
    print("=" * 60)
    print("Starting AI Bug Triage & Resolution Server...")
    print("Interactive Swagger Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
