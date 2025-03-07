@echo off
echo Setting up environment for building Sudoku executable (PyInstaller Method)...

:: Create a temporary directory for building
if exist build_temp rmdir /s /q build_temp
mkdir build_temp
cd build_temp

:: Create a virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies with specific versions for compatibility
echo Installing dependencies...
pip install Flask==2.0.1 Flask-SQLAlchemy==2.5.1 Werkzeug==2.0.1 requests==2.26.0
pip install pyinstaller==6.12.0

:: Copy necessary files
echo Copying necessary files...
copy ..\app.py .
copy ..\backend.py .
copy ..\frontend.py .
copy ..\database.py .
copy ..\sudoku_logic.py .

:: Create a compatible spec file
echo Creating spec file...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis(
echo     ['app.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=['flask', 'flask_sqlalchemy', 'werkzeug', 'sqlalchemy', 'sqlalchemy.sql.default_comparator', 'tkinter', 'tkinter.messagebox', 'json', 'threading', 'requests', 'sqlite3', 'datetime', 'random'],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo )
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='Sudoku',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo )
) > sudoku_build.spec

:: Build the executable
echo Building executable...
pyinstaller --clean sudoku_build.spec

:: Copy the executable to the parent directory
echo Copying executable to main directory...
copy dist\Sudoku.exe ..\Sudoku_PyInstaller.exe

:: Clean up if the build was successful
if exist ..\Sudoku_PyInstaller.exe (
  echo Cleaning up...
  cd ..
  rmdir /s /q build_temp
  echo Build complete! Sudoku_PyInstaller.exe has been created.
) else (
  cd ..
  echo Build failed! Executable was not created.
)

pause 