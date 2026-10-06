#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start all Inventory Management System services.

.DESCRIPTION
    Launches the API Gateway and all backend microservices.
    PostgreSQL must be running on localhost:5432 before running this script.

.USAGE
    .\start-all.ps1
#>

$ErrorActionPreference = "Continue"
$ROOT = $PSScriptRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Inventory Management System - Service Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# -- Load root .env
Write-Host "[1/7] Loading environment variables from .env..." -ForegroundColor Yellow
$envFile = Join-Path $ROOT ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#=\s][^=]*)=(.*)$") {
            $key   = $Matches[1].Trim()
            $value = $Matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "    [OK] Environment loaded." -ForegroundColor Green
} else {
    Write-Host "    [WARN] .env not found" -ForegroundColor Red
}

# -- Check Database
Write-Host "[2/7] Checking database configuration..." -ForegroundColor Yellow
$dbUrl = [System.Environment]::GetEnvironmentVariable("DATABASE_URL")
if ($dbUrl -match "^sqlite") {
    Write-Host "    [OK] Database mode: SQLite (no background database daemon needed)." -ForegroundColor Green
} else {
    $pgRunning = netstat -ano | Select-String ":5432\s" | Select-Object -First 1
    if (-not $pgRunning) {
        Write-Host "    [FAIL] PostgreSQL is NOT running on port 5432!" -ForegroundColor Red
        Write-Host "    To use SQLite instead, set DATABASE_URL=sqlite:///... in .env" -ForegroundColor Yellow
        Write-Host "    To start PostgreSQL service:" -ForegroundColor White
        Write-Host "      Start-Service postgresql*" -ForegroundColor White
        Read-Host "    Press ENTER to exit, or switch to SQLite in .env and retry"
        exit 1
    }
    Write-Host "    [OK] PostgreSQL is running on port 5432." -ForegroundColor Green
}

# -- Helper: Start service in new window
function Start-SvcWindow {
    param([string]$Name, [string]$ServiceDir, [string]$Port, [string]$Module)
    $venvExe = Join-Path (Join-Path $ROOT $ServiceDir) ".venv\Scripts\uvicorn.exe"
    if (-not (Test-Path $venvExe)) {
        Write-Host "    [WARN] No .venv in $ServiceDir - skipping $Name" -ForegroundColor DarkYellow
        return
    }
    $cmd = "`$env:PYTHONPATH='.'; `$env:PYTHONIOENCODING='utf-8'; & '$venvExe' $Module --port $Port --host 0.0.0.0; Read-Host 'Press ENTER'"
    Start-Process powershell -ArgumentList "-NoExit","-Command",$cmd -WorkingDirectory (Join-Path $ROOT $ServiceDir) -WindowStyle Normal
    Write-Host "    [OK] $Name starting on :$Port" -ForegroundColor Green
    Start-Sleep -Milliseconds 800
}

Write-Host "[3/7] Starting Auth Service (port 8001)..." -ForegroundColor Yellow
Start-SvcWindow -Name "Auth Service" -ServiceDir "backend\services\auth-service" -Port "8001" -Module "app.main:app"

Write-Host "[4/7] Starting Product Service (port 8003)..." -ForegroundColor Yellow
Start-SvcWindow -Name "Product Service" -ServiceDir "backend\services\product-service" -Port "8003" -Module "app.main:app"

Write-Host "[5/7] Starting Inventory Service (port 8004)..." -ForegroundColor Yellow
Start-SvcWindow -Name "Inventory Service" -ServiceDir "backend\services\inventory-service" -Port "8004" -Module "app.main:app"

Write-Host "[6/7] Starting Order Service (port 8005)..." -ForegroundColor Yellow
Start-SvcWindow -Name "Order Service" -ServiceDir "backend\services\order-service" -Port "8005" -Module "app.main:app"

Write-Host "[7/7] Starting API Gateway (port 8000)..." -ForegroundColor Yellow
$gwVenv = Join-Path $ROOT "backend\api-gateway\.venv\Scripts\uvicorn.exe"
if (Test-Path $gwVenv) {
    $gwCmd = "`$env:PYTHONPATH='.'; `$env:PYTHONIOENCODING='utf-8'; & '$gwVenv' app.main:app --port 8000 --host 0.0.0.0; Read-Host 'Press ENTER'"
    Start-Process powershell -ArgumentList "-NoExit","-Command",$gwCmd -WorkingDirectory (Join-Path $ROOT "backend\api-gateway") -WindowStyle Normal
    Write-Host "    [OK] API Gateway starting on :8000" -ForegroundColor Green
}

# -- Status
Write-Host ""
Write-Host "Waiting 6 seconds for services to initialize..." -ForegroundColor DarkGray
Start-Sleep -Seconds 6

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Service Status" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

@(
    @{P="8000";N="API Gateway"},
    @{P="8001";N="Auth Service"},
    @{P="8003";N="Product Service"},
    @{P="8004";N="Inventory Service"},
    @{P="8005";N="Order Service"},
    @{P="5173";N="Frontend (Vite)"}
) | ForEach-Object {
    $up = netstat -ano | Select-String ":$($_.P)\s" | Select-Object -First 1
    if ($up) { Write-Host "  [UP]   $($_.N) - http://localhost:$($_.P)" -ForegroundColor Green }
    else { Write-Host "  [DOWN] $($_.N) - port $($_.P) not active" -ForegroundColor Red }
}

Write-Host ""
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor Green
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Admin    : admin@inventory.com / admin123" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# -- Start frontend if not running
$frontendUp = netstat -ano | Select-String ":5173\s" | Select-Object -First 1
if (-not $frontendUp) {
    Write-Host "Frontend not running. Starting Vite dev server..." -ForegroundColor Yellow
    $npmPath = Join-Path $ROOT "frontend"
    if (Test-Path $npmPath) {
        Start-Process powershell -ArgumentList "-NoExit","-Command","npm.cmd run dev" -WorkingDirectory $npmPath -WindowStyle Normal
        Write-Host "    [OK] Vite starting on :5173" -ForegroundColor Green
    }
}

Read-Host "Press ENTER to exit this launcher"
