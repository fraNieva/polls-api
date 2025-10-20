.PHONY: test test-unit test-integration test-cov test-watch clean

# Run all tests
test:
    pytest

# Run tests with verbose output
test-verbose:
    pytest -v

# Run only unit tests
test-unit:
    pytest -m unit -v

# Run only integration tests  
test-integration:
    pytest -m integration -v

# Run tests with coverage report
test-cov:
    pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
test-setup:
    pytest tests/test_setup.py -v

# Clean up test artifacts
clean:
    rm -rf .pytest_cache __pycache__ htmlcov .coverage
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +