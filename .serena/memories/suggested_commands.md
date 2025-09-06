# Suggested Development Commands

## Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Check Python version
python --version  # Should show Python 3.13.2
```

## Code Quality Commands
```bash
# Lint and format code
source .venv/bin/activate && ruff check .
source .venv/bin/activate && ruff check . --fix
source .venv/bin/activate && ruff format .

# Show linting statistics
source .venv/bin/activate && ruff check . --statistics

# Check specific files
source .venv/bin/activate && ruff check src/
```

## Testing Commands
```bash
# Run tests (when test suite is created)
source .venv/bin/activate && pytest
source .venv/bin/activate && pytest -v
source .venv/bin/activate && pytest --tb=short

# Run with coverage (once tests exist)
source .venv/bin/activate && pytest --cov=src
```

## Application Commands (Currently Broken - Circular Import)
```bash
# Note: These commands currently fail due to circular import issue
# chief CLI
source .venv/bin/activate && python src/appclis/chief.py --help

# chen CLI  
source .venv/bin/activate && python src/appclis/chen.py --help
```

## Development Utilities
```bash
# Check project structure
ls -la src/
find src/ -name "*.py" -type f

# Check dependencies
cat requirements.lock | head -20
cat requirements-dev.lock | head -10

# Git operations
git status
git add . && git commit -m "feat: description"
git log --oneline -10
```

## macOS Specific Commands (Darwin)
```bash
# Standard Unix commands work on macOS
ls -la          # List files with details
find . -name    # Find files by name
grep -r         # Recursive search
cd             # Change directory
```

## Troubleshooting
```bash
# Check ruff configuration
source .venv/bin/activate && ruff check --show-settings src/appclis/chief.py

# Validate Python environment
source .venv/bin/activate && python -c "import sys; print(sys.path)"

# Debug import issues
source .venv/bin/activate && python -c "import libagentic; print('OK')"
```