@echo off
echo Adding Python to PATH...

:: Try different possible Python installation locations
set PYTHON_PATHS=^
C:\Users\User\AppData\Local\Programs\Python\Python39;^
C:\Users\User\AppData\Local\Programs\Python\Python39\Scripts;^
C:\Program Files\Python39;^
C:\Program Files\Python39\Scripts;^
C:\Python39;^
C:\Python39\Scripts

:: Add to PATH
setx PATH "%PATH%;%PYTHON_PATHS%"

echo.
echo Python paths have been added to your system PATH.
echo Please restart your command prompt or IDE to apply changes.
echo.

pause
