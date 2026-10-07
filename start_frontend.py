#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path


def main():
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("Frontend directory not found")
        sys.exit(1)
    
    cmd = ["npm", "run", "dev"]
    
    print("Starting BDA Analytics Frontend...")
    print(f"Working directory: {frontend_dir}")
    print(f"Command: {' '.join(cmd)}")
    
    subprocess.run(cmd, cwd=frontend_dir, shell=True)


if __name__ == "__main__":
    main()
