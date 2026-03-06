# listener

Aurora SDK listener bridge.

This module exposes a Python listener base class that mirrors the native
slamtec_aurora_sdk_listener_t callback surface.

## Import

```python
from slamtec_aurora_sdk import listener
```

## Classes

### SDKListener

Base listener for receiving asynchronous Aurora SDK callbacks.

Subclass this class and override the callbacks you need. All callbacks are
invoked on SDK-managed threads, so handlers should return quickly.

#### Properties

**native_listener**

Return the native listener structure kept alive by this instance.

#### Methods

**on_tracking_data**(self, tracking_frame)

Receive tracking frame updates.

**on_raw_image_data**(self, timestamp_ns, left_image, right_image)

Receive raw stereo image data.

**on_pose_augmentation_result**(self, timestamp_ns, mode, pose)

Receive augmented pose updates.

**on_imu_data**(self, imu_buffer)

Receive IMU samples.

**on_mapping_flags**(self, flags)

Receive mapping flag updates.

**on_device_status**(self, timestamp_ns, status)

Receive device status enum updates.

**on_lidar_scan**(self, scan_data)

Receive single-layer LiDAR scans.

**on_camera_preview_image**(self, timestamp_ns, left_image, right_image)

Receive camera preview frames.

**on_connection_status**(self, status)

Receive connection status updates.

**on_depth_camera_data_arrived**(self, timestamp_ns)

Receive depth camera availability notifications.

**on_semantic_segmentation_data_arrived**(self, timestamp_ns)

Receive semantic segmentation availability notifications.

**on_pose_covariance**(self, timestamp_ns, covariance)

Receive pose covariance updates.

#### Special Methods

**__init__**(self)

## Functions

**_copy_struct**(source)
