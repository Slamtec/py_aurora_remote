# SLAMTEC Aurora Python SDK API Reference

This is the automatically generated API reference for the SLAMTEC Aurora Python SDK.

## Components

- **[aurora_sdk](aurora_sdk.md)** - Aurora SDK v2 - Component-based architecture.
- **[controller](controller.md)** - Aurora SDK Controller component.
- **[data_provider](data_provider.md)** - Aurora SDK DataProvider component.
- **[enhanced_imaging](enhanced_imaging.md)** - Aurora SDK Enhanced Imaging component (SDK 2.
- **[floor_detector](floor_detector.md)** - Floor Detector module for Aurora SDK.
- **[lidar_2d_map_builder](lidar_2d_map_builder.md)** - Aurora SDK LIDAR2DMapBuilder component.
- **[map_manager](map_manager.md)** - Aurora SDK MapManager component.
- **[data_types](data_types.md)** - Data types and structures for Aurora SDK Python bindings.
- **[exceptions](exceptions.md)** - Exception classes for Aurora SDK Python bindings.
- **[utils](utils.md)** - Aurora SDK Utility Functions

This module contains helper functions and utilities for common operations
with the Aurora SDK, such as map synchronization checking, data processing,
status monitoring, and semantic segmentation utilities.
- **[c_bindings](c_bindings.md)** - Low-level C bindings for Aurora SDK using ctypes.

## Quick Start

```python
from slamtec_aurora_sdk import AuroraSDK

# Create SDK instance
sdk = AuroraSDK()

# Connect to device
sdk.connect(connection_string="192.168.1.212")

# Get data
pose = sdk.data_provider.get_current_pose()
left_img, right_img = sdk.data_provider.get_camera_preview()

# Cleanup
sdk.disconnect()
sdk.release()
```

## Architecture

The Aurora Python SDK follows a component-based architecture:

- **AuroraSDK**: Aurora SDK v2 - Component-based architecture.
- **Controller**: Aurora SDK Controller component.
- **DataProvider**: Aurora SDK DataProvider component.
- **EnhancedImaging**: Aurora SDK Enhanced Imaging component (SDK 2.
- **FloorDetector**: Floor Detector module for Aurora SDK.
- **LIDAR2DMapBuilder**: Aurora SDK LIDAR2DMapBuilder component.
- **MapManager**: Aurora SDK MapManager component.

*Documentation generated automatically from source code*