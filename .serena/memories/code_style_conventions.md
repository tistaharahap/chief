# Code Style and Conventions

## Python Version
- **Target**: Python 3.13
- **Minimum**: Python 3.8 (as per pyproject.toml)

## Code Formatting (Ruff Configuration)
- **Line Length**: 120 characters
- **Quote Style**: Double quotes (`"`) for inline and multiline
- **Indentation**: Spaces (not tabs)
- **Line Endings**: Auto-detected

## Import Organization
- **Known First Party**: `["apppublicapi", "libagentic", "libshared"]`
- **Style**: Combine as imports, force wrap aliases
- **Relative Imports**: Banned (absolute imports required)
- **Import Order**: External → First party → Local

## Linting Rules (Selected)
- **pycodestyle** (E, W) - Code style enforcement
- **pyflakes** (F) - Code quality checks
- **isort** (I) - Import sorting
- **flake8-bugbear** (B) - Bug detection
- **flake8-comprehensions** (C4) - List/dict comprehension improvements
- **pyupgrade** (UP) - Modern Python syntax
- **flake8-quotes** (Q) - Quote consistency
- **flake8-simplify** (SIM) - Code simplification
- **flake8-tidy-imports** (TID) - Import organization
- **flake8-type-checking** (TCH) - Type checking imports
- **flake8-use-pathlib** (PTH) - Prefer pathlib over os.path
- **flake8-datetimez** (DTZ) - Timezone-aware datetime

## Project Structure
```
src/
├── appclis/          # CLI applications
├── libagentic/       # Core agent library
│   └── tools/        # Agent tools
└── libshared/        # Shared utilities
```

## Naming Conventions
- **Modules**: snake_case
- **Classes**: PascalCase
- **Functions/Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE