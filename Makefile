.PHONY: install test clean setup help

help:
	@echo "Available commands:"
	@echo "  setup    - Set up the development environment"
	@echo "  install  - Install the package in development mode"
	@echo "  test     - Run a test citation check"
	@echo "  clean    - Clean up generated files"

setup:
	pip install -r requirements.txt
	@echo "Setup complete! Now add your API key to .env file"

install:
	pip install -e .

test:
	@echo "Testing with a sample citation..."
	python citecheck.py "Roe v. Wade"

clean:
	rm -rf __pycache__/
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/ 