# lidar_2d_map_builder

Aurora SDK LIDAR2DMapBuilder component.

Handles CoMap (2D LIDAR-based mapping) operations.

## Import

```python
from slamtec_aurora_sdk import lidar_2d_map_builder
```

## Classes

### LIDAR2DMapBuilder

LIDAR2DMapBuilder component for Aurora SDK.

Responsible for CoMap (2D LIDAR-based mapping) operations:
- 2D LIDAR map preview generation and rendering
- 2D occupancy grid map management
- Real-time 2D map building from LIDAR data
- Map preview image retrieval
- 2D map configuration and parameters

Note: This handles the 2D LIDAR-based mapping system (CoMap). 
For the main 3D VSLAM mapping, see the MapManager component.

#### Methods

**start_lidar_2d_map_preview**(self, resolution)

Start LIDAR 2D map preview generation.

This starts the real-time generation of a 2D occupancy grid map
from LIDAR scan data, which can be retrieved as preview images.

Args:
    resolution: Map resolution in meters per pixel (default: 0.05m = 5cm)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to start 2D map preview

**stop_lidar_2d_map_preview**(self)

Stop LIDAR 2D map preview generation.

Stops the real-time 2D map generation process.

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to stop 2D map preview

**get_preview_map_generation_options**(self)

Get the current generation options of the LIDAR 2D preview map.

This returns the actual options being used for map generation,
which may differ from the requested options (e.g., when auto
floor detection is enabled and adjusts height ranges).

Returns:
    dict: Current map generation options containing:
        - resolution (float): Map resolution in meters per pixel
        - map_canvas_width (float): Canvas width in meters
        - map_canvas_height (float): Canvas height in meters
        - active_map_only (bool): Whether generating only active map
        - height_range_specified (bool): Whether height range is specified
        - min_height (float): Minimum height to include (if specified)
        - max_height (float): Maximum height to include (if specified)

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get generation options

Example:
    options = sdk.lidar_2d_map_builder.get_preview_map_generation_options()
    print(f"Current resolution: {options['resolution']}m")
    print(f"Height range: {options['min_height']} - {options['max_height']}m")

**get_lidar_2d_map_preview**(self)

Get current LIDAR 2D map preview image.

Retrieves the current state of the 2D occupancy grid map as an image.
The map shows obstacles (occupied cells), free space, and unknown areas.

Returns:
    Tuple of (map_image_data, map_info) or None if not available
    - map_image_data: Raw image data of the 2D map
    - map_info: Dictionary with map metadata (resolution, origin, etc.)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get 2D map preview

**save_lidar_2d_map**(self, file_path, format)

Save current 2D LIDAR map to file.

Args:
    file_path: Path where to save the 2D map
    format: Map file format ("pgm", "png", "yaml", etc.)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to save 2D map or not implemented

**load_lidar_2d_map**(self, file_path)

Load 2D LIDAR map from file.

Args:
    file_path: Path to the 2D map file
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to load 2D map or not implemented

**clear_lidar_2d_map**(self)

Clear the current 2D LIDAR map and restart building.

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to clear 2D map or not implemented

**set_lidar_2d_map_parameters**(self, resolution, map_size, origin)

Set parameters for 2D LIDAR map building.

Args:
    resolution: Map resolution in meters per pixel
    map_size: Map size as (width, height) in pixels
    origin: Map origin as (x, y) in world coordinates
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to set parameters or not implemented

**get_lidar_2d_map_info**(self)

Get information about the current 2D LIDAR map.

Returns:
    Dict containing 2D map information (resolution, size, coverage, etc.)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get 2D map info or not implemented

**start_preview_map_background_update**(self, options)

Start LIDAR 2D preview map background update.

Args:
    options: GridMapGenerationOptions instance with map generation parameters
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to start background update

**stop_preview_map_background_update**(self)

Stop LIDAR 2D preview map background update.

Raises:
    ConnectionError: If not connected to a device

**is_preview_map_background_updating**(self)

Check if preview map background update is running.

Returns:
    bool: True if background update is running
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to check status

**require_preview_map_redraw**(self)

Require a redraw of the preview map.

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to require redraw

**get_and_reset_preview_map_dirty_rect**(self)

Get and reset the dirty rectangle of the preview map.

Returns:
    Tuple of (dirty_rect, map_changed) where:
    - dirty_rect: Rect instance with dirty area
    - map_changed: bool indicating if map has changed
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get dirty rect

**set_preview_map_auto_floor_detection**(self, enable)

Enable/disable auto floor detection for preview map.

Args:
    enable: bool, True to enable auto floor detection
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to set auto floor detection

**is_preview_map_auto_floor_detection**(self)

Check if auto floor detection is enabled.

Returns:
    bool: True if auto floor detection is enabled
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to check status

**get_preview_map**(self)

Get the preview map handle and data.

Returns:
    OccupancyGridMap2DRef-like object for accessing map data
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get preview map

**generate_fullmap_ondemand**(self, options, wait_for_data_sync, timeout_ms)

Generate a full 2D LiDAR map on-demand using slamtec_aurora_sdk_lidar2dmap_generate_fullmap.

This is the proper interface for on-demand map building, different from preview map
background update which is meant for real-time visualization.

Args:
    options: GridMapGenerationOptions for the map generation
    wait_for_data_sync: Whether to wait for map data sync (default: True)
    timeout_ms: Timeout in milliseconds (default: 60000)
    
Returns:
    GridMapRef: Reference to the generated map handle

#### Special Methods

**__init__**(self, controller, c_bindings)

Initialize LIDAR2DMapBuilder component.

Args:
    controller: Controller component instance
    c_bindings: Optional C bindings instance

### GridMapRef

Reference to a 2D grid map for accessing map data with automatic cleanup.

This class handles both owned gridmaps (that need to be released) and
non-owned gridmaps (like preview map that should not be released).

#### Properties

**owns_handle**

Check if this object owns the gridmap handle.

**is_valid**

Check if the gridmap is still valid.

#### Methods

**release**(self)

Release the grid map resources if owned.

This method is safe to call multiple times. It only releases
the gridmap if this object owns it (e.g., generated maps).
Built-in gridmaps like preview map are not released.

**get_map_dimension**(self)

Get map dimension.

**read_cell_data**(self, fetch_rect, resolution, l2p_mapping)

Read cell data from the map.

Args:
    fetch_rect: Rectangle area to fetch (in meters)
    resolution: Map resolution in meters per cell (default: 0.05m = 5cm)
    l2p_mapping: If True, perform log-odd to linear (0-255) mapping for visualization.
                If False, return raw data for navigation (default: True)

Returns:
    tuple: (cell_data_list, fetch_info)

#### Special Methods

**__init__**(self, c_bindings, gridmap_handle, owns_handle)

Initialize GridMapRef.

Args:
    c_bindings: C bindings instance
    gridmap_handle: Handle to the grid map
    owns_handle: If True, this object owns the handle and will release it.
                If False (e.g., for preview map), the handle won't be released.

**__del__**(self)

Destructor to ensure cleanup.

**__enter__**(self)

Context manager entry.

**__exit__**(self, exc_type, exc_val, exc_tb)

Context manager exit with cleanup.
