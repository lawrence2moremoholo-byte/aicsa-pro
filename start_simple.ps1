Write-Host "Starting Simple AICSA Pro Server..." -ForegroundColor Green
.\venv\Scripts\Activate
uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000