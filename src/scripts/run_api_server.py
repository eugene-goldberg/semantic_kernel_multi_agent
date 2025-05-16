#!/usr/bin/env python3
import os
import subprocess
import sys

def run_api_server():
    """Run the API server using uvicorn"""
    # Get the root directory of the project
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    
    # Add the root directory to the Python path
    sys.path.insert(0, root_dir)
    
    # Run the API server
    from src.api.server import app
    import uvicorn
    
    print("Starting API server at http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_api_server()