#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path


def main():
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print("Backend directory not found")
        sys.exit(1)
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    print("Starting BDA Analytics API...")
    print(f"Working directory: {backend_dir}")
    print(f"Command: {' '.join(cmd)}")
    
    subprocess.run(cmd, cwd=backend_dir)


if __name__ == "__main__":
    main()
