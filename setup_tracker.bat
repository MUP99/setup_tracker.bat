@echo off
python -m pip install --upgrade pip
pip install pyinstaller pyqt5 opencv-python numpy pyautogui pynput pyscreeze
pyinstaller --onefile --windowed --name BO6_AimAssist bo6_tracker_final.py
pause
