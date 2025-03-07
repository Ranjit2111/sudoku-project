# app.py
import threading
import time
import os
import requests
import sys
from backend import run_backend
from frontend import run_frontend
import atexit
import signal

def start_backend():
    global backend_thread  # Make it global so we can access it for cleanup
    
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait for the backend to start with a timeout
    start_time = time.time()
    max_wait = 10  # Maximum wait time in seconds
    
    while time.time() - start_time < max_wait:
        try:
            # Try to connect to the backend
            response = requests.get("http://localhost:5000", timeout=1)
            if response.status_code == 200:
                print("Backend server started successfully")
                return True
        except requests.exceptions.ConnectionError:
            # Check if database file exists (a sign that the backend is running)
            if os.path.exists('sudoku.db') or os.path.exists('instance/sudoku.db'):
                print("Backend appears to be starting...")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error checking backend: {e}")
            time.sleep(0.5)
    
    print("Warning: Backend might not have started properly.")
    return False

if __name__ == "__main__":
    print("Starting Sudoku application...")
    if start_backend():
        print("Starting frontend...")
        run_frontend()
    else:
        print("Application failed to start properly.")
        sys.exit(1)
