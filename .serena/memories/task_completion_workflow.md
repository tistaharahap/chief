# Task Completion Workflow

## Before Starting Development
1. **Activate Environment**: `source .venv/bin/activate`
2. **Check Git Status**: `git status` and `git branch`
3. **Pull Latest Changes**: `git pull origin main` (if working in team)

## During Development
1. **Make Code Changes** following project conventions
2. **Test Locally** (once test suite is implemented)
3. **Check for Import Issues** (project currently has circular import)

## Task Completion Checklist

### 1. Code Quality (Required)
```bash
# Lint code and fix issues
source .venv/bin/activate && ruff check . --fix

# Format code
source .venv/bin/activate && ruff format .

# Verify no linting errors remain  
source .venv/bin/activate && ruff check .
```

### 2. Testing (When Available)
```bash
# Run test suite (not implemented yet)
source .venv/bin/activate && pytest

# Run with coverage (future)
source .venv/bin/activate && pytest --cov=src
```

### 3. Import Validation
```bash
# Check imports work (currently failing due to circular import)
source .venv/bin/activate && python -c "from libagentic.agents import get_chief_agent"
source .venv/bin/activate && python src/appclis/chief.py --help
source .venv/bin/activate && python src/appclis/chen.py --help
```

### 4. Git Workflow
```bash
# Stage changes
git add .

# Check what will be committed
git diff --cached

# Commit with descriptive message
git commit -m "type: description"

# Push to remote (if applicable)
git push origin feature-branch-name
```

## Critical Issues to Address
1. **Circular Import**: Fix `libagentic.agents` ↔ `libagentic.tools.search` circular dependency
2. **Test Suite**: Create comprehensive test coverage
3. **CLI Functionality**: Ensure both chief and chen CLIs work properly

## Quality Gates
- ✅ **Ruff linting** passes with no errors
- ✅ **Import statements** work without circular dependencies  
- ✅ **CLI applications** start without errors
- ⏳ **Test coverage** >80% (when tests are implemented)
- ✅ **Git commits** follow conventional commit format

## Environment Notes
- **OS**: macOS (Darwin)
- **Python**: 3.13.2 in virtual environment
- **Ruff**: Available at `.venv/bin/ruff`
- **Pytest**: Available at `.venv/bin/pytest`