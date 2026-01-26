# Code Formatting Scripts

This directory contains scripts to automatically format all code in the project.

## Quick Start

### Windows (PowerShell)

```powershell
.\scripts\format.ps1
```

### Windows (Command Prompt)

```cmd
scripts\format.bat
```

### Linux/Mac/WSL

```bash
chmod +x scripts/format.sh
./scripts/format.sh
```

## What Gets Formatted

- **Python files** (.py): Formatted with `black` and `isort`
  - Line length: 79 characters (PEP 8)
  - Import sorting with `black` profile
- **Markdown files** (.md): Formatted with `prettier`
  - Consistent heading styles
  - Proper list formatting
- **YAML files** (.yaml, .yml): Formatted with `prettier`
  - Consistent indentation
  - Proper spacing
- **JSON files** (.json): Formatted with `prettier`
  - Consistent indentation
  - Proper spacing

## Installation

### Python Formatters

Install all Python development dependencies:

```bash
pip install -r requirements-dev.txt
```

Or install individually:

```bash
pip install black isort
```

### Prettier (for Markdown/YAML/JSON)

Install with npm globally:

```bash
npm install -g prettier
```

Or install in project (creates node_modules):

```bash
npm install --save-dev prettier
```

## Configuration

### Black Configuration

See `pyproject.toml` for black settings:

- Line length: 79
- Target Python versions: 3.8+

### isort Configuration

See `pyproject.toml` for isort settings:

- Profile: black (compatible with black formatting)
- Line length: 79
- Skip gitignore files

### Prettier Configuration

See `.prettierrc.json` for prettier settings:

- Print width: 80
- Tab width: 2 spaces
- End of line: LF

### Ignore Files

- `.prettierignore`: Excludes files from prettier formatting
- `.gitignore`: Used by isort to skip files

## Manual Formatting

### Format Python Files Only

```bash
# Sort imports
isort . --profile black --line-length 79

# Format code
black . --line-length 79
```

### Format Markdown/YAML Only

```bash
prettier --write "**/*.{md,yaml,yml,json}"
```

### Check Formatting (Don't Modify)

```bash
# Check Python
black . --check
isort . --check-only

# Check Markdown/YAML
prettier --check "**/*.{md,yaml,yml,json}"
```

## Pre-commit Hook (Optional)

You can set up automatic formatting on commit by creating `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "🎨 Running formatters..."
./scripts/format.sh
git add -u
```

Then make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

## Troubleshooting

### "Command not found" errors

- **black/isort**: Install Python formatters with `pip install -r requirements-dev.txt`
- **prettier**: Install with `npm install -g prettier`

### "Permission denied" on Linux/Mac

```bash
chmod +x scripts/format.sh
```

### Prettier formats Python files

Check that `.prettierignore` includes `*.py` patterns

### Formatting breaks code

- This shouldn't happen with proper configuration
- Check `pyproject.toml` for black/isort settings
- Report issues with specific files

## Editor Integration

### VS Code

Install extensions:

- Python (ms-python.python) - includes black/isort support
- Prettier (esbenp.prettier-vscode)

Settings:

```json
{
  "python.formatting.provider": "black",
  "python.sortImports.provider": "isort",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[markdown]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[yaml]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm/IntelliJ

- Settings → Tools → Black
- Settings → Tools → isort
- Settings → Languages → JavaScript → Prettier

## CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Check formatting
  run: |
    pip install black isort
    black . --check
    isort . --check-only

    npm install -g prettier
    prettier --check "**/*.{md,yaml,yml,json}"
```

## Related Files

- `requirements-dev.txt` - Python development dependencies
- `pyproject.toml` - Python tool configuration (black, isort, pytest, mypy)
- `.prettierrc.json` - Prettier configuration
- `.prettierignore` - Files to exclude from prettier
