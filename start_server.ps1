Write-Host "Starting AICSA Pro Server..." -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$packages = @("fastapi", "uvicorn", "openai", "sqlalchemy", "pydantic")
foreach ($pkg in $packages) {
    try {
        python -c "import $pkg" 2>$null
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $pkg - installing..." -ForegroundColor Red
        pip install $pkg
    }
}

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
python -c "from infrastructure.database import init_db; init_db(); print('Database initialized')"

# Start the server
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Server will be available at: https://aicsa.org.za" -ForegroundColor Cyan
Write-Host "API Documentation: https://aicsa.org.za/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

uvicorn main:app --reload --host 0.0.0.0 --port 8000