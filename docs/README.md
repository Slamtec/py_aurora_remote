# Aurora Python SDK Documentation

This directory contains the automatically generated API reference documentation for the SLAMTEC Aurora Python SDK.

## Documentation Formats

The documentation is available in two formats:

- **[HTML Documentation](index.html)** - Interactive web-based documentation with navigation
- **[Markdown Documentation](index.md)** - Text-based documentation for reading in editors

## Quick Navigation

### Core Components
- **[AuroraSDK](aurora_sdk.md)** - Main SDK class with component-based architecture
- **[Controller](controller.md)** - Device connection and control
- **[DataProvider](data_provider.md)** - Data acquisition (pose, images, sensors)
- **[MapManager](map_manager.md)** - VSLAM (3D visual mapping) operations
- **[LIDAR2DMapBuilder](lidar_2d_map_builder.md)** - 2D LIDAR mapping operations
- **[EnhancedImaging](enhanced_imaging.md)** - Advanced imaging features
- **[FloorDetector](floor_detector.md)** - Multi-floor detection

### Supporting Modules
- **[DataTypes](data_types.md)** - Data structures and type definitions
- **[Exceptions](exceptions.md)** - Exception classes and error handling
- **[Utils](utils.md)** - Utility functions and helpers
- **[C Bindings](c_bindings.md)** - Low-level C API bindings

## Updating Documentation

The documentation is automatically generated from the Python source code comments and docstrings. To update the documentation:

### Manual Update
```bash
# Generate both HTML and Markdown documentation
python3 tools/update_docs.py

# Generate only specific format
python3 tools/update_docs.py --format markdown
python3 tools/update_docs.py --format html

# Clean regeneration
python3 tools/update_docs.py --clean
```

### Advanced Options
```bash
# Verbose output
python3 tools/update_docs.py --verbose

# Skip backup creation
python3 tools/update_docs.py --no-backup

# Check if update is needed
python3 tools/update_docs.py --check-only
```

## Documentation Generation Process

The documentation is generated using the `tools/generate_docs.py` script which:

1. **Parses Python source files** using AST (Abstract Syntax Tree) analysis
2. **Extracts docstrings** from classes, methods, and functions
3. **Analyzes type hints** and function signatures
4. **Generates cross-references** between components
5. **Creates navigation** and table of contents
6. **Outputs formatted documentation** in HTML and Markdown

## Documentation Standards

To ensure high-quality documentation:

### Docstring Format
Use Google-style docstrings for consistency:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of the function.
    
    Longer description with more details about what the function does,
    its behavior, and any important notes.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter (default: 0)
    
    Returns:
        Description of the return value
        
    Raises:
        ValueError: When param1 is empty
        ConnectionError: When device is not connected
        
    Example:
        Basic usage example:
        
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    # Implementation here
    pass
```

### Class Documentation
Document classes with:
- Purpose and responsibility
- Usage examples
- Relationship to other components
- Important notes or limitations

### Type Hints
Use comprehensive type hints for:
- Function parameters
- Return values
- Class attributes
- Complex data structures

## Integration with CI/CD

The documentation update script can be integrated into continuous integration:

```yaml
# Example GitHub Actions workflow
name: Update Documentation
on:
  push:
    paths:
      - 'python_bindings/slamtec_aurora_sdk/**/*.py'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - name: Update documentation
        run: python3 tools/update_docs.py --format both
      - name: Commit changes
        run: |
          git add docs/
          git commit -m "Auto-update API documentation" || exit 0
          git push
```

## Contributing to Documentation

When contributing to the SDK:

1. **Write comprehensive docstrings** for all public classes and methods
2. **Include usage examples** in docstrings where helpful
3. **Update type hints** when changing function signatures
4. **Test documentation generation** locally before submitting
5. **Review generated documentation** for accuracy and completeness

## Troubleshooting

### Common Issues

**Documentation generation fails:**
- Check Python syntax in source files
- Ensure all imports are available
- Verify write permissions to docs directory

**Missing documentation for new modules:**
- Ensure module has a proper docstring
- Check that module is included in `__init__.py`
- Verify module naming follows conventions

**Broken cross-references:**
- Check class and method names for typos
- Ensure proper import statements
- Verify component relationships

### Debug Mode

For detailed debugging information:
```bash
python3 tools/generate_docs.py --format markdown --output docs 2>&1 | tee debug.log
```

---

*This documentation is automatically generated from source code. Last updated: [Generated automatically]*