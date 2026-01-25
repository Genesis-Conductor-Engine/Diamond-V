<#
.SYNOPSIS
    Launch Yennefer UI (hosted and/or local)

.DESCRIPTION
    Opens the hosted Yennefer UI and optionally starts a local development server.

.PARAMETER NoOpen
    Don't open the browser

.PARAMETER WebOnly
    Only open hosted UI, skip local server

.PARAMETER DryRun
    Print what would be executed without running

.EXAMPLE
    .\launch_yennefer.ps1
    Opens hosted UI and starts local server if available

.EXAMPLE
    .\launch_yennefer.ps1 -WebOnly
    Only opens the hosted UI

.EXAMPLE
    .\launch_yennefer.ps1 -DryRun
    Shows what would be executed without running
#>

param(
    [switch]$NoOpen,
    [switch]$WebOnly,
    [switch]$DryRun,
    [switch]$Help
)

# Configuration
$HOSTED_URL = "https://yennefer.quest"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Show-Help {
    @"
🔮 Yennefer Launcher (PowerShell)

Usage: .\launch_yennefer.ps1 [OPTIONS]

Options:
  -NoOpen       Don't open the browser
  -WebOnly      Only open hosted UI, skip local server
  -DryRun       Print what would be executed without running
  -Help         Show this help message

Examples:
  .\launch_yennefer.ps1              # Open hosted UI + start local server
  .\launch_yennefer.ps1 -WebOnly     # Just open hosted UI
  .\launch_yennefer.ps1 -DryRun      # Preview commands

"@
}

function Open-Browser {
    param([string]$Url)
    
    if ($DryRun) {
        Write-Info "[DRY-RUN] Would open: $Url"
        return
    }
    
    if ($NoOpen) {
        Write-Info "Browser opening disabled. URL: $Url"
        return
    }
    
    Write-Info "Opening $Url ..."
    
    try {
        Start-Process $Url
        Write-Success "Browser opened"
    }
    catch {
        Write-Warning "Failed to open browser. Please open manually: $Url"
    }
}

function Get-UIDetection {
    $result = @{
        Type = "none"
        Path = ""
        Command = ""
        Port = ""
    }
    
    # Check for yennefer-observatory (Vite/React UI)
    $observatoryPkg = Join-Path $REPO_ROOT "yennefer-observatory" "package.json"
    if (Test-Path $observatoryPkg) {
        $pkgContent = Get-Content $observatoryPkg -Raw
        if ($pkgContent -match '"dev"') {
            $result.Type = "node-vite"
            $result.Path = Join-Path $REPO_ROOT "yennefer-observatory"
            $result.Command = "npm run dev"
            $result.Port = "5173"
            return $result
        }
    }
    
    # Check root package.json for dev script
    $rootPkg = Join-Path $REPO_ROOT "package.json"
    if (Test-Path $rootPkg) {
        $pkgContent = Get-Content $rootPkg -Raw
        if ($pkgContent -match '"dev"') {
            $result.Type = "node"
            $result.Path = $REPO_ROOT
            $result.Command = "npm run dev"
            $result.Port = "3000"
            return $result
        }
    }
    
    # Check for Python UI (streamlit/gradio)
    $requirementsFile = Join-Path $REPO_ROOT "requirements.txt"
    if (Test-Path $requirementsFile) {
        $reqContent = Get-Content $requirementsFile -Raw -ErrorAction SilentlyContinue
        
        if ($reqContent -match "streamlit") {
            $streamlitApp = Get-ChildItem -Path $REPO_ROOT -Filter "app.py" -Recurse -Depth 3 | Select-Object -First 1
            if ($null -eq $streamlitApp) {
                $streamlitApp = Get-ChildItem -Path $REPO_ROOT -Filter "streamlit_app.py" -Recurse -Depth 3 | Select-Object -First 1
            }
            if ($null -ne $streamlitApp) {
                $result.Type = "python-streamlit"
                $result.Path = $REPO_ROOT
                $result.Command = "streamlit run `"$($streamlitApp.FullName)`" --server.headless true"
                $result.Port = "8501"
                return $result
            }
        }
        
        if ($reqContent -match "gradio") {
            $gradioApp = Get-ChildItem -Path $REPO_ROOT -Filter "app.py" -Recurse -Depth 3 | Select-Object -First 1
            if ($null -ne $gradioApp) {
                $result.Type = "python-gradio"
                $result.Path = $REPO_ROOT
                $result.Command = "python `"$($gradioApp.FullName)`""
                $result.Port = "7860"
                return $result
            }
        }
    }
    
    # Check for yennefer-core Flask/FastAPI
    $yenCoreServer = Join-Path $REPO_ROOT "yennefer-core" "landing_server.py"
    if (Test-Path $yenCoreServer) {
        $result.Type = "python-flask"
        $result.Path = Join-Path $REPO_ROOT "yennefer-core"
        $result.Command = "python landing_server.py"
        $result.Port = "8000"
        return $result
    }
    
    return $result
}

function Start-LocalUI {
    param([hashtable]$UIInfo)
    
    if ($UIInfo.Type -eq "none") {
        Write-Info "No local UI detected; using hosted UI only."
        return
    }
    
    Write-Info "Detected UI: $($UIInfo.Type)"
    Write-Info "Path: $($UIInfo.Path)"
    Write-Info "Command: $($UIInfo.Command)"
    Write-Info "Port: $($UIInfo.Port)"
    
    if ($DryRun) {
        Write-Info "[DRY-RUN] Would run: cd `"$($UIInfo.Path)`" && $($UIInfo.Command)"
        return
    }
    
    Write-Host ""
    Write-Info "Starting local UI server..."
    Write-Info "Local URL will be: http://localhost:$($UIInfo.Port)"
    Write-Host ""
    
    Set-Location $UIInfo.Path
    
    # Install dependencies if needed
    if ($UIInfo.Type -like "node*") {
        if (-not (Test-Path "node_modules")) {
            Write-Info "Installing Node dependencies..."
            npm install
        }
    }
    
    # Run the command
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "Starting: $($UIInfo.Command)" -ForegroundColor Magenta
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host ""
    
    Invoke-Expression $UIInfo.Command
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Host "🔮 Yennefer Launcher" -ForegroundColor Magenta
Write-Host ""

# Always open hosted UI first
Open-Browser -Url $HOSTED_URL

# Start local UI unless web-only mode
if (-not $WebOnly) {
    $uiInfo = Get-UIDetection
    Start-LocalUI -UIInfo $uiInfo
}
else {
    Write-Info "Web-only mode: skipping local UI"
}

if ($DryRun) {
    Write-Success "[DRY-RUN] Complete - no changes made"
}
