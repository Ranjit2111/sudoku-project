import os
import subprocess
import shutil
import sys

def build_executable():
    # Ensure all dependencies are installed
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Clean previous build directories
    print("Cleaning previous builds...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Build with PyInstaller
    print("Building executable with PyInstaller...")
    subprocess.run(["pyinstaller", "sudoku.spec"], check=True)
    
    print("\nBuild completed successfully!")
    print("Your executable is located in the 'dist' folder.")

if __name__ == "__main__":
    build_executable()