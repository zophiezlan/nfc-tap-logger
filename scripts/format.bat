@echo off
REM Format all code in the project
REM Run from project root: scripts\format.bat

echo 🎨 Formatting FlowState Project...
echo.

cd /d "%~dp0\.."

REM Check if formatters are installed
echo 📋 Checking formatters...

where black >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  black not found. Install with: pip install black
    set BLACK_INSTALLED=0
) else (
    set BLACK_INSTALLED=1
)

where isort >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  isort not found. Install with: pip install isort
    set ISORT_INSTALLED=0
) else (
    set ISORT_INSTALLED=1
)

where prettier >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  prettier not found. Install with: npm install -g prettier
    set PRETTIER_INSTALLED=0
) else (
    set PRETTIER_INSTALLED=1
)

if %BLACK_INSTALLED%==0 if %ISORT_INSTALLED%==0 if %PRETTIER_INSTALLED%==0 (
    echo.
    echo ❌ No formatters installed. Please install at least one formatter.
    exit /b 1
)

echo.

REM Format Python files with isort (import sorting)
if %ISORT_INSTALLED%==1 (
    echo 📦 Sorting Python imports with isort...
    isort . --profile black --line-length 79 --skip-gitignore
    echo ✅ isort completed successfully
    echo.
)

REM Format Python files with black
if %BLACK_INSTALLED%==1 (
    echo 🐍 Formatting Python files with black...
    black . --line-length 79 --exclude "/(\.git|\.venv|venv|env|__pycache__|\.eggs|\.tox|build|dist)/"
    echo ✅ black completed successfully
    echo.
)

REM Format Markdown, YAML, JSON with prettier
if %PRETTIER_INSTALLED%==1 (
    echo 📝 Formatting Markdown, YAML, JSON with prettier...
    prettier --write "**/*.{md,yaml,yml,json}" --ignore-path .prettierignore
    echo ✅ prettier completed successfully
    echo.
)

echo ✨ Formatting complete!
echo.
