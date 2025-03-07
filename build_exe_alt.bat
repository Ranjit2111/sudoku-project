@echo off
echo Setting up environment for building Sudoku executable (Auto-Py-To-Exe Method)...

:: Create a temporary directory for building
if exist build_temp_alt rmdir /s /q build_temp_alt
mkdir build_temp_alt
cd build_temp_alt

:: Create a virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies with specific versions for compatibility
echo Installing dependencies...
pip install Flask==2.0.1 Flask-SQLAlchemy==2.5.1 Werkzeug==2.0.1 requests==2.26.0
pip install pyinstaller==6.12.0
pip install auto-py-to-exe

:: Copy necessary files
echo Copying necessary files...
copy ..\app.py .
copy ..\backend.py .
copy ..\frontend.py .
copy ..\database.py .
copy ..\sudoku_logic.py .

:: Create configuration for auto-py-to-exe
echo Creating auto-py-to-exe configuration...
(
echo {
echo     "version": "auto-py-to-exe-configuration_v1",
echo     "pyinstallerOptions": [
echo         {
echo             "optionDest": "noconfirm",
echo             "value": true
echo         },
echo         {
echo             "optionDest": "filenames",
echo             "value": "app.py"
echo         },
echo         {
echo             "optionDest": "onefile",
echo             "value": true
echo         },
echo         {
echo             "optionDest": "console",
echo             "value": false
echo         },
echo         {
echo             "optionDest": "name",
echo             "value": "Sudoku"
echo         },
echo         {
echo             "optionDest": "clean_build",
echo             "value": true
echo         },
echo         {
echo             "optionDest": "hiddenimports",
echo             "value": "flask, flask_sqlalchemy, werkzeug, sqlalchemy, sqlalchemy.sql.default_comparator, tkinter, tkinter.messagebox, json, threading, requests, sqlite3, datetime, random"
echo         }
echo     ],
echo     "nonPyinstallerOptions": {
echo         "increaseRecursionLimit": true,
echo         "manualArguments": ""
echo     }
echo }
) > config.json

:: Build using auto-py-to-exe
echo Building executable with auto-py-to-exe...
python -m auto_py_to_exe --config config.json

:: Copy the executable to the parent directory
echo Copying executable to main directory...
if exist output\Sudoku.exe (
  copy output\Sudoku.exe ..\Sudoku_Auto.exe
  echo Build complete! Sudoku_Auto.exe has been created.
) else (
  echo Build failed! Executable was not created.
)

:: Clean up if the build was successful
if exist ..\Sudoku_Auto.exe (
  echo Cleaning up...
  cd ..
  rmdir /s /q build_temp_alt
) else (
  cd ..
)

pause 