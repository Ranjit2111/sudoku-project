@echo off
echo Sudoku Executable Builder for Python 3.12
echo ========================================
echo This script will attempt to build the Sudoku executable using three different methods.
echo At least one of them should work on your system.
echo.

echo Method 1: Standard PyInstaller
echo -----------------------------
call build_exe.bat
echo.

echo Method 2: Auto-Py-To-Exe
echo -----------------------
call build_exe_alt.bat
echo.

echo Method 3: Nuitka
echo --------------
call build_exe_nuitka.bat
echo.

echo All build methods completed!
echo Check for the following files:
echo - Sudoku_PyInstaller.exe (Standard PyInstaller)
echo - Sudoku_Auto.exe (Auto-Py-To-Exe)
echo - Sudoku_Nuitka.exe (Nuitka)
echo.
echo Use whichever executable works best on your system.
pause 