@echo off
set "PATH=%~dp0;%PATH%"
doskey relang=python "%~dp0relang-submit.py" $*
echo Ready. Use relang ^<args^> to run relang-submit.py from anywhere.
