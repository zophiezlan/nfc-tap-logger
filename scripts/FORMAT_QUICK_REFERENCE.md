# Code Formatting Quick Reference

## One-Command Formatting

| Platform               | Command                |
| ---------------------- | ---------------------- |
| **Windows PowerShell** | `.\scripts\format.ps1` |
| **Windows CMD**        | `scripts\format.bat`   |
| **Linux/Mac/WSL**      | `./scripts/format.sh`  |

## Install Formatters

```bash
# Python formatters
pip install -r requirements-dev.txt

# Prettier (Node.js required)
npm install -g prettier
```

## Manual Formatting

### Python

```bash
isort . --profile black --line-length 79
black . --line-length 79
```

### Markdown/YAML/JSON

```bash
prettier --write "**/*.{md,yaml,yml,json}"
```

## Check Only (No Changes)

```bash
black . --check
isort . --check-only
prettier --check "**/*.{md,yaml,yml,json}"
```

## Configuration

- **Python**: `pyproject.toml`
- **Prettier**: `.prettierrc.json`
- **Ignore**: `.prettierignore`

## What Gets Formatted

✅ Python files → `black` + `isort`  
✅ Markdown files → `prettier`  
✅ YAML files → `prettier`  
✅ JSON files → `prettier`

❌ Binary files  
❌ Generated files  
❌ Dependencies (venv, node_modules)

## Full Documentation

See [scripts/README_FORMATTING.md](README_FORMATTING.md)
