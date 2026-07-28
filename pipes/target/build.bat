@echo off
setlocal enabledelayedexpansion
set DIR=%~dp0
set SRC=%DIR%src
set OUT=%DIR%out
set LIB=%DIR%lib

if not exist "%OUT%" mkdir "%OUT%"
if not exist "%LIB%" mkdir "%LIB%"

set JNA_VER=5.14.0
set JNA_JAR=%LIB%\jna-%JNA_VER%.jar
set JNA_PLATFORM_JAR=%LIB%\jna-platform-%JNA_VER%.jar

if not exist "%JNA_JAR%" (
    echo Downloading JNA core library...
    powershell -Command "try { $wc = New-Object System.Net.WebClient; $wc.DownloadFile('https://repo1.maven.org/maven2/net/java/dev/jna/jna/%JNA_VER%/jna-%JNA_VER%.jar', '%JNA_JAR%') } catch { exit 1 }"
    if !ERRORLEVEL! neq 0 (
        echo Warning: Could not download JNA. Building without JNA support.
        echo Raw keyboard input may not work on Windows.
        set JNA_JAR=
        set JNA_PLATFORM_JAR=
    ) else (
        echo Downloading JNA platform library...
        powershell -Command "try { $wc = New-Object System.Net.WebClient; $wc.DownloadFile('https://repo1.maven.org/maven2/net/java/dev/jna/jna-platform/%JNA_VER%/jna-platform-%JNA_VER%.jar', '%JNA_PLATFORM_JAR%') } catch { exit 1 }"
        if !ERRORLEVEL! neq 0 (
            echo Warning: Could not download JNA platform. Building without JNA support.
            set JNA_PLATFORM_JAR=
        )
    )
)

dir /s /B "%SRC%\*.java" > "%DIR%sources.txt" 2>nul

set CP=%OUT%
if exist "%LIB%\jna-%JNA_VER%.jar" set CP=%CP%;%LIB%\jna-%JNA_VER%.jar
if exist "%LIB%\jna-platform-%JNA_VER%.jar" set CP=%CP%;%LIB%\jna-platform-%JNA_VER%.jar

javac -d "%OUT%" -cp "%CP%" @"%DIR%sources.txt"

if %ERRORLEVEL% equ 0 (
    echo Build successful.
    echo.
    echo To run: java -cp "%CP%" pipes.Pipes [options]
    echo.
    echo Examples:
    echo   java -cp "%CP%" pipes.Pipes -p 3 -f 60
    echo   java -cp "%CP%" pipes.Pipes -R -P 2
    echo   java -cp "%CP%" pipes.Pipes -p 3 -C -B
) else (
    echo Build failed.
)

if exist "%DIR%sources.txt" del "%DIR%sources.txt"
endlocal
