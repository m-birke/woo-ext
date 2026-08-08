# woo-ext Project Instructions

## Project Overview

**woo-ext** is a Python library that provides extended functions for the WooCommerce REST API client. It handles order management, metadata, and data model transformations with a focus on type safety and data validation using Pydantic.

## Tech Stack

- **Language**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13)
- **Key Dependencies**: 
  - Pydantic >= 2.12.5 (data validation)
  - tenacity >= 9.1 (retry logic)
  - woocommerce >= 3.0.0 (WooCommerce client)
- **WooCommerce API**: Use v3
- **Build**: Hatchling with VCS versioning
- **Code Quality**: Ruff (linting), mypy (type checking), pytest (testing)

## Project Structure

```
woo-ext/
├── src/woo_ext/           # Main package source
│   ├── __init__.py
│   ├── data_models.py     # Pydantic models (WooOrder, WooMetaDatum, etc.)
│   ├── orders.py          # Order handling functions
│   ├── order_metadata.py  # Order metadata operations
│   └── utils.py           # Utility functions
├── tests/                 # Test suite (pytest)
├── pyproject.toml         # Project config & dependencies
└── README.md
```

## Code Style & Quality Standards

- **Formatting & Linting**: Ruff (strict rules configured in pyproject.toml)
- **Type Checking**: mypy with strict settings
- **Line Length**: 120 characters
- **Imports**: Absolute imports enforced, organized with isort
- **Testing**: pytest with coverage tracking
- **Pre-commit**: Hooks configured in `.pre-commit-config.yaml`

### Ruff Rules Enforced
- A (builtins), ARG (unused args), B (bugbear)
- E (style errors), F (unused code)
- I (import sorting), N (naming)
- S (security), UP (upgrades), and 15+ more rule sets

## Development Workflow

### Testing
```bash
hatch run test                    # Run tests
hatch run test-cov               # Run with coverage
hatch run cov                     # Full coverage report
```

### Type Checking
```bash
hatch run types:check             # Run mypy
```

### Building
```bash
./build.sh                        # Build the package
```

## Key Patterns & Conventions

1. **Pydantic Models**: All data structures inherit from `BaseModel` with field validators
2. **Enums**: Use for fixed status values (e.g., `WooOrderStatus`)
3. **Type Hints**: Always use full type annotations; mypy is strict
4. **Error Handling**: Use tenacity for retries in API calls
5. **Metadata**: WooCommerce metadata must be JSON-serializable (validated in models)

## When Making Changes

- Ensure all code passes mypy type checking (strict mode)
- Run ruff to auto-fix linting issues
- Add tests in `tests/` for new functionality
- Update type hints comprehensively
- Maintain 100% type coverage where possible
- Keep docstrings for public APIs

## CI/CD

- GitHub Actions: `.github/workflows/static-code-check.yml`
- Runs on every push: linting, type checks, tests
- Pre-commit hooks available via renovate

## Common Tasks

- **Add a new data model**: Create in `data_models.py`, inherit from `BaseModel`, add validators
- **Add order functionality**: Extend `orders.py` or `order_metadata.py`
- **Handle API calls**: Use tenacity decorators for retries, maintain type safety
- **Test changes**: Add test cases in `tests/` following pytest patterns
