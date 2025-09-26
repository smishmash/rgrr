# Server Development Guidelines

## Commands
- Run all tests: `python -m pytest rgrr/tests`
- Run single test: `python -m pytest rgrr/tests/test_server.py::test_function_name`
- Lint: `flake8 rgrr/`
- Format: `black rgrr/`
- Type check: `mypy rgrr/`

## Code Style
- Follow PEP 8 with 4-space indentation
- Import ordering: standard library, third-party, local imports
- Use type hints for all function parameters and return values
- Naming: snake_case for functions and variables, PascalCase for classes
- Error handling: Use specific exceptions, log errors appropriately
- Docstrings: Use Google-style docstrings for public functions
- Tests: Each test function should be isolated and cover edge cases