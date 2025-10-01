# c_bindings

Low-level C bindings for Aurora SDK using ctypes.

## Import

```python
from slamtec_aurora_sdk import c_bindings
```

## Classes

### CBindings

Low-level C bindings for Aurora SDK.

#### Methods

**get_version_info**(self)

Get SDK version information.

**create_session**(self)

Create a new SDK session.

**release_session**(self, handle)

Release SDK session.

**get_discovered_servers**(self, handle, max_count)

Get list of discovered Aurora servers.

**discover_devices**(self, handle, timeout)

Discover Aurora devices on the network.

**connect_device**(self, handle, device_info)

Connect to Aurora device using device info dictionary from discovery.

**connect_string**(self, handle, connection_string)

Connect to Aurora device using connection string.

**connect**(self, handle, server_info)

Connect to Aurora server (legacy method).

**disconnect**(self, handle)

Disconnect from Aurora server.

**is_connected**(self, handle)

Check if connected to Aurora server.

**set_map_data_syncing**(self, handle, enable)

Enable/disable map data syncing.

**set_raw_data_subscription**(self, handle, enable)

Enable/disable raw data subscription.

**get_current_pose_se3**(self, handle)

Get current pose in SE3 format with timestamp.

**get_current_pose**(self, handle)

Get current pose in Euler angle format with timestamp.

**get_device_basic_info**(self, handle)

Get device basic information.

**peek_camera_preview_image**(self, handle, timestamp_ns, allow_nearest_frame)

Get camera preview image with actual pixel data.

**peek_tracking_data**(self, handle)

Get tracking frame data with keypoints.

**require_mapping_mode**(self, handle, timeout_ms)

Require the device to enter mapping mode.

**resync_map_data**(self, handle, invalidate_cache)

Force resync of map data.

**get_global_mapping_info_legacy**(self, handle)

Get global mapping information (legacy).

**start_lidar2d_preview_map**(self, handle, resolution)

Start LIDAR 2D map preview generation.

**stop_lidar2d_preview_map**(self, handle)

Stop LIDAR 2D map preview generation.

**get_lidar2d_preview_map**(self, handle)

Get current LIDAR 2D map preview.

**get_global_mapping_info**(self, handle)

Get global mapping information.

**access_map_data**(self, handle, map_ids, fetch_kf, fetch_mp, fetch_mapinfo, kf_fetch_flags, mp_fetch_flags)

Access visual map data (map points and keyframes).

Args:
    handle: Session handle
    map_ids: Optional list/tuple of map IDs to fetch. If None, fetches only the active map.
            If empty list, fetches all maps.
    fetch_kf: Whether to fetch keyframes (default: True)
    fetch_mp: Whether to fetch map points (default: True)
    fetch_mapinfo: Whether to fetch map info (default: False)
    kf_fetch_flags: Keyframe fetch flags (default: None, uses FETCH_ALL)
    mp_fetch_flags: Map point fetch flags (default: None, uses FETCH_ALL)

Returns:
    Dict containing 'map_points', 'keyframes', and 'loop_closures' lists with full metadata

**peek_recent_lidar_scan**(self, handle, max_points, force_latest)

Get the most recent LiDAR scan data.

**start_lidar2dmap_preview**(self, handle, options)

Start LIDAR 2D grid map preview generation.

**stop_lidar2dmap_preview**(self, handle)

Stop LIDAR 2D grid map preview generation.

**get_lidar2dmap_preview_handle**(self, handle)

Get the handle of the preview 2D grid map.

**is_lidar2dmap_preview_updating**(self, handle)

Check if LIDAR 2D grid map preview is updating.

**require_lidar2dmap_redraw**(self, handle)

Require redraw of the 2D map preview.

**get_lidar2dmap_dirty_rect**(self, handle)

Get and reset the dirty rectangle of the 2D map preview.

**set_lidar2dmap_auto_floor_detection**(self, handle, enable)

Enable/disable auto floor detection for 2D map.

**is_lidar2dmap_auto_floor_detection**(self, handle)

Check if auto floor detection is enabled.

**get_gridmap_dimension**(self, gridmap_handle, get_max_capacity)

Get the dimension of a 2D grid map.

**read_gridmap_cell_data**(self, gridmap_handle, fetch_rect, resolution, l2p_mapping)

Read cell data from a 2D grid map.

Args:
    gridmap_handle: Handle to the grid map
    fetch_rect: Rectangle area to fetch (in meters)
    resolution: Map resolution in meters per cell (default: 0.05m = 5cm)
    l2p_mapping: If True, perform log-odd to linear (0-255) mapping for visualization.
                If False, return raw data for navigation (default: True)

Returns:
    tuple: (cell_data_list, fetch_info)

**get_floor_detection_histogram**(self, handle)

Get floor detection histogram data.

**get_all_floor_detection_info**(self, handle)

Get all floor detection descriptions and current floor ID.

**get_current_floor_detection_desc**(self, handle)

Get current floor detection description.

**generate_lidar_2d_fullmap**(self, handle, build_options, wait_for_data_sync, timeout_ms)

Generate full 2D LiDAR map on-demand.

Args:
    handle: Session handle
    build_options: GridMapGenerationOptions for the map generation
    wait_for_data_sync: Whether to wait for map data sync (default: True)
    timeout_ms: Timeout in milliseconds (default: 60000)
    
Returns:
    Handle to the generated 2D grid map

**set_enhanced_imaging_subscription**(self, handle, enhanced_image_type, enable)

Set enhanced imaging subscription for specific image type.

**is_enhanced_imaging_subscribed**(self, handle, enhanced_image_type)

Check if enhanced imaging is subscribed for specific image type.

**require_semantic_segmentation_alternative_model**(self, handle, use_alternative_model, timeout_ms)

Require semantic segmentation to use alternative model.

**get_camera_calibration**(self, handle)

Get camera calibration parameters.

**get_transform_calibration**(self, handle)

Get transform calibration parameters.

**peek_depth_camera_frame**(self, handle, frame_type)

Get depth camera frame data using correct C API (two-step process like C++).

**peek_depth_camera_related_rectified_image**(self, handle, timestamp)

Get depth camera related rectified image using correct C API.

**get_semantic_segmentation_config**(self, handle)

Get semantic segmentation configuration.

**get_semantic_segmentation_labels**(self, handle)

Get semantic segmentation label information.

**get_semantic_segmentation_label_set_name**(self, handle)

Get semantic segmentation label set name.

**peek_semantic_segmentation_frame**(self, handle, timestamp_ns, allow_nearest)

Get semantic segmentation frame data using two-step buffer allocation.

**wait_semantic_segmentation_next_frame**(self, handle, timeout_ms)

Wait for the next semantic segmentation frame to be available.

**is_semantic_segmentation_using_alternative_model**(self, handle)

Check if semantic segmentation is using alternative model.

**set_semantic_segmentation_model**(self, handle, model_type)

Set semantic segmentation model type.

**calc_depth_aligned_segmentation_map**(self, handle, segmentation_data, seg_width, seg_height)

Calculate depth camera aligned segmentation map (matching C++ implementation).

**require_map_reset**(self, handle, timeout_ms)

Require the device to reset its map.

**require_pure_localization_mode**(self, handle, timeout_ms)

Require the device to enter pure localization mode (no mapping).

**is_device_connection_alive**(self, handle)

Check if the device connection is alive and healthy.

**is_raw_data_subscribed**(self, handle)

Check if raw data subscription is active.

**get_last_device_status**(self, handle)

Get the last device status information.

**get_relocalization_status**(self, handle)

Get relocalization status information.

**get_mapping_flags**(self, handle)

Get current mapping flags.

**convert_quaternion_to_euler**(self, qx, qy, qz, qw)

Convert quaternion to Euler angles.

**depthcam_is_ready**(self, handle)

Check if depth camera is ready.

**depthcam_get_config_info**(self, handle)

Get depth camera configuration.

**depthcam_wait_next_frame**(self, handle, timeout_ms)

Wait for next depth camera frame.

**semantic_segmentation_is_ready**(self, handle)

Check if semantic segmentation is ready.

**gridmap_release**(self, gridmap_handle)

Release gridmap handle to prevent memory leaks.

**gridmap_get_resolution**(self, gridmap_handle)

Get gridmap resolution.

**get_supported_grid_resolution_range**(self, handle)

Get supported grid resolution range.

**get_supported_max_grid_cell_count**(self, handle)

Get maximum supported grid cell count.

**get_imu_info**(self, handle)

Get IMU information.

**get_all_map_info**(self, handle, max_count)

Get information about all maps.

**peek_history_pose**(self, handle, timestamp_ns, allow_interpolation, max_time_diff_ns)

Peek historical pose at specific timestamp.

**peek_imu_data**(self, handle, max_count)

Peek recent IMU data.

**set_low_rate_mode**(self, handle, enable)

Enable/disable low rate mode - CORRECTED: no return value.

**set_loop_closure**(self, handle, enable, timeout_ms)

Enable/disable loop closure - CORRECTED: added missing timeout_ms parameter.

**force_map_global_optimization**(self, handle, timeout_ms)

Force global map optimization.

**send_custom_command**(self, handle, command_id, data, timeout_ms)

Send custom command - CORRECTED: proper parameter order and types.

**set_keyframe_fetch_flags**(self, handle, flags)

Set keyframe fetch flags.

**get_keyframe_fetch_flags**(self, handle)

Get current keyframe fetch flags.

**set_map_point_fetch_flags**(self, handle, flags)

Set map point fetch flags.

**get_map_point_fetch_flags**(self, handle)

Get current map point fetch flags.

**depthcam_set_postfiltering**(self, handle, enable, flags)

Enable/disable depth camera post-filtering.

#### Special Methods

**__init__**(self)

## Functions

**load_aurora_sdk_library**()

Load the Aurora SDK dynamic library based on platform.

**get_c_bindings**()

Get global C bindings instance.

**map_point_callback**(user_data, map_point_ptr)

**keyframe_callback**(user_data, keyframe_ptr, looped_ids, connected_ids, related_mp_ids)

**map_desc_callback**(user_data, map_desc_ptr)
