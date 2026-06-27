#!/usr/bin/env python3
"""
Build and run script for the Restaurant Operator Terminal
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        
        print(result.stdout)
        return True
        
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def main():
    """Main build and run process"""
    print("🏪 Restaurant Operator Terminal - Build & Run")
    print("=" * 50)
    
    # Get the app root directory (scripts/ lives under the app root)
    script_dir = Path(__file__).parent.parent
    frontend_dir = script_dir / "frontend"
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing npm dependencies...")
        if not run_command("npm install", cwd=frontend_dir):
            print("❌ Failed to install npm dependencies")
            return False
        print("✅ npm dependencies installed")
    
    # Build the frontend
    print("🔨 Building frontend...")
    if not run_command("npm run build", cwd=frontend_dir):
        print("❌ Failed to build frontend")
        return False
    
    print("✅ Frontend built successfully")
    
    # Check if dist directory was created
    dist_dir = frontend_dir / "dist"
    if not dist_dir.exists():
        print("❌ Build output (dist) directory not found!")
        return False
    
    # Change back to main directory
    os.chdir(script_dir)
    
    # Run the PyWebView application
    print("🚀 Starting Restaurant Operator Terminal...")
    try:
        subprocess.run([sys.executable, "main.py"], cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
