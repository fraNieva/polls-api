.PHONY: test test-unit test-integration test-cov test-watch clean

# Activate virtual environment
activate:
	source venv/bin/activate

# Run dev server
run:
	./venv/bin/python -m uvicorn main:app --reload

# Run all tests
test:
	./venv/bin/python -m pytest

# Run tests with verbose output
test-verbose:
	./venv/bin/python -m pytest -v

# Run only unit tests
test-unit:
	./venv/bin/python -m pytest -m unit -v

# Run only integration tests  
test-integration:
	./venv/bin/python -m pytest -m integration -v

# Run tests with coverage report
test-cov:
	./venv/bin/python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
test-setup:
	./venv/bin/python -m pytest tests/test_setup.py -v

# Clean up test artifacts
clean:
	rm -rf .pytest_cache __pycache__ htmlcov .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +