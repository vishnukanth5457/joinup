#!/usr/bin/env pwsh

# JoinUp Platform - Start All Services Script
# This script starts MongoDB, Backend, and Frontend in separate windows

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          JoinUp Platform - Starting All Services              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📍 Step 1: Checking MongoDB..." -ForegroundColor Yellow

# Check if MongoDB is running
$mongoRunning = Get-Process mongod -ErrorAction SilentlyContinue

if ($mongoRunning) {
    Write-Host "✅ MongoDB is already running (PID: $($mongoRunning.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️  MongoDB is not running. Please start it manually:" -ForegroundColor Yellow
    Write-Host "   mongod" -ForegroundColor Gray
    Write-Host "   Or if installed as service: net start MongoDB" -ForegroundColor Gray
    Write-Host "`nContinuing with backend startup..." -ForegroundColor Yellow
}

Write-Host "`n📍 Step 2: Starting Backend Server..." -ForegroundColor Yellow

$backendPath = Join-Path $PSScriptRoot "backend"
$backendScript = Join-Path $backendPath "server.py"

if (Test-Path $backendScript) {
    Write-Host "✅ Backend script found at: $backendScript" -ForegroundColor Green
    
    # Create a script block to run backend
    $backendCmd = @"
cd "$backendPath"
python server.py
pause
"@
    
    # Start backend in new window
    $backendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"$backendCmd`"" -PassThru
    Write-Host "✅ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
    Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
    Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor Gray
} else {
    Write-Host "❌ Backend script not found at: $backendScript" -ForegroundColor Red
}

# Wait a bit for backend to start
Start-Sleep -Seconds 2

Write-Host "`n📍 Step 3: Starting Frontend Server..." -ForegroundColor Yellow

$frontendPath = Join-Path $PSScriptRoot "frontend"
$packageJson = Join-Path $frontendPath "package.json"

if (Test-Path $packageJson) {
    Write-Host "✅ Frontend found at: $frontendPath" -ForegroundColor Green
    
    # Create a script block to run frontend
    $frontendCmd = @"
cd "$frontendPath"
npm start
"@
    
    # Start frontend in new window
    $frontendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"$frontendCmd`"" -PassThru
    Write-Host "✅ Frontend starting (PID: $($frontendProcess.Id))" -ForegroundColor Green
    Write-Host "   Follow the Expo instructions to start:" -ForegroundColor Gray
    Write-Host "   - Press 'a' for Android" -ForegroundColor Gray
    Write-Host "   - Press 'i' for iOS" -ForegroundColor Gray
    Write-Host "   - Press 'w' for Web" -ForegroundColor Gray
    Write-Host "   - Scan QR with Expo Go app" -ForegroundColor Gray
} else {
    Write-Host "❌ Frontend not found at: $frontendPath" -ForegroundColor Red
}

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ✅ JoinUp Platform is Starting!                              ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║  Backend:  http://localhost:8000                              ║" -ForegroundColor Green
Write-Host "║  Frontend: Expo Dev Server (check browser output)             ║" -ForegroundColor Green
Write-Host "║  MongoDB:  localhost:27017                                    ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║  Note: All processes are running in separate windows          ║" -ForegroundColor Yellow
Write-Host "║  Close any window to stop that service                        ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n💡 Tip: To test the API, run:" -ForegroundColor Cyan
Write-Host "   python test_all_features.py" -ForegroundColor Gray

Write-Host "`n📚 For detailed setup, see: SETUP_COMPLETE.md" -ForegroundColor Cyan
