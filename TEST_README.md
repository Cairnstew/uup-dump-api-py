# UUP Dump API Test Suite

Comprehensive test suite for the UUP Dump API Python wrapper module.

## Overview

This test suite provides thorough coverage of:
- ✅ Exception handling and custom exceptions
- ✅ REST adapter functionality
- ✅ API method calls and parameter handling
- ✅ Error response handling
- ✅ Timeout and connection error handling
- ✅ Logging functionality
- ✅ Edge cases and error conditions
- ✅ Integration workflows

## Test Statistics

- **Total Test Classes**: 8
- **Total Test Methods**: 50+
- **Coverage Target**: >90%

## Running Tests Locally

### Prerequisites

```bash
# Install testing dependencies
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Basic test run
pytest test_uup_dump_api.py -v

# With coverage report
pytest test_uup_dump_api.py -v --cov=. --cov-report=html

# Parallel execution (faster)
pytest test_uup_dump_api.py -v -n auto

# With detailed output
pytest test_uup_dump_api.py -vv --tb=short
```

### Run Specific Test Classes

```bash
# Test only exceptions
pytest test_uup_dump_api.py::TestExceptions -v

# Test only REST adapter methods
pytest test_uup_dump_api.py::TestRestAdapterMethods -v

# Test only error handling
pytest test_uup_dump_api.py::TestRestAdapterGetMethod -v
```

### Run Specific Tests

```bash
# Run a single test
pytest test_uup_dump_api.py::TestExceptions::test_http_error -v

# Run tests matching a pattern
pytest test_uup_dump_api.py -k "timeout" -v
```

## Test Organization

### Test Classes

1. **TestExceptions**: Tests all custom exception classes
   - Base exception functionality
   - HTTP errors with status codes
   - Validation, timeout, connection errors
   - Response errors with API codes

2. **TestErrorMessages**: Tests error message mapping
   - Known error code handling
   - Unknown error code handling
   - Error message dictionary validation

3. **TestRestAdapterInit**: Tests adapter initialization
   - Default parameters
   - Custom timeout and log levels
   - Logger configuration

4. **TestRestAdapterGetMethod**: Tests the internal `_get` method
   - Successful requests
   - Parameter passing
   - Timeout handling
   - Connection errors
   - HTTP errors
   - Invalid JSON responses
   - API error responses

5. **TestRestAdapterMethods**: Tests all public API methods
   - `listid()` - List updates
   - `fetchupd()` - Fetch update info
   - `get_files()` - Get update files
   - `list_editions()` - List editions
   - `list_langs()` - List languages
   - `update_info()` - Get update details
   - `api_version()` - Get API version

6. **TestLogging**: Tests logging functionality
   - Logger existence
   - Debug logging
   - Error logging

7. **TestEdgeCases**: Tests edge cases and boundary conditions
   - Empty responses
   - Missing response keys
   - Response body truncation
   - Zero/negative timeouts

8. **TestIntegration**: Integration tests
   - Multi-step workflows
   - Error recovery patterns

## GitHub Actions Integration

The test suite is designed to run automatically in GitHub Actions on:
- Every push to `main` or `develop` branches
- Every pull request
- Manual workflow dispatch

### Workflow Features

✅ **Multi-OS Testing**: Ubuntu, Windows, macOS
✅ **Multi-Python Testing**: Python 3.8, 3.9, 3.10, 3.11, 3.12
✅ **Code Coverage**: Automatic coverage reporting to Codecov
✅ **Linting**: flake8, pylint, black, isort checks
✅ **Security Scanning**: bandit and safety checks
✅ **Parallel Execution**: Fast test execution with matrix strategy

### Setting Up GitHub Actions

1. Copy the workflow file to your repository:
```bash
mkdir -p .github/workflows
cp .github_workflows_tests.yml .github/workflows/tests.yml
```

2. Commit and push:
```bash
git add .github/workflows/tests.yml
git commit -m "Add test workflow"
git push
```

3. (Optional) Set up Codecov:
   - Sign up at https://codecov.io
   - Add your repository
   - No token needed for public repos

## Code Coverage

Generate HTML coverage report:

```bash
pytest test_uup_dump_api.py --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

View coverage in terminal:

```bash
pytest test_uup_dump_api.py --cov=. --cov-report=term-missing
```

## Continuous Integration Best Practices

### Pre-commit Checks

Before committing, run:

```bash
# Run tests
pytest test_uup_dump_api.py -v

# Check code style
black --check .
isort --check-only .
flake8 .

# Run security scan
bandit -r . -f screen
```

### Local CI Simulation

Test what will run in CI:

```bash
# Install all test dependencies
pip install -r requirements-test.txt

# Run the full test suite
pytest test_uup_dump_api.py -v --cov=. --cov-report=term

# Run linters
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
pylint *.py --disable=C,R

# Run security checks
bandit -r .
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'exceptions'`
**Solution**: Ensure the test file is in the same directory as the module files, or adjust the import path.

**Issue**: Tests fail with network errors
**Solution**: The tests use mocking and don't require actual network access. Check that `pytest-mock` is installed.

**Issue**: Coverage is lower than expected
**Solution**: Ensure all module files are in the coverage source path. Check `pytest.ini` and `.coveragerc` configurations.

## Contributing

When adding new features to the module:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >90% code coverage
4. Update this README if adding new test classes

## Test Philosophy

These tests follow best practices:

- ✅ **Isolated**: Each test is independent
- ✅ **Fast**: Uses mocking to avoid network calls
- ✅ **Comprehensive**: Tests both success and failure paths
- ✅ **Maintainable**: Clear test names and organization
- ✅ **Documented**: Docstrings explain what each test does

## License

These tests are part of the UUP Dump API Python module project.