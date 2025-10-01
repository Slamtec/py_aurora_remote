# enhanced_imaging

Aurora SDK Enhanced Imaging component (SDK 2.0).

Handles Enhanced Imaging operations including depth camera frames, semantic segmentation,
camera calibration, and transform calibration.

## Import

```python
from slamtec_aurora_sdk import enhanced_imaging
```

## Classes

### EnhancedImaging

Enhanced Imaging component for Aurora SDK 2.0.

Responsible for:
- Depth camera frame retrieval and processing
- Semantic segmentation frame retrieval and processing
- Camera calibration data access
- Transform calibration data access
- Model switching for semantic segmentation
- Depth-aligned segmentation map calculation

#### Methods

**is_depth_camera_ready**(self)

Check if depth camera is ready for frame capture.

Returns:
    bool: True if depth camera is ready, False otherwise

**wait_depth_camera_next_frame**(self, timeout_ms)

Wait for the next depth camera frame.

Args:
    timeout_ms (int): Timeout in milliseconds
    
Returns:
    bool: True if frame is available, False if timeout

**peek_depth_camera_frame**(self, frame_type, timestamp_ns, allow_nearest_frame)

Get the latest depth camera frame from the device.

Args:
    frame_type (int): Type of depth frame 
        - DEPTHCAM_FRAME_TYPE_DEPTH_MAP (0): depth map
        - DEPTHCAM_FRAME_TYPE_POINT3D (1): point3d
    timestamp_ns (int): Specific timestamp to retrieve (0 for latest)
    allow_nearest_frame (bool): Allow nearest frame if exact timestamp not available
    
Returns:
    ImageFrame: Image frame with depth data (depth map or point3d)
    None: If no frame is available
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve depth frame

**peek_depth_camera_related_rectified_image**(self, timestamp_ns)

Get the related rectified camera image for a depth frame.

Args:
    timestamp_ns (int): Timestamp of the depth frame to get related image for
    
Returns:
    ImageFrame: Camera image frame data with rectified image
    None: If no frame is available
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve image

**is_semantic_segmentation_ready**(self)

Check if semantic segmentation is ready for frame capture.

Returns:
    bool: True if semantic segmentation is ready, False otherwise

**wait_semantic_segmentation_next_frame**(self, timeout_ms)

Wait for the next semantic segmentation frame.

Args:
    timeout_ms (int): Timeout in milliseconds
    
Returns:
    bool: True if frame is available, False if timeout

**get_semantic_segmentation_config**(self)

Get semantic segmentation configuration information.

Returns:
    SemanticSegmentationConfig: Configuration including model type, class count, etc.
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve configuration

**get_semantic_segmentation_labels**(self)

Get semantic segmentation label information.

Returns:
    SemanticSegmentationLabelInfo: Label set name and label names
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve label information

**get_semantic_segmentation_label_set_name**(self)

Get the current semantic segmentation label set name.

Returns:
    str: Label set name (e.g., "indoor_80_classes", "outdoor_18_classes")

**peek_semantic_segmentation_frame**(self, timestamp_ns, allow_nearest_frame)

Get the latest semantic segmentation frame from the device.

Args:
    timestamp_ns (int): Specific timestamp to retrieve (0 for latest)
    allow_nearest_frame (bool): Allow nearest frame if exact timestamp not available
    
Returns:
    ImageFrame: Semantic segmentation frame as unified ImageFrame with class IDs and metadata
    None: If no frame is available
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve segmentation frame

**calc_depth_camera_aligned_segmentation_map**(self, segmentation_frame)

Calculate depth camera aligned segmentation map.

This function maps the segmentation map to the same coordinate system as the depth map,
allowing for proper overlay and analysis.

Args:
    segmentation_frame (ImageFrame): Segmentation frame to align (unified ImageFrame format)
    
Returns:
    tuple: (aligned_data, aligned_width, aligned_height)
        - aligned_data (bytes): Aligned segmentation data
        - aligned_width (int): Width of aligned map
        - aligned_height (int): Height of aligned map
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to calculate aligned map

**is_depth_camera_supported**(self)

Check if depth camera is supported by the current device.

This is a convenience method that delegates to DeviceBasicInfo.isSupportDepthCamera().

Returns:
    bool: True if depth camera is supported, False otherwise

**is_semantic_segmentation_supported**(self)

Check if semantic segmentation is supported by the current device.

This is a convenience method that delegates to DeviceBasicInfo.isSupportSemanticSegmentation().

Returns:
    bool: True if semantic segmentation is supported, False otherwise

**is_semantic_segmentation_alternative_model**(self)

Check if semantic segmentation is currently using the alternative model.

Returns:
    bool: True if using alternative model, False if using default model
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to check model status

**get_depth_camera_config**(self)

Get depth camera configuration information.

Returns:
    DepthcamConfigInfo: Configuration information
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to retrieve configuration

**set_depth_camera_postfiltering**(self, enable, flags)

Enable or disable depth camera post-filtering to refine depth estimation.

Post-filtering is enabled by default and helps improve depth map quality
by applying refinement algorithms to the raw depth data.

Args:
    enable (bool): True to enable post-filtering, False to disable
    flags (int): Reserved for future use, should be 0
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to set post-filtering

#### Special Methods

**__init__**(self, controller, c_bindings)

Initialize Enhanced Imaging component.

Args:
    controller: Controller component instance
    c_bindings: Optional C bindings instance
