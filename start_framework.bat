@echo off
title AI Test Automation Framework
color 0A

echo.
echo ================================================
echo   AI Test Automation Framework
echo   Powered by Ollama + Selenium + Playwright
echo ================================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run: py -3.13 -m venv venv
    echo Then run: venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama does not appear to be running.
    echo Please open a separate terminal and run: ollama serve
    echo The framework will still launch but LLM calls will fail
    echo until Ollama is running.
    echo.
    pause
)

:: Create outputs directory if it doesn't exist
if not exist "outputs" mkdir outputs

:: Ask user what to launch
echo.
echo What would you like to launch?
echo   1. Streamlit UI  ^(recommended^)
echo   2. FastAPI only
echo   3. Both Streamlit UI and FastAPI
echo.
set /p choice="Enter 1, 2, or 3: "

if "%choice%"=="1" goto launch_streamlit
if "%choice%"=="2" goto launch_api
if "%choice%"=="3" goto launch_both

echo Invalid choice. Launching Streamlit UI by default.
goto launch_streamlit

:launch_streamlit
echo.
echo Starting Streamlit UI...
echo Open your browser at: http://localhost:8501
echo.
streamlit run ui/app.py --server.port=8501
goto end

:launch_api
echo.
echo Starting FastAPI...
echo API docs available at: http://localhost:8000/docs
echo.
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
goto end

:launch_both
echo.
echo Starting FastAPI in background...
start "FastAPI" cmd /k "uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
echo.
echo Starting Streamlit UI...
echo Open your browser at: http://localhost:8501
echo API docs available at: http://localhost:8000/docs
echo.
streamlit run ui/app.py --server.port=8501
goto end

:end
echo.
echo Framework stopped.
pause