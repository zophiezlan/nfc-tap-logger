#!/usr/bin/env pwsh
# Format all code in the project
# Run from project root: .\scripts\format.ps1

Write-Host "🎨 Formatting NFC Tap Logger Project..." -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $PSScriptRoot

# Change to project root
Push-Location $projectRoot

try {
    # Check if formatters are installed
    Write-Host "📋 Checking formatters..." -ForegroundColor Yellow

    $blackInstalled = $null -ne (Get-Command black -ErrorAction SilentlyContinue)
    $isortInstalled = $null -ne (Get-Command isort -ErrorAction SilentlyContinue)
    $prettierInstalled = $null -ne (Get-Command prettier -ErrorAction SilentlyContinue)

    if (-not $blackInstalled) {
        Write-Host "⚠️  black not found. Install with: pip install black" -ForegroundColor Red
    }
    if (-not $isortInstalled) {
        Write-Host "⚠️  isort not found. Install with: pip install isort" -ForegroundColor Red
    }
    if (-not $prettierInstalled) {
        Write-Host "⚠️  prettier not found. Install with: npm install -g prettier" -ForegroundColor Red
    }

    if (-not ($blackInstalled -or $isortInstalled -or $prettierInstalled)) {
        Write-Host ""
        Write-Host "❌ No formatters installed. Please install at least one formatter." -ForegroundColor Red
        exit 1
    }

    Write-Host ""

    # Format Python files with isort (import sorting)
    if ($isortInstalled) {
        Write-Host "📦 Sorting Python imports with isort..." -ForegroundColor Green
        isort . --profile black --line-length 79 --skip-gitignore
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ isort completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  isort encountered issues" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    # Format Python files with black
    if ($blackInstalled) {
        Write-Host "🐍 Formatting Python files with black..." -ForegroundColor Green
        black . --line-length 79 --exclude "/(\.git|\.venv|venv|env|__pycache__|\.eggs|\.tox|build|dist)/"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ black completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  black encountered issues" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    # Format Markdown, YAML, JSON with prettier
    if ($prettierInstalled) {
        Write-Host "📝 Formatting Markdown, YAML, JSON with prettier..." -ForegroundColor Green
        prettier --write "**/*.{md,yaml,yml,json}" --ignore-path .prettierignore
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ prettier completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  prettier encountered issues" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    Write-Host "✨ Formatting complete!" -ForegroundColor Cyan
    Write-Host ""

}
finally {
    Pop-Location
}
