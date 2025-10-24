# Run Services Script for Classroom Connect
# This script starts both the Django server (Classroom Connect) and Node.js server (Academic Analyzer)
# Created: October 18, 2025

# Check if running as administrator (needed for network permissions)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Display header
Write-Host "┌──────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│     CLASSROOM CONNECT SERVICE STARTER    │" -ForegroundColor Cyan
Write-Host "└──────────────────────────────────────────┘" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Classroom Connect Application Services..." -ForegroundColor Green
Write-Host "--------------------------------------------" -ForegroundColor Green

# Define paths to each service
$djangoPath = Join-Path -Path $PSScriptRoot -ChildPath "classroom_connect\backend_quiz"
$nodePath = Join-Path -Path $PSScriptRoot -ChildPath "academic-analyzer"

# Validate paths exist
if (-not (Test-Path -Path $djangoPath)) {
    Write-Host "❌ Error: Django project path not found at $djangoPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -Path $nodePath)) {
    Write-Host "❌ Error: Node.js project path not found at $nodePath" -ForegroundColor Red
    exit 1
}

# Validate dependency files exist
$djangoManagePy = Join-Path -Path $djangoPath -ChildPath "manage.py"
$nodeServerJs = Join-Path -Path $nodePath -ChildPath "server.js"

if (-not (Test-Path -Path $djangoManagePy)) {
    Write-Host "❌ Error: Django manage.py not found at $djangoManagePy" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -Path $nodeServerJs)) {
    Write-Host "❌ Error: Node.js server.js not found at $nodeServerJs" -ForegroundColor Red
    exit 1
}

# Function to check if a port is in use
function Test-PortInUse {
    param(
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connections.Count -gt 0
}

# Function to start a service in a new PowerShell window
function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$WorkingDirectory,
        [string]$Command,
        [string]$Color,
        [int]$Port
    )
    
    # Check if the port is already in use
    if (Test-PortInUse -Port $Port) {
        Write-Host "⚠️ Warning: Port $Port is already in use. $Title might not start correctly." -ForegroundColor Yellow
    }
    
    Write-Host "🚀 Starting $Title service on port $Port..." -ForegroundColor $Color
    
    # Create a more detailed startup script with error handling
    $scriptBlock = @"
cd '$WorkingDirectory'
Write-Host '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' -ForegroundColor $Color
Write-Host '  Starting $Title on port $Port' -ForegroundColor $Color
Write-Host '  $(Get-Date)' -ForegroundColor $Color
Write-Host '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' -ForegroundColor $Color
Write-Host ''
try {
    $Command
} catch {
    Write-Host 'An error occurred while running the service:' -ForegroundColor Red
    Write-Host `$_.Exception.Message -ForegroundColor Red
}
Write-Host ''
Write-Host 'Service stopped. Press Enter to close this window...' -ForegroundColor Yellow
Read-Host
"@
    
    # Start the service in a new PowerShell window
    $encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($scriptBlock))
    
    Start-Process powershell.exe -ArgumentList "-NoExit", "-EncodedCommand", $encodedCommand -WindowStyle Normal
}

# Define ports
$djangoPort = 8000
$nodePort = 5000

# Check for npm and python/pip
$npmInstalled = $null -ne (Get-Command npm -ErrorAction SilentlyContinue)
$pythonInstalled = $null -ne (Get-Command python -ErrorAction SilentlyContinue)

if (-not $npmInstalled) {
    Write-Host "⚠️ Warning: npm not found. Node.js server may not start correctly." -ForegroundColor Yellow
}

if (-not $pythonInstalled) {
    Write-Host "⚠️ Warning: python not found. Django server may not start correctly." -ForegroundColor Yellow
}

# Inform the user
Write-Host "This script will start both services in separate windows:" -ForegroundColor Cyan
Write-Host "  ✅ Django server (Classroom Connect): http://localhost:$djangoPort" -ForegroundColor Cyan
Write-Host "  ✅ Node.js server (Academic Analyzer): http://localhost:$nodePort" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Magenta
Write-Host "  - Django and required Python packages" -ForegroundColor Magenta
Write-Host "  - Node.js and required npm packages" -ForegroundColor Magenta
Write-Host ""
Write-Host "⚠️ Press Ctrl+C in each window when you want to stop the services." -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Do you want to continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Operation cancelled." -ForegroundColor Red
    exit
}

# Start the Node.js server first (API backend)
Start-ServiceWindow -Title "Node.js Server (Academic Analyzer)" -WorkingDirectory $nodePath -Command "node server.js" -Color "Green" -Port $nodePort

# Give a short delay between starting services
Write-Host "Waiting for Node.js server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start the Django server (frontend)
Start-ServiceWindow -Title "Django Server (Classroom Connect)" -WorkingDirectory $djangoPath -Command "python manage.py runserver" -Color "Blue" -Port $djangoPort

# Final instructions
Write-Host ""
Write-Host "✅ Both services have been started in separate windows." -ForegroundColor Green
Write-Host "✅ You can access the application at http://localhost:$djangoPort" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Main application pages:" -ForegroundColor Cyan
Write-Host "  - Home: http://localhost:$djangoPort/" -ForegroundColor Cyan
Write-Host "  - Student Login: http://localhost:$djangoPort/student/login/" -ForegroundColor Cyan
Write-Host "  - Staff Login: http://localhost:$djangoPort/staff/login/" -ForegroundColor Cyan
Write-Host ""

# Add helper function for later service troubleshooting
Write-Host "🔧 If you encounter any issues:" -ForegroundColor Yellow
Write-Host "  1. Ensure all dependencies are installed in both projects" -ForegroundColor Yellow
Write-Host "  2. Check if ports $djangoPort and $nodePort are free" -ForegroundColor Yellow
Write-Host "  3. Verify database connections are properly configured" -ForegroundColor Yellow
Write-Host ""
Write-Host "📌 Run this script again to restart the services if needed" -ForegroundColor Magenta
Write-Host ""
