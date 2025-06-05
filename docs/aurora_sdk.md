# aurora_sdk

Aurora SDK v2 - Component-based architecture.

This is the new component-based implementation following C++ SDK patterns.

## Import

```python
from slamtec_aurora_sdk import aurora_sdk
```

## Classes

### AuroraSDK

Aurora SDK main class with component-based architecture.

This class provides access to Aurora device functionality through separate
components following the C++ SDK design pattern:
- Controller: Device connection and control
- DataProvider: Data retrieval (pose, images, sensors)
- MapManager: VSLAM (3D visual mapping) operations
- LIDAR2DMapBuilder: CoMap (2D LIDAR mapping) operations
- EnhancedImaging: Enhanced imaging features (depth camera, semantic segmentation)

Example usage:
    sdk = AuroraSDK()
    sdk.controller.connect(connection_string="192.168.1.212")
    
    # Get camera preview and tracking data
    left_img, right_img = sdk.data_provider.get_camera_preview()
    tracking_frame = sdk.data_provider.get_tracking_frame()
    
    # VSLAM operations
    sdk.map_manager.save_vslam_map("my_map.vslam")
    
    # 2D LIDAR mapping (CoMap)
    sdk.lidar_2d_map_builder.start_lidar_2d_map_preview()

#### Properties

**controller**

Get the Controller component.

The Controller handles:
- Device discovery and connection
- Session management
- Device control operations
- Configuration management

Returns:
    Controller: Controller component instance

**data_provider**

Get the DataProvider component.

The DataProvider handles:
- Pose data retrieval
- Camera image data
- LiDAR scan data
- IMU sensor data
- Tracking data

Returns:
    DataProvider: DataProvider component instance

**map_manager**

Get the MapManager component.

The MapManager component handles VSLAM (3D visual mapping):
- VSLAM map creation and management
- 3D SLAM operations
- Relocalization in VSLAM maps
- VSLAM map file operations

Returns:
    MapManager: MapManager component instance

**lidar_2d_map_builder**

Get the LIDAR2DMapBuilder component.

The LIDAR2DMapBuilder component handles CoMap (2D LIDAR mapping):
- 2D occupancy grid map generation
- Real-time 2D map preview
- 2D LIDAR map management
- CoMap configuration and rendering

Returns:
    LIDAR2DMapBuilder: LIDAR2DMapBuilder component instance

**floor_detector**

Get the FloorDetector component.

The FloorDetector handles:
- Auto floor detection histogram
- Floor descriptions and current floor
- Multi-floor environment detection

Returns:
    FloorDetector: FloorDetector component instance

**enhanced_imaging**

Get the EnhancedImaging component (SDK 2.0).

The EnhancedImaging component handles:
- Depth camera frame retrieval and processing
- Semantic segmentation frame retrieval and processing
- Camera calibration data access
- Transform calibration data access
- Model switching for semantic segmentation
- Depth-aligned segmentation map calculation

Returns:
    EnhancedImaging: EnhancedImaging component instance

#### Methods

**create_session**(self)

Convenience helper: Create SDK session.

NOTE: Session is created automatically during SDK initialization.
This method is deprecated and should not be called manually.

Raises:
    AuroraSDKError: If session is already created

**connect**(self, device_info, connection_string)

Convenience helper: Connect to an Aurora device.

Args:
    device_info: Device info from discovery (preferred)
    connection_string: Direct connection string (fallback)
    
Raises:
    ConnectionError: If connection fails
    AuroraSDKError: If session not created or invalid parameters

**disconnect**(self)

Convenience helper: Disconnect from current device.

**is_connected**(self)

Convenience helper: Check if connected to a device.

Returns:
    bool: True if connected, False otherwise

**discover_devices**(self, timeout)

Convenience helper: Discover Aurora devices on the network.

Args:
    timeout: Discovery timeout in seconds
    
Returns:
    List of discovered device information dictionaries

**get_version_info**(self)

Convenience helper: Get SDK version information.

Returns:
    dict containing version information

**connect_and_start**(self, connection_string, auto_discover)

Convenience method to create session and connect to device.

Args:
    connection_string: Optional specific device to connect to
    auto_discover: If True, discover devices if connection_string not provided
    
Returns:
    bool: True if successfully connected
    
Raises:
    AuroraSDKError: If connection fails

**get_device_status**(self)

Get comprehensive device status information.

Returns:
    dict: Device status including connection state, device info, etc.

**quick_start_preview**(self, connection_string)

Quick start method for camera preview applications.

Args:
    connection_string: Optional specific device to connect to
    
Returns:
    bool: True if successfully started

**release**(self)

Convenience helper: Release SDK session and cleanup resources.

This method provides a simple way to cleanup the SDK session,
disconnecting from the device if connected and releasing the session.

**get_device_info**(self)

Convenience helper: Get device information.

Returns:
    Device information object

**get_current_pose**(self, use_se3)

Convenience helper: Get current device pose.

Args:
    use_se3: If True, return pose in SE3 format (position + quaternion)
            If False, return pose in Euler format (position + roll/pitch/yaw)
            
Returns:
    tuple: (position, rotation, timestamp) where:
        - position: (x, y, z) coordinates
        - rotation: (qx, qy, qz, qw) quaternion if use_se3=True, 
                   (roll, pitch, yaw) Euler angles if use_se3=False
        - timestamp: timestamp in nanoseconds

**get_tracking_frame**(self)

Convenience helper: Get tracking frame with images and keypoints.

Returns:
    TrackingFrame object with left/right images and keypoints

**get_camera_preview**(self)

Convenience helper: Get camera preview images.

Returns:
    tuple: (left_image, right_image) as ImageFrame objects

**get_map_info**(self)

Convenience helper: Get map information.

Returns:
    dict: Map information including status, count, etc.

**get_recent_lidar_scan**(self, max_points)

Convenience helper: Get recent LiDAR scan data.

Args:
    max_points: Maximum number of scan points to retrieve

Returns:
    LidarScanData object with scan points and metadata

**start_lidar_2d_map_preview**(self, resolution)

Convenience helper: Start LIDAR 2D map preview generation.

Args:
    resolution: Map resolution in meters per pixel (default: 0.05m = 5cm)

**stop_lidar_2d_map_preview**(self)

Convenience helper: Stop LIDAR 2D map preview generation.

**enable_map_data_syncing**(self, enable)

Convenience helper: Enable/disable map data syncing.

Args:
    enable: True to enable, False to disable

**get_map_data**(self)

Convenience helper: Get visual map data (map points and keyframes).

Returns:
    dict: Dictionary containing 'map_points' and 'keyframes' lists

**require_mapping_mode**(self, timeout_ms)

Convenience helper: Require device to enter mapping mode.

Args:
    timeout_ms: Timeout in milliseconds

**resync_map_data**(self, invalidate_cache)

Convenience helper: Force resync of map data.

Args:
    invalidate_cache: Whether to invalidate cache

**convert_quaternion_to_euler**(self, qx, qy, qz, qw)

Convert quaternion to Euler angles.

Args:
    qx, qy, qz, qw: Quaternion components
    
Returns:
    tuple: (roll, pitch, yaw) in radians
    
Raises:
    AuroraSDKError: If conversion fails

#### Special Methods

**__init__**(self)

Initialize Aurora SDK with component-based architecture.

**__enter__**(self)

Context manager entry.

**__exit__**(self, exc_type, exc_val, exc_tb)

Context manager exit with automatic cleanup.

**__del__**(self)

Destructor to ensure proper cleanup when object is garbage collected.
