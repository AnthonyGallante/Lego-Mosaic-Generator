@echo off
echo Lego Mosaic Generator - One-Click Installation

echo 1. Installing required Python packages...
pip install -r requirements.txt
pip install pyinstaller

echo 2. Building executable...
python build_executable.py

echo Installation complete! You can find the executable in the Lego_Mosaic_Generator_Release folder.
echo Press any key to exit.
pause 