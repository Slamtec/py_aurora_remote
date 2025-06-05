# utils

Aurora SDK Utility Functions

This module contains helper functions and utilities for common operations
with the Aurora SDK, such as map synchronization checking, data processing,
status monitoring, and semantic segmentation utilities.

## Import

```python
from slamtec_aurora_sdk import utils
```

## Functions

**get_map_sync_status**(global_mapping_info)

Calculate map data synchronization status from global mapping info.

Args:
    global_mapping_info: Dictionary returned from DataProvider.get_global_mapping_info()
    
Returns:
    dict: Map sync status with sync ratio and derived information
        - sync_ratio: float (0.0 to 1.0) - ratio of fetched/total keyframes  
        - total_kf_count: int - total keyframes in the map
        - total_kf_count_fetched: int - keyframes successfully fetched
        - is_synced: bool - True if sync ratio >= 95%
        - is_sufficient: bool - True if has enough data for map generation
        - raw_info: dict - original global mapping info

**wait_for_map_data**(data_provider, min_keyframes, min_sync_ratio, max_wait_time, progress_callback)

Wait for sufficient map data to be available for processing.

Args:
    data_provider: DataProvider instance
    min_keyframes: Minimum number of keyframes required (default: 10)
    min_sync_ratio: Minimum sync ratio required (default: 0.8 = 80%)
    max_wait_time: Maximum time to wait in seconds (default: 30.0)
    progress_callback: Optional callback function(elapsed_time, sync_status)
    
Returns:
    dict: Final sync status when sufficient data is available or timeout reached
    
Raises:
    AuroraSDKError: If no map data is available after timeout

**format_map_sync_status**(sync_status, verbose)

Format map synchronization status for display.

Args:
    sync_status: Dictionary from get_map_sync_status()
    verbose: If True, include detailed information
    
Returns:
    str: Formatted status string

**validate_map_generation_options**(options)

Validate map generation options for common issues.

Args:
    options: GridMapGenerationOptions instance
    
Returns:
    list: List of validation warnings/errors (empty if all good)

**to_numpy_segmentation_map**(image_frame)

Convert ImageFrame containing segmentation data to numpy array.

Args:
    image_frame (ImageFrame): ImageFrame containing segmentation data
    
Returns:
    numpy.ndarray: 2D array of class IDs, or None if conversion fails
    
Raises:
    ImportError: If NumPy is not available
    ValueError: If image_frame is invalid

**to_colorized_segmentation_map**(image_frame, colors, max_classes)

Convert ImageFrame containing segmentation data to colorized visualization.

Args:
    image_frame (ImageFrame): ImageFrame containing segmentation data  
    colors: List of (B, G, R) color tuples for each class. If None, random colors are generated.
    max_classes: Maximum number of classes to generate colors for (default: 256)
    
Returns:
    numpy.ndarray: Colorized segmentation map as BGR image, or None if conversion fails
    
Raises:
    ImportError: If OpenCV and NumPy are not available

**generate_class_colors**(class_count)

Generate colors exactly like C++ generateClassColors function.

Args:
    class_count (int): Number of classes to generate colors for
    
Returns:
    list: List of (B, G, R) color tuples

**manual_colorize_segmentation**(seg_map, colors)

Manual colorization (matching C++ colorizeSegmentationMap exactly).

Args:
    seg_map (numpy.ndarray): 2D segmentation map with class IDs
    colors: List of (B, G, R) color tuples
    
Returns:
    numpy.ndarray: Colorized segmentation map as BGR image, or None if failed

**get_colorized_segmentation**(image_frame, colors)

Get colorized segmentation with C API fallback.

Args:
    image_frame (ImageFrame): ImageFrame containing segmentation data
    colors: List of (B, G, R) color tuples
    
Returns:
    numpy.ndarray: Colorized segmentation map, or None if failed

**get_class_at_position**(image_frame, x, y)

Get class ID at given pixel position in segmentation frame.

Args:
    image_frame (ImageFrame): ImageFrame containing segmentation data
    x (int): X coordinate
    y (int): Y coordinate
    
Returns:
    int: Class ID at position, or None if invalid position or no data

## Constants

- **NUMPY_AVAILABLE** = `True`
- **NUMPY_AVAILABLE** = `False`
