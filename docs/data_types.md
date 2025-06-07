# data_types

Data types and structures for Aurora SDK Python bindings.

## Import

```python
from slamtec_aurora_sdk import data_types
```

## Classes

### Vector3

**Inherits from:** ctypes.Structure

3D vector structure (slamtec_aurora_sdk_position3d_t).

#### Methods

**to_tuple**(self)

**to_numpy**(self)

### Quaternion

**Inherits from:** ctypes.Structure

Quaternion structure (slamtec_aurora_sdk_quaternion_t).

#### Methods

**to_tuple**(self)

**to_numpy**(self)

### EulerAngle

**Inherits from:** ctypes.Structure

Euler angle structure (slamtec_aurora_sdk_euler_angle_t).

#### Methods

**to_tuple**(self)

**to_numpy**(self)

### Pose

**Inherits from:** ctypes.Structure

Pose structure with translation and rotation (slamtec_aurora_sdk_pose_t).

#### Properties

**position**

**rotation**

### PoseSE3

**Inherits from:** ctypes.Structure

Pose structure in SE3 format (slamtec_aurora_sdk_pose_se3_t).

#### Properties

**position**

**rotation**

### ConnectionInfo

**Inherits from:** ctypes.Structure

Connection info structure (slamtec_aurora_sdk_connection_info_t).

### ServerConnectionInfo

**Inherits from:** ctypes.Structure

Server connection info structure (slamtec_aurora_sdk_server_connection_info_t).

### DeviceBasicInfo

**Inherits from:** ctypes.Structure

Device basic info structure (slamtec_aurora_sdk_device_basic_info_t).

### ImageDesc

**Inherits from:** ctypes.Structure

Image description structure (slamtec_aurora_sdk_image_desc_t).

### StereoImagePairDesc

**Inherits from:** ctypes.Structure

Stereo image pair description (slamtec_aurora_sdk_stereo_image_pair_desc_t).

### StereoImagePairBuffer

**Inherits from:** ctypes.Structure

Stereo image pair buffer (slamtec_aurora_sdk_stereo_image_pair_buffer_t).

### Keypoint

**Inherits from:** ctypes.Structure

Keypoint structure (slamtec_aurora_sdk_keypoint_t).

### TrackingDataBuffer

**Inherits from:** ctypes.Structure

Tracking data buffer (slamtec_aurora_sdk_tracking_data_buffer_t).

### TrackingInfo

**Inherits from:** ctypes.Structure

Tracking info structure (slamtec_aurora_sdk_tracking_info_t).

### LidarScanPoint

**Inherits from:** ctypes.Structure

Single LiDAR scan point.

### LidarScanData

**Inherits from:** ctypes.Structure

LiDAR scan data header.

### VersionInfo

**Inherits from:** ctypes.Structure

SDK version info structure.

### MapStorageSessionStatus

**Inherits from:** ctypes.Structure

Map storage session status structure (slamtec_aurora_sdk_mapstorage_session_status_t).

#### Methods

**is_finished**(self)

Check if session finished successfully.

**is_working**(self)

Check if session is currently working.

**is_idle**(self)

Check if session is idle.

**is_failed**(self)

Check if session failed.

**is_aborted**(self)

Check if session was aborted.

**is_rejected**(self)

Check if session was rejected.

**is_timeout**(self)

Check if session timed out.

**get_status_string**(self)

Get human-readable status string.

### IMUData

**Inherits from:** ctypes.Structure

IMU data structure (slamtec_aurora_sdk_imu_data_t).

#### Methods

**get_timestamp_seconds**(self)

Get timestamp in seconds (floating point).

**get_acceleration**(self)

Get acceleration as a tuple (x, y, z) in g units.

**get_gyroscope**(self)

Get gyroscope data as a tuple (x, y, z) in degrees per second.

**to_dict**(self)

Convert IMU data to dictionary.

**to_numpy**(self)

Convert IMU data to numpy arrays (if available).

#### Special Methods

**__str__**(self)

String representation of IMU data.

### DeviceBasicInfoWrapper

Python wrapper for device basic information matching C++ RemoteDeviceBasicInfo.

This class wraps slamtec_aurora_sdk_device_basic_info_t and provides
capability checking methods matching the C++ SDK interface.

#### Properties

**device_name**

Get device name.

**device_model_string**

Get device model string (e.g., 'A1M1', 'A2M1-r1').

**firmware_version**

Get firmware version string.

**firmware_build_date**

Get firmware build date.

**firmware_build_time**

Get firmware build time.

**hardware_version**

Get hardware version string.

**serial_number**

Get device serial number.

**model_major**

Get model major version.

**model_sub**

Get model sub version.

**model_revision**

Get model revision.

**device_uptime_us**

Get device uptime in microseconds.

**timestamp_ns**

Get timestamp when this info was retrieved.

**hwfeature_bitmaps**

Get hardware feature bitmaps.

**sensing_feature_bitmaps**

Get sensing feature bitmaps.

**swfeature_bitmaps**

Get software feature bitmaps.

#### Methods

**from_c_struct**(cls, c_struct, timestamp_ns)

Create DeviceBasicInfo from C structure.

**isSupportDepthCamera**(self)

Check if depth camera is supported.

Returns:
    bool: True if depth camera is supported, False otherwise

**isSupportSemanticSegmentation**(self)

Check if semantic segmentation is supported.

Returns:
    bool: True if semantic segmentation is supported, False otherwise

**isSupportCameraPreviewStream**(self)

Check if camera preview stream is supported.

Returns:
    bool: True if camera preview stream is supported, False otherwise

**isSupportVSLAM**(self)

Check if VSLAM is supported.

Returns:
    bool: True if VSLAM is supported, False otherwise

**isSupportCoMap**(self)

Check if CoMap (2D LIDAR mapping) is supported.

Returns:
    bool: True if CoMap is supported, False otherwise

**isSupportLiDAR**(self)

Check if LiDAR is supported.

Returns:
    bool: True if LiDAR is supported, False otherwise

**isSupportIMU**(self)

Check if IMU is supported.

Returns:
    bool: True if IMU is supported, False otherwise

**isSupportStereoCamera**(self)

Check if stereo camera is supported.

Returns:
    bool: True if stereo camera is supported, False otherwise

**isSupportEnhancedImaging**(self)

Check if enhanced imaging is supported.

Returns:
    bool: True if enhanced imaging is supported, False otherwise

#### Special Methods

**__init__**(self, c_struct, timestamp_ns)

Initialize from C structure.

### DeviceInfo

Legacy device info wrapper for backward compatibility.

#### Methods

**from_device_basic_info**(cls, device_basic_info)

Create legacy DeviceInfo from DeviceBasicInfo.

**from_c_struct**(cls, c_struct, timestamp_ns)

Create DeviceInfo from C structure (DeviceBasicInfo).

#### Special Methods

**__init__**(self, device_name, device_model_string, firmware_version, hardware_version, serial_number, model_major, model_sub, model_revision)

### DeviceStatus

**Inherits from:** ctypes.Structure

Device status information structure.

### RelocalizationStatus

**Inherits from:** ctypes.Structure

Relocalization status information structure.

### ImageFrame

Python wrapper for image frame data.

This class handles various image formats including regular images (grayscale, RGB, RGBA)
and depth data (float32 depth maps).

#### Methods

**from_c_desc**(cls, desc, data)

**from_depth_camera_struct**(cls, frame_desc, frame_data)

Create ImageFrame from depth camera C structures.

**from_point3d_struct**(cls, frame_desc, frame_data)

Create ImageFrame from point3d C structures.

**to_opencv_image**(self)

Convert image data to OpenCV-compatible numpy array.

Returns:
    numpy.ndarray: BGR image array ready for OpenCV, or None if no data
    
Note:
    Requires opencv-python and numpy to be installed.

**has_image_data**(self)

Check if this frame contains actual image data.

**is_depth_frame**(self)

Check if this frame contains depth data.

**is_point3d_frame**(self)

Check if this frame contains point3d data.

**to_numpy_depth_map**(self)

Convert depth data to numpy array.

Returns:
    numpy.ndarray: 2D array of float32 depth values, or None if not depth data

**to_colorized_depth_map**(self, colormap)

Convert depth map to colorized visualization.

Args:
    colormap: OpenCV colormap (default: cv2.COLORMAP_JET)
    
Returns:
    numpy.ndarray: Colorized depth map as BGR image

**to_point3d_array**(self)

Convert point3d data to numpy array of 3D points.

Returns:
    numpy.ndarray: Nx3 array of (x, y, z) points, or None if not point3d data

**to_point_cloud_data**(self)

Convert point3d data to point cloud format.

Returns:
    tuple: (points_xyz, valid_mask) where points_xyz is shaped (height, width, 3)
           and valid_mask indicates which points are valid (non-zero)

#### Special Methods

**__init__**(self, width, height, pixel_format, timestamp_ns, data, depth_scale, min_depth, max_depth)

### TrackingFrame

Python wrapper for tracking frame data.

#### Methods

**from_c_struct**(cls, tracking_info, left_keypoints, right_keypoints, left_image_data, right_image_data)

Create TrackingFrame from C structures.

**draw_keypoints_on_image**(self, opencv_image, image_side, color, radius)

Draw keypoints on a provided OpenCV image.

Args:
    opencv_image (numpy.ndarray): OpenCV image to draw keypoints on
    image_side (str): 'left' or 'right' to specify which keypoints to use
    color (tuple): BGR color for keypoints (default: green)
    radius (int): Radius of keypoint circles
    
Returns:
    numpy.ndarray: Image with keypoints drawn (modifies input image)
    
Note:
    Requires opencv-python to be installed.

**draw_keypoints**(self, image_side, color, radius)

Draw keypoints on the tracking frame's own image and return the result.

Args:
    image_side (str): 'left' or 'right' to specify which image to use
    color (tuple): BGR color for keypoints (default: green)
    radius (int): Radius of keypoint circles
    
Returns:
    numpy.ndarray: Image with keypoints drawn, or None if no image/keypoints
    
Note:
    Requires opencv-python and numpy to be installed.
    This method only works if the tracking frame has image data.

#### Special Methods

**__init__**(self, left_image, right_image, left_keypoints, right_keypoints, pose, timestamp_ns, tracking_status)

### ScanData

Python wrapper for LiDAR scan data.

#### Methods

**from_c_data**(cls, header, points)

#### Special Methods

**__init__**(self, timestamp_ns, points, ranges, angles)

### LidarScanData

Python wrapper for 2D LiDAR scan data.

#### Methods

**from_c_data**(cls, scan_info, scan_points)

Create LidarScanData from C structures.

**to_cartesian**(self)

Convert polar coordinates to cartesian (x, y) points.

**get_scan_count**(self)

Get the number of scan points.

**get_valid_points**(self)

Get only valid scan points (quality > 0).

#### Special Methods

**__init__**(self, timestamp_ns, layer_id, binded_kf_id, dyaw, points)

### GridMap2D

Python wrapper for 2D grid map data.

#### Methods

**get_cell_value**(self, x, y)

Get the value of a cell at grid coordinates (x, y).

**world_to_grid**(self, world_x, world_y)

Convert world coordinates to grid coordinates.

**grid_to_world**(self, grid_x, grid_y)

Convert grid coordinates to world coordinates.

**to_numpy**(self)

Convert grid data to numpy array (requires numpy).

#### Special Methods

**__init__**(self, width, height, resolution, origin_x, origin_y, data)

### GridMapGenerationOptions

**Inherits from:** ctypes.Structure

2D gridmap generation options structure (slamtec_aurora_sdk_2d_gridmap_generation_options_t).

### GlobalMapDesc

**Inherits from:** ctypes.Structure

Global map description structure (slamtec_aurora_sdk_global_map_desc_t).

### MapPointDesc

**Inherits from:** ctypes.Structure

Map point description structure (slamtec_aurora_sdk_map_point_desc_t).

### KeyframeDesc

**Inherits from:** ctypes.Structure

Keyframe description structure (slamtec_aurora_sdk_keyframe_desc_t).

### MapDesc

**Inherits from:** ctypes.Structure

Map description structure (slamtec_aurora_sdk_map_desc_t).

### MapDataVisitor

**Inherits from:** ctypes.Structure

Map data visitor structure (slamtec_aurora_sdk_map_data_visitor_t).

### GridMap2DDimension

**Inherits from:** ctypes.Structure

2D gridmap dimension structure (slamtec_aurora_sdk_2dmap_dimension_t).

### Rect

**Inherits from:** ctypes.Structure

Rectangle structure (slamtec_aurora_sdk_rect_t).

### GridMapGenerationOptions

**Inherits from:** ctypes.Structure

2D gridmap generation options (slamtec_aurora_sdk_2d_gridmap_generation_options_t).

### GridMap2DFetchInfo

**Inherits from:** ctypes.Structure

2D gridmap fetch info (slamtec_aurora_sdk_2d_gridmap_fetch_info_t).

### FloorDetectionDesc

**Inherits from:** ctypes.Structure

Floor detection description (slamtec_aurora_sdk_floor_detection_desc_t).

### FloorDetectionHistogramInfo

**Inherits from:** ctypes.Structure

Floor detection histogram info (slamtec_aurora_sdk_floor_detection_histogram_info_t).

### LidarScanPoint

**Inherits from:** ctypes.Structure

LiDAR scan point structure (slamtec_aurora_sdk_lidar_scan_point_t).

### LidarSinglelayerScanDataInfo

**Inherits from:** ctypes.Structure

LiDAR single layer scan data info (slamtec_aurora_sdk_lidar_singlelayer_scandata_info_t).

### GridMap2DDimension

**Inherits from:** ctypes.Structure

2D grid map dimension structure (slamtec_aurora_sdk_2dmap_dimension_t).

### GridMap2DGenerationOptions

**Inherits from:** ctypes.Structure

2D grid map generation options (slamtec_aurora_sdk_2d_gridmap_generation_options_t).

### SingleCameraCalibration

**Inherits from:** ctypes.Structure

Single camera calibration structure (slamtec_aurora_sdk_single_camera_calibration_t).

### ExtCameraTransform

**Inherits from:** ctypes.Structure

External camera transform structure (slamtec_aurora_sdk_ext_camera_transform_t).

### CameraCalibrationInfo

**Inherits from:** ctypes.Structure

Camera calibration info structure (slamtec_aurora_sdk_camera_calibration_t).

### TransformCalibrationInfo

**Inherits from:** ctypes.Structure

Transform calibration info structure (slamtec_aurora_sdk_transform_calibration_t).

### SemanticSegmentationConfig

**Inherits from:** ctypes.Structure

Semantic segmentation configuration structure.

### SemanticSegmentationLabelName

**Inherits from:** ctypes.Structure

Semantic segmentation label name structure.

### SemanticSegmentationLabelInfo

**Inherits from:** ctypes.Structure

Semantic segmentation label information structure.

### EnhancedImagingFrameDesc

**Inherits from:** ctypes.Structure

Enhanced imaging frame descriptor (slamtec_aurora_sdk_enhanced_imaging_frame_desc_t).

### EnhancedImagingFrameBuffer

**Inherits from:** ctypes.Structure

Enhanced imaging frame buffer (slamtec_aurora_sdk_enhanced_imaging_frame_buffer_t).

### DepthcamConfigInfo

**Inherits from:** ctypes.Structure

Depth camera configuration info (slamtec_aurora_sdk_depthcam_config_info_t).

### IMUInfo

**Inherits from:** ctypes.Structure

IMU information structure (slamtec_aurora_sdk_imu_info_t).

## Constants

- **ERRORCODE_OK** = `0`
- **ERRORCODE_OP_FAILED** = `<complex_value>`
- **ERRORCODE_INVALID_ARGUMENT** = `<complex_value>`
- **ERRORCODE_NOT_SUPPORTED** = `<complex_value>`
- **ERRORCODE_NOT_IMPLEMENTED** = `<complex_value>`
- **ERRORCODE_TIMEOUT** = `<complex_value>`
- **ERRORCODE_IO_ERROR** = `<complex_value>`
- **ERRORCODE_NOT_READY** = `<complex_value>`
- **ENHANCED_IMAGE_TYPE_NONE** = `0`
- **ENHANCED_IMAGE_TYPE_DEPTH** = `1`
- **ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION** = `2`
- **DEPTHCAM_FRAME_TYPE_DEPTH_MAP** = `0`
- **DEPTHCAM_FRAME_TYPE_POINT3D** = `1`
- **SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_LIDAR** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_IMU** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_STEREO_CAMERA** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_VSLAM** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_COMAP** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_STEREO_DENSE_DISPARITY** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_SEMANTIC_SEGMENTATION** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_CAMERA_PREVIEW_STREAM** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_ENHANCED_IMAGING** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_UPLOAD** = `0`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_DOWNLOAD** = `1`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FINISHED** = `2`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_WORKING** = `1`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_IDLE** = `0`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FAILED** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_KEYFRAME_FLAG_NONE** = `0`
- **SLAMTEC_AURORA_SDK_KEYFRAME_FLAG_BAD** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_KEYFRAME_FLAG_FIXED** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_MAP_FETCH_FLAG_ALL** = `4294967295`
- **SLAMTEC_AURORA_SDK_KF_FETCH_FLAG_ALL** = `4294967295`
- **SLAMTEC_AURORA_SDK_MP_FETCH_FLAG_ALL** = `4294967295`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_ABORTED** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_REJECTED** = `<complex_value>`
- **SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_TIMEOUT** = `<complex_value>`
- **NUMPY_AVAILABLE** = `True`
- **FORMAT_DEPTH_FLOAT32** = `100`
- **FORMAT_POINT3D_FLOAT32** = `101`
- **NUMPY_AVAILABLE** = `False`
