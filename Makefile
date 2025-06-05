# SLAMTEC Aurora Python SDK Makefile
# Provides convenient commands for common development tasks

.PHONY: help docs docs-clean docs-html docs-markdown test clean build install dev-install

# Default target
help:
	@echo "SLAMTEC Aurora Python SDK - Available commands:"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs         - Generate both HTML and Markdown documentation"
	@echo "  make docs-html    - Generate HTML documentation only"
	@echo "  make docs-markdown - Generate Markdown documentation only"
	@echo "  make docs-clean   - Clean and regenerate documentation"
	@echo "  make docs-check   - Check if documentation needs updating"
	@echo ""
	@echo "Development:"
	@echo "  make dev-install  - Install SDK in development mode"
	@echo "  make build        - Build wheel packages for all platforms"
	@echo "  make build-current - Build wheel package for current platform"
	@echo "  make clean        - Clean build artifacts"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run basic SDK tests"
	@echo "  make examples     - List available examples"
	@echo ""

# Documentation targets
docs:
	@echo "Generating API documentation (HTML + Markdown)..."
	python3 tools/update_docs.py --format both

docs-html:
	@echo "Generating HTML documentation..."
	python3 tools/update_docs.py --format html

docs-markdown:
	@echo "Generating Markdown documentation..."
	python3 tools/update_docs.py --format markdown

docs-clean:
	@echo "Cleaning and regenerating documentation..."
	python3 tools/update_docs.py --clean --format both

docs-check:
	@echo "Checking if documentation needs updating..."
	python3 tools/update_docs.py --check-only

# Build targets
build:
	@echo "Building wheel packages for all platforms..."
	python3 tools/build_package.py --all-platforms --clean

build-current:
	@echo "Building wheel package for current platform..."
	python3 tools/build_package.py --clean

build-test:
	@echo "Building and testing wheel package..."
	python3 tools/build_package.py --test --clean

# Development targets
dev-install:
	@echo "Installing SDK in development mode..."
	cd python_bindings && pip install -e .

install:
	@echo "Installing SDK from built wheel..."
	@if [ -d "wheels" ]; then \
		latest_wheel=$$(ls -t wheels/*.whl | head -n1); \
		echo "Installing $$latest_wheel"; \
		pip install "$$latest_wheel"; \
	else \
		echo "No wheels found. Run 'make build' first."; \
		exit 1; \
	fi

# Clean targets
clean:
	@echo "Cleaning build artifacts..."
	rm -rf python_bindings/build
	rm -rf python_bindings/dist
	rm -rf python_bindings/*.egg-info
	find python_bindings -name "*.pyc" -delete
	find python_bindings -name "__pycache__" -type d -exec rm -rf {} +
	@echo "Cleaned build artifacts"

clean-docs:
	@echo "Cleaning documentation..."
	rm -rf docs/*.html docs/*.md
	@echo "Documentation cleaned"

clean-all: clean clean-docs
	@echo "Cleaned all generated files"

# Testing targets
test:
	@echo "Running basic SDK tests..."
	@echo "Testing package imports..."
	cd python_bindings && python3 -c "import slamtec_aurora_sdk; print('✓ SDK import successful')"
	@echo "Testing SDK initialization..."
	cd python_bindings && python3 -c "from slamtec_aurora_sdk import AuroraSDK; sdk = AuroraSDK(); print('✓ SDK initialization successful'); sdk.release()"
	@echo "All tests passed!"

examples:
	@echo "Available examples:"
	@find examples -name "*.py" | sort | sed 's/^/  /'
	@echo ""
	@echo "Run examples with: python examples/<example_name>.py [device_ip]"

# Utility targets
version:
	@python3 -c "import sys; sys.path.insert(0, 'python_bindings'); from slamtec_aurora_sdk import __version__; print('Aurora SDK Version:', __version__)"

check-deps:
	@echo "Checking Python dependencies..."
	@python3 -c "import numpy; print('✓ numpy')"
	@python3 -c "import cv2; print('✓ opencv-python')" 2>/dev/null || echo "⚠ opencv-python (optional)"
	@python3 -c "import open3d; print('✓ open3d')" 2>/dev/null || echo "⚠ open3d (optional)"
	@echo "Dependency check complete"

# Git integration
docs-commit:
	@echo "Committing documentation changes..."
	git add docs/
	git commit -m "Update API documentation" || echo "No documentation changes to commit"

# Combined targets
full-build: clean build docs
	@echo "Full build completed (packages + documentation)"

release-prep: clean build docs test
	@echo "Release preparation completed"
	@echo "- Packages built: $$(ls wheels/*.whl | wc -l) wheels"
	@echo "- Documentation: $$(ls docs/*.html docs/*.md | wc -l) files"
	@echo "- Tests: passed"

# Development workflow
dev-setup:
	@echo "Setting up development environment..."
	pip install -r requirements-dev.txt
	pip install -r python_bindings/requirements.txt
	make dev-install
	make docs
	@echo "Development environment ready!"