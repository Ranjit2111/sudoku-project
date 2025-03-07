@echo off
echo Creating Sudoku Game Distribution Package...

:: Create distribution directory
mkdir SudokuGame
echo Created distribution directory: SudokuGame

:: Copy Python files
copy app.py SudokuGame\
copy backend.py SudokuGame\
copy frontend.py SudokuGame\
copy database.py SudokuGame\
copy sudoku_logic.py SudokuGame\
copy requirements.txt SudokuGame\
copy run_sudoku.bat SudokuGame\
copy README.md SudokuGame\
echo Copied Python files and documentation

echo Distribution package created successfully!
echo The package is ready in the SudokuGame folder.
pause 