@echo off
echo Setting up environment for building Sudoku executable (Nuitka Method)...

:: Create a temporary directory for building
if exist build_temp_nuitka rmdir /s /q build_temp_nuitka
mkdir build_temp_nuitka
cd build_temp_nuitka

:: Create a virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies with specific versions for compatibility
echo Installing dependencies...
pip install Flask==2.0.1 Flask-SQLAlchemy==2.5.1 Werkzeug==2.0.1 requests==2.26.0
:: Latest Nuitka version should work with Python 3.12
pip install nuitka

:: Copy necessary files
echo Copying necessary files...
copy ..\app.py .
copy ..\backend.py .
copy ..\frontend.py .
copy ..\database.py .
copy ..\sudoku_logic.py .

:: Build using Nuitka
echo Building executable with Nuitka...
python -m nuitka --standalone --windows-disable-console ^
  --include-package=flask ^
  --include-package=flask_sqlalchemy ^
  --include-package=werkzeug ^
  --include-package=sqlalchemy ^
  --include-package=tkinter ^
  --include-package=requests ^
  --include-package=sqlite3 ^
  --enable-plugin=tk-inter ^
  --follow-imports ^
  app.py

:: Copy the executable to the parent directory
echo Checking for executable...
if exist app.dist\app.exe (
  echo Copying executable to main directory...
  copy app.dist\app.exe ..\Sudoku_Nuitka.exe
  echo Build complete! Sudoku_Nuitka.exe has been created.
) else (
  echo Build failed! Executable was not created.
)

:: Clean up if the build was successful
if exist ..\Sudoku_Nuitka.exe (
  echo Cleaning up...
  cd ..
  rmdir /s /q build_temp_nuitka
) else (
  cd ..
)

pause 