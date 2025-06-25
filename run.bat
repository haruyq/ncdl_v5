@echo off

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2 delims= " %%a in ('python -V 2^>^&1') do set "PYTHON_VER=%%a"
    
    echo %PYTHON_VER% | findstr "^3" >nul
    if %ERRORLEVEL% EQU 0 (
        python main.py
        goto END
    )
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python3 main.py
    goto END
)

exit /b 1

:END