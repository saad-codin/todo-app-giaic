#Requires -Version 5.1
<#
.SYNOPSIS
    Azure Free Tier Deployment - Todo App
.DESCRIPTION
    Deploys backend (FastAPI) and frontend (Next.js) to Azure App Service F1 (Free).
.USAGE
    .\scripts\deploy-azure.ps1              # Deploy both
    .\scripts\deploy-azure.ps1 -Target backend   # Backend only
    .\scripts\deploy-azure.ps1 -Target frontend  # Frontend only
#>

param(
    [ValidateSet("all", "backend", "frontend")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"

# ── Configuration ────────────────────────────────────────────────────────────
$RESOURCE_GROUP   = "todo-app-rg"
$LOCATION         = "centralus"
$BACKEND_APP      = "todo-backend-app"
$FRONTEND_APP     = "todo-frontend-app"
$APP_SERVICE_PLAN = "todo-free-plan"
$PROJECT_DIR      = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Log($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[!]  $msg" -ForegroundColor Yellow }
function Info($msg)  { Write-Host "[->] $msg" -ForegroundColor Cyan }
function Err($msg)   { Write-Host "[X]  $msg" -ForegroundColor Red; exit 1 }

# ── Pre-flight ───────────────────────────────────────────────────────────────
function Check-Prerequisites {
    Info "Checking prerequisites..."

    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Err "Azure CLI not found. Install from: https://aka.ms/installazurecli"
    }

    $account = az account show 2>$null | ConvertFrom-Json
    if (-not $account) {
        Warn "Not logged in. Opening browser..."
        az login
        $account = az account show | ConvertFrom-Json
    }
    Log "Logged in to Azure: $($account.name)"
}

# ── Create shared resources ──────────────────────────────────────────────────
function Create-Resources {
    Info "Creating resource group: $RESOURCE_GROUP..."
    az group create --name $RESOURCE_GROUP --location $LOCATION --output none 2>$null
    Log "Resource group ready"

    Info "Creating Free (F1) App Service Plan..."
    az appservice plan create `
        --name $APP_SERVICE_PLAN `
        --resource-group $RESOURCE_GROUP `
        --location $LOCATION `
        --sku F1 `
        --is-linux `
        --output none 2>$null
    Log "App Service Plan ready (F1 Free)"
}

# ── Parse .env file ──────────────────────────────────────────────────────────
function Get-EnvValue($file, $key) {
    $line = Get-Content $file | Where-Object { $_ -match "^$key=" } | Select-Object -First 1
    if ($line) {
        return $line.Substring($key.Length + 1)
    }
    return ""
}

# ── Deploy Backend ───────────────────────────────────────────────────────────
function Deploy-Backend {
    Info "Deploying backend (FastAPI)..."

    Info "Creating backend web app..."
    az webapp create `
        --resource-group $RESOURCE_GROUP `
        --plan $APP_SERVICE_PLAN `
        --name $BACKEND_APP `
        --runtime "PYTHON:3.11" `
        --output none 2>$null
    if ($LASTEXITCODE -ne 0) { Warn "Backend app may already exist, continuing..." }

    Info "Configuring startup command..."
    az webapp config set `
        --resource-group $RESOURCE_GROUP `
        --name $BACKEND_APP `
        --startup-file "gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120" `
        --output none

    $BACKEND_URL = "https://${BACKEND_APP}.azurewebsites.net"
    Info "Backend URL: $BACKEND_URL"

    # Read secrets from .env
    $envFile = Join-Path $PROJECT_DIR "backend\.env"
    if (-not (Test-Path $envFile)) { Err "backend\.env not found. Create it first." }

    $DB_URL     = Get-EnvValue $envFile "DATABASE_URL"
    $SECRET_KEY = Get-EnvValue $envFile "SECRET_KEY"
    $OPENAI_KEY = Get-EnvValue $envFile "OPENAI_API_KEY"

    Info "Setting backend environment variables..."
    az webapp config appsettings set `
        --resource-group $RESOURCE_GROUP `
        --name $BACKEND_APP `
        --settings `
            DATABASE_URL="$DB_URL" `
            SECRET_KEY="$SECRET_KEY" `
            ALGORITHM="HS256" `
            ACCESS_TOKEN_EXPIRE_MINUTES="1440" `
            OPENAI_API_KEY="$OPENAI_KEY" `
            FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net" `
            SCM_DO_BUILD_DURING_DEPLOYMENT="true" `
            WEBSITE_PORT="8000" `
        --output none
    Log "Backend environment configured"

    # Zip deploy
    Info "Packaging backend code..."
    $backendDir = Join-Path $PROJECT_DIR "backend"
    $zipPath = Join-Path $env:TEMP "backend-deploy.zip"

    if (Test-Path $zipPath) { Remove-Item $zipPath }

    # Create zip excluding unnecessary files
    $filesToZip = Get-ChildItem -Path $backendDir -Recurse -File |
        Where-Object {
            $rel = $_.FullName.Substring($backendDir.Length + 1)
            $rel -notmatch '(^\.env$|^\.venv\\|^venv\\|__pycache__|\.pyc$|^todo\.db$|^\.git\\|^\.azure\\)'
        }

    # Use .NET compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
    foreach ($file in $filesToZip) {
        $entryName = $file.FullName.Substring($backendDir.Length + 1).Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $entryName) | Out-Null
    }
    $zip.Dispose()

    Info "Deploying backend (this may take a few minutes)..."
    az webapp deploy `
        --resource-group $RESOURCE_GROUP `
        --name $BACKEND_APP `
        --src-path $zipPath `
        --type zip `
        --output none

    Remove-Item $zipPath -ErrorAction SilentlyContinue
    Log "Backend deployed at: $BACKEND_URL"
}

# ── Deploy Frontend ──────────────────────────────────────────────────────────
function Deploy-Frontend {
    Info "Deploying frontend (Next.js)..."

    $BACKEND_URL = "https://${BACKEND_APP}.azurewebsites.net"

    Info "Creating frontend web app..."
    az webapp create `
        --resource-group $RESOURCE_GROUP `
        --plan $APP_SERVICE_PLAN `
        --name $FRONTEND_APP `
        --runtime "NODE:20-lts" `
        --output none 2>$null
    if ($LASTEXITCODE -ne 0) { Warn "Frontend app may already exist, continuing..." }

    # Read frontend env
    $frontendEnv = Join-Path $PROJECT_DIR "frontend\.env.local"
    $CHATKIT_KEY = ""
    if (Test-Path $frontendEnv) {
        $CHATKIT_KEY = Get-EnvValue $frontendEnv "NEXT_PUBLIC_CHATKIT_DOMAIN_KEY"
    }

    Info "Setting frontend environment variables..."
    az webapp config appsettings set `
        --resource-group $RESOURCE_GROUP `
        --name $FRONTEND_APP `
        --settings `
            NEXT_PUBLIC_API_URL="$BACKEND_URL" `
            NEXT_PUBLIC_CHATKIT_DOMAIN_KEY="$CHATKIT_KEY" `
            SCM_DO_BUILD_DURING_DEPLOYMENT="true" `
            WEBSITE_PORT="3000" `
        --output none
    Log "Frontend environment configured"

    az webapp config set `
        --resource-group $RESOURCE_GROUP `
        --name $FRONTEND_APP `
        --startup-file "node server.js" `
        --output none

    # Build locally
    Info "Building frontend locally (this may take a minute)..."
    $frontendDir = Join-Path $PROJECT_DIR "frontend"

    Push-Location $frontendDir
    $env:NEXT_PUBLIC_API_URL = $BACKEND_URL
    $env:NEXT_PUBLIC_CHATKIT_DOMAIN_KEY = $CHATKIT_KEY

    npm ci
    npm run build

    # Package standalone build
    Info "Packaging standalone build..."
    $standalonePath = Join-Path $frontendDir ".next\standalone"
    $staticSrc      = Join-Path $frontendDir ".next\static"
    $staticDest     = Join-Path $standalonePath ".next\static"
    $publicSrc      = Join-Path $frontendDir "public"
    $publicDest     = Join-Path $standalonePath "public"

    # Copy static assets into standalone
    if (Test-Path $staticSrc) {
        Copy-Item -Path $staticSrc -Destination $staticDest -Recurse -Force
    }
    if (Test-Path $publicSrc) {
        Copy-Item -Path $publicSrc -Destination $publicDest -Recurse -Force
    }

    $zipPath = Join-Path $env:TEMP "frontend-deploy.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($standalonePath, $zipPath)

    Pop-Location

    Info "Deploying frontend (this may take a few minutes)..."
    az webapp deploy `
        --resource-group $RESOURCE_GROUP `
        --name $FRONTEND_APP `
        --src-path $zipPath `
        --type zip `
        --output none

    Remove-Item $zipPath -ErrorAction SilentlyContinue

    $FRONTEND_URL = "https://${FRONTEND_APP}.azurewebsites.net"
    Log "Frontend deployed at: $FRONTEND_URL"
}

# ── Update CORS ──────────────────────────────────────────────────────────────
function Update-Cors {
    $FRONTEND_URL = "https://${FRONTEND_APP}.azurewebsites.net"
    Info "Updating backend CORS for: $FRONTEND_URL"

    az webapp cors add `
        --resource-group $RESOURCE_GROUP `
        --name $BACKEND_APP `
        --allowed-origins $FRONTEND_URL `
        --output none 2>$null
    Log "CORS updated"
}

# ── Summary ──────────────────────────────────────────────────────────────────
function Print-Summary {
    $BACKEND_URL  = "https://${BACKEND_APP}.azurewebsites.net"
    $FRONTEND_URL = "https://${FRONTEND_APP}.azurewebsites.net"

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host "  Deployment Complete (Azure Free Tier)" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Frontend:  $FRONTEND_URL" -ForegroundColor Cyan
    Write-Host "  Backend:   $BACKEND_URL" -ForegroundColor Cyan
    Write-Host "  Health:    $BACKEND_URL/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Free tier notes:" -ForegroundColor Yellow
    Write-Host "  - Apps sleep after ~20 min inactivity (cold start ~30s)"
    Write-Host "  - 60 CPU min/day limit per app"
    Write-Host "  - No custom domain SSL on F1"
    Write-Host ""
    Write-Host "  Useful commands:" -ForegroundColor Cyan
    Write-Host "  az webapp log tail -g $RESOURCE_GROUP -n $BACKEND_APP"
    Write-Host "  az webapp log tail -g $RESOURCE_GROUP -n $FRONTEND_APP"
    Write-Host "  az group delete -n $RESOURCE_GROUP --yes   # tear down"
    Write-Host ""
}

# ── Main ─────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Azure Free Tier Deployment - Todo App" -ForegroundColor Cyan
Write-Host ""

Check-Prerequisites
Create-Resources

switch ($Target) {
    "all" {
        Deploy-Backend
        Deploy-Frontend
        Update-Cors
    }
    "backend"  { Deploy-Backend }
    "frontend" { Deploy-Frontend }
}

Print-Summary
