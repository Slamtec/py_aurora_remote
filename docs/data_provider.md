# data_provider

Aurora SDK DataProvider component.

Handles data retrieval operations including pose, images, tracking data, and sensor data.

## Import

```python
from slamtec_aurora_sdk import data_provider
```

## Classes

### DataProvider

DataProvider component for Aurora SDK.

Responsible for:
- Pose data retrieval (current pose, pose history)
- Camera image data (preview, tracking frames)
- LiDAR scan data
- IMU sensor data
- Tracking and mapping data

#### Methods

**get_current_pose**(self, use_se3)

Get current device pose.

Args:
    use_se3: If True, return SE3 format (position + quaternion),
            if False, return Euler format (position + euler angles)
            
Returns:
    Tuple of (position, rotation, timestamp_ns)
    - position: (x, y, z) tuple
    - rotation: (qx, qy, qz, qw) if use_se3, (roll, pitch, yaw) otherwise
    - timestamp_ns: timestamp in nanoseconds
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get pose

**get_camera_preview**(self)

Get camera preview frames.

Returns:
    Tuple of (left_frame, right_frame) ImageFrame objects
    
Raises:
    ConnectionError: If not connected to a device
    DataNotReadyError: If camera data is not ready
    AuroraSDKError: If failed to get camera preview

**get_tracking_frame**(self)

Get tracking frame data with keypoints and images.

Returns:
    TrackingFrame object containing images, keypoints, pose, and tracking status
    
Raises:
    ConnectionError: If not connected to a device
    DataNotReadyError: If tracking data is not ready
    AuroraSDKError: If failed to get tracking data

**get_recent_lidar_scan**(self, max_points)

Get recent LiDAR scan data.

Args:
    max_points: Maximum number of scan points to retrieve
    
Returns:
    LidarScanData object containing scan points and metadata, or None if not available
    
Raises:
    ConnectionError: If not connected to a device
    DataNotReadyError: If LiDAR data is not ready
    AuroraSDKError: If failed to get scan data

**get_imu_data**(self)

Get IMU sensor data.

Returns:
    List of IMUData objects containing accelerometer and gyroscope data
    
Raises:
    ConnectionError: If not connected to a device
    DataNotReadyError: If IMU data is not ready
    AuroraSDKError: If failed to get IMU data

**peek_imu_data**(self, max_count)

Peek at cached IMU data from the device.

This method retrieves IMU data that has been cached by the SDK.
It's non-blocking and returns immediately with available data.
The C++ SDK returns immediately with the actual count of samples retrieved,
regardless of whether the max_count is reached.

Args:
    max_count (int): Maximum number of IMU samples to retrieve (default: 100)
    
Returns:
    List of IMUData objects containing accelerometer and gyroscope data
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get IMU data

**get_map_data**(self)

Get visual map data including map points and keyframes.

Returns:
    dict: Dictionary containing 'map_points' and 'keyframes' lists
    
Raises:
    ConnectionError: If not connected to a device
    DataNotReadyError: If map data is not ready
    AuroraSDKError: If failed to get map data

**peek_recent_lidar_scan_raw**(self)

Get the most recent LiDAR scan data in raw format.

Returns:
    tuple: (scan_info, scan_points) or None if not available

**get_global_mapping_info**(self)

Get global mapping information from the device.

This exposes the complete slamtec_aurora_sdk_global_map_desc_t structure
with all available fields for map status monitoring and processing.

Returns:
    dict: Complete global mapping information with all fields:
        - lastMPCountToFetch: Last map point count to fetch
        - lastKFCountToFetch: Last keyframe count to fetch  
        - lastMapCountToFetch: Last map count to fetch
        - lastMPRetrieved: Last map point retrieved
        - lastKFRetrieved: Last keyframe retrieved
        - totalMPCount: Total map point count
        - total_kf_count: Total keyframe count
        - totalMapCount: Total map count
        - totalMPCountFetched: Total map points fetched
        - total_kf_count_fetched: Total keyframes fetched
        - totalMapCountFetched: Total maps fetched
        - currentActiveMPCount: Current active map point count
        - currentActiveKFCount: Current active keyframe count
        - active_map_id: Active map ID
        - mappingFlags: Mapping flags
        - slidingWindowStartKFId: Sliding window start keyframe ID

**get_camera_calibration**(self)

Get camera calibration parameters from the device.

Returns:
    CameraCalibrationInfo: Camera calibration data including intrinsic and extrinsic parameters
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve calibration data

**get_transform_calibration**(self)

Get transform calibration parameters from the device.

Returns:
    TransformCalibrationInfo: Transform calibration data including camera-to-LiDAR transforms
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve transform calibration data

**get_last_device_basic_info**(self)

Get the last device basic information.

Returns:
    DeviceBasicInfoWrapper: Device basic information wrapper with capability checking methods
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve device basic info

**get_device_info**(self)

Get device information (legacy compatibility method).

Returns:
    DeviceInfo: Legacy device info for backward compatibility
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve device info

**get_last_device_status**(self)

Get the last device status information.

Returns:
    Tuple of (DeviceStatus, timestamp_ns): Device status and timestamp
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve device status

**get_relocalization_status**(self)

Get relocalization status information.

Returns:
    RelocalizationStatus: Current relocalization status
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve relocalization status

**get_mapping_flags**(self)

Get current mapping flags.

Returns:
    int: Current mapping flags as bitmask
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve mapping flags

**get_imu_info**(self)

Get IMU information.

Returns:
    IMUInfo: IMU configuration and capabilities
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve IMU info

**get_all_map_info**(self, max_count)

Get information about all maps.

Args:
    max_count (int): Maximum number of maps to retrieve (default: 32)
    
Returns:
    list: List of MapDesc objects containing map information
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve map info

**peek_history_pose**(self, timestamp_ns, allow_interpolation, max_time_diff_ns)

Peek historical pose at specific timestamp.

Args:
    timestamp_ns (int): Timestamp in nanoseconds (0 for latest)
    allow_interpolation (bool): Allow pose interpolation (default: True)
    max_time_diff_ns (int): Maximum time difference in nanoseconds (default: 1 second)
    
Returns:
    PoseSE3: Historical pose data
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve historical pose

#### Special Methods

**__init__**(self, controller, c_bindings)

Initialize DataProvider component.

Args:
    controller: Controller component instance
    c_bindings: Optional C bindings instance
