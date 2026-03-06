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
- **[Persistent Config](persistent_config.md)** - Persistent JSON configuration management
- **[Transform Manager](transform_manager.md)** - Device-side SE3 transform management
- **[Camera Mask](camera_mask.md)** - Static camera mask management
- **[Dashcam Recorder](dashcam_recorder.md)** - Datalogger status and storage control
- **[Listener](listener.md)** - Asynchronous SDK listener bridge
- **[Time Sync](timesync.md)** - Standalone Aurora time synchronization client

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
python3 tools/generate_docs.py --format both

# Generate only specific format
python3 tools/generate_docs.py --format markdown
python3 tools/generate_docs.py --format html

# Clean regeneration
python3 tools/generate_docs.py --format both --clean
```

### Advanced Options
```bash
# Verbose output
python3 tools/generate_docs.py --format both --verbose

# Skip backup creation
python3 tools/generate_docs.py --format both --no-backup

# Check if update is needed
python3 tools/generate_docs.py --check-only
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

Consider integrating documentation generation into your CI/CD pipeline:

```bash
# Check if docs need updating after code changes
python3 tools/generate_docs.py --check-only

# Regenerate docs as part of release workflow
python3 tools/generate_docs.py --format both --clean
```
