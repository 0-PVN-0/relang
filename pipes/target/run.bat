@echo off
setlocal enabledelayedexpansion

set DIR=%~dp0
set OUT=%DIR%out
set LIB=%DIR%lib

if not exist "%OUT%" (
    echo Build directory not found. Run build.bat first.
    exit /b 1
)

set CP=%OUT%
if exist "%LIB%\jna-5.14.0.jar" set CP=%CP%;%LIB%\jna-5.14.0.jar
if exist "%LIB%\jna-platform-5.14.0.jar" set CP=%CP%;%LIB%\jna-platform-5.14.0.jar

java -cp "%CP%" pipes.Pipes %*
endlocal
