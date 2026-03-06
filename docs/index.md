# SLAMTEC Aurora Python SDK API Reference

This is the automatically generated API reference for the SLAMTEC Aurora Python SDK.

## Components

- **[aurora_sdk](aurora_sdk.md)** - Aurora SDK v2 - Component-based architecture.
- **[controller](controller.md)** - Aurora SDK Controller component.
- **[data_provider](data_provider.md)** - Aurora SDK DataProvider component.
- **[enhanced_imaging](enhanced_imaging.md)** - Aurora SDK Enhanced Imaging component.
- **[floor_detector](floor_detector.md)** - Floor Detector module for Aurora SDK.
- **[lidar_2d_map_builder](lidar_2d_map_builder.md)** - Aurora SDK LIDAR2DMapBuilder component.
- **[map_manager](map_manager.md)** - Aurora SDK MapManager component.
- **[transform_manager](transform_manager.md)** - Transform manager for Aurora SDK 2.1.1.
- **[camera_mask](camera_mask.md)** - Camera mask management for Aurora SDK 2.1.1.
- **[dashcam_recorder](dashcam_recorder.md)** - Dashcam recorder management for Aurora SDK 2.1.1.
- **[data_recorder](data_recorder.md)** - Aurora SDK DataRecorder component.
- **[listener](listener.md)** - Aurora SDK listener bridge.
- **[persistent_config](persistent_config.md)** - Persistent configuration management for Aurora SDK 2.1.1.
- **[timesync](timesync.md)** - Standalone time synchronization client for Aurora SDK 2.1.1.
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
sdk.connect(connection_string="192.168.11.1")

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
- **EnhancedImaging**: Aurora SDK Enhanced Imaging component.
- **FloorDetector**: Floor Detector module for Aurora SDK.
- **LIDAR2DMapBuilder**: Aurora SDK LIDAR2DMapBuilder component.
- **MapManager**: Aurora SDK MapManager component.
- **TransformManager**: Transform manager for Aurora SDK 2.1.1.
- **CameraMask**: Camera mask management for Aurora SDK 2.1.1.
- **DashcamRecorder**: Dashcam recorder management for Aurora SDK 2.1.1.
- **DataRecorder**: Aurora SDK DataRecorder component.
- **Listener**: Aurora SDK listener bridge.
- **PersistentConfig**: Persistent configuration management for Aurora SDK 2.1.1.
- **Timesync**: Standalone time synchronization client for Aurora SDK 2.1.1.

*Documentation generated automatically from source code*