@echo off
set "SCRIPT_DIR=%~dp0"
setx PATH "%SCRIPT_DIR%;%PATH%"
echo.
echo Installed. Open a new Command Prompt to use 'relang'.
echo Or run: refreshenv  (if available)
echo.
echo Usage: relang ^<your-program-command^>
