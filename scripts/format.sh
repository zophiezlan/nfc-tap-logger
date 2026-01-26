#!/bin/bash
# Format all code in the project
# Run from project root: ./scripts/format.sh

set -e

echo "🎨 Formatting FlowState Project..."
echo ""

# Get project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if formatters are installed
echo "📋 Checking formatters..."

BLACK_INSTALLED=false
ISORT_INSTALLED=false
PRETTIER_INSTALLED=false

if command -v black &> /dev/null; then
    BLACK_INSTALLED=true
else
    echo "⚠️  black not found. Install with: pip install black"
fi

if command -v isort &> /dev/null; then
    ISORT_INSTALLED=true
else
    echo "⚠️  isort not found. Install with: pip install isort"
fi

if command -v prettier &> /dev/null; then
    PRETTIER_INSTALLED=true
else
    echo "⚠️  prettier not found. Install with: npm install -g prettier"
fi

if ! $BLACK_INSTALLED && ! $ISORT_INSTALLED && ! $PRETTIER_INSTALLED; then
    echo ""
    echo "❌ No formatters installed. Please install at least one formatter."
    exit 1
fi

echo ""

# Format Python files with isort (import sorting)
if $ISORT_INSTALLED; then
    echo "📦 Sorting Python imports with isort..."
    isort . --profile black --line-length 79 --skip-gitignore
    echo "✅ isort completed successfully"
    echo ""
fi

# Format Python files with black
if $BLACK_INSTALLED; then
    echo "🐍 Formatting Python files with black..."
    black . --line-length 79 --exclude "/(\.git|\.venv|venv|env|__pycache__|\.eggs|\.tox|build|dist)/"
    echo "✅ black completed successfully"
    echo ""
fi

# Format Markdown, YAML, JSON with prettier
if $PRETTIER_INSTALLED; then
    echo "📝 Formatting Markdown, YAML, JSON with prettier..."
    prettier --write "**/*.{md,yaml,yml,json}" --ignore-path .prettierignore
    echo "✅ prettier completed successfully"
    echo ""
fi

echo "✨ Formatting complete!"
echo ""
