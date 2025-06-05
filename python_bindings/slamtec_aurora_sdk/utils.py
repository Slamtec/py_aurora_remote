"""
Aurora SDK Utility Functions

This module contains helper functions and utilities for common operations
with the Aurora SDK, such as map synchronization checking, data processing,
status monitoring, and semantic segmentation utilities.
"""

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


def get_map_sync_status(global_mapping_info):
    """
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
    """
    total_kf_count = global_mapping_info.get('total_kf_count', 0)
    total_kf_count_fetched = global_mapping_info.get('total_kf_count_fetched', 0)
    
    # Calculate sync ratio (0.0 to 1.0)
    if total_kf_count > 0:
        sync_ratio = total_kf_count_fetched / total_kf_count
    else:
        sync_ratio = 0.0
    
    # Determine sync status
    is_synced = sync_ratio >= 0.95  # Consider synced if >= 95%
    is_sufficient = total_kf_count >= 10 and sync_ratio >= 0.8  # Sufficient for map generation
    
    return {
        'sync_ratio': sync_ratio,
        'total_kf_count': total_kf_count,
        'total_kf_count_fetched': total_kf_count_fetched,
        'is_synced': is_synced,
        'is_sufficient': is_sufficient,
        'raw_info': global_mapping_info
    }


def wait_for_map_data(data_provider, min_keyframes=10, min_sync_ratio=0.8, 
                     max_wait_time=30.0, progress_callback=None):
    """
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
    """
    import time
    from .exceptions import AuroraSDKError
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        # Get current mapping info and sync status
        global_info = data_provider.get_global_mapping_info()
        sync_status = get_map_sync_status(global_info)
        
        # Call progress callback if provided
        if progress_callback:
            progress_callback(elapsed, sync_status)
        
        # Check if we have sufficient data
        if (sync_status['total_kf_count'] >= min_keyframes and 
            sync_status['sync_ratio'] >= min_sync_ratio):
            return sync_status
        
        # Check timeout
        if elapsed >= max_wait_time:
            if sync_status['total_kf_count'] > 0:
                # Return available data even if not ideal
                return sync_status
            else:
                raise AuroraSDKError(
                    "No map data available after {:.1f}s. "
                    "Device may not be in mapping mode or not moving.".format(elapsed)
                )
        
        time.sleep(0.5)


def format_map_sync_status(sync_status, verbose=False):
    """
    Format map synchronization status for display.
    
    Args:
        sync_status: Dictionary from get_map_sync_status()
        verbose: If True, include detailed information
        
    Returns:
        str: Formatted status string
    """
    ratio_pct = sync_status['sync_ratio'] * 100
    total_kf = sync_status['total_kf_count'] 
    fetched_kf = sync_status['total_kf_count_fetched']
    
    if verbose:
        status = "Map sync: {:.1f}% ({}/{} keyframes)".format(ratio_pct, fetched_kf, total_kf)
        if sync_status['is_synced']:
            status += " ✓ Well synchronized"
        elif sync_status['is_sufficient']:
            status += " ⚠ Sufficient for processing"
        else:
            status += " ⏳ Waiting for more data"
        return status
    else:
        return "{:.1f}% synced ({}/{} KF)".format(ratio_pct, fetched_kf, total_kf)


def validate_map_generation_options(options):
    """
    Validate map generation options for common issues.
    
    Args:
        options: GridMapGenerationOptions instance
        
    Returns:
        list: List of validation warnings/errors (empty if all good)
    """
    warnings = []
    
    if hasattr(options, 'resolution'):
        if options.resolution <= 0:
            warnings.append("Resolution must be positive")
        elif options.resolution < 0.01:
            warnings.append("Very high resolution (< 1cm) may cause memory issues")
        elif options.resolution > 0.5:
            warnings.append("Very low resolution (> 50cm) may lose detail")
    
    if hasattr(options, 'map_canvas_width') and hasattr(options, 'map_canvas_height'):
        if options.map_canvas_width <= 0 or options.map_canvas_height <= 0:
            warnings.append("Map dimensions must be positive")
        
        if hasattr(options, 'resolution'):
            total_cells = (options.map_canvas_width / options.resolution) * (options.map_canvas_height / options.resolution)
            if total_cells > 10_000_000:  # 10M cells
                warnings.append("Very large map ({:,.0f} cells) may cause memory issues".format(total_cells))
    
    if hasattr(options, 'height_range_specified') and options.height_range_specified:
        if hasattr(options, 'min_height') and hasattr(options, 'max_height'):
            if options.min_height >= options.max_height:
                warnings.append("min_height must be less than max_height")
    
    return warnings


# Semantic Segmentation Utility Functions
def to_numpy_segmentation_map(image_frame):
    """
    Convert ImageFrame containing segmentation data to numpy array.
    
    Args:
        image_frame (ImageFrame): ImageFrame containing segmentation data
        
    Returns:
        numpy.ndarray: 2D array of class IDs, or None if conversion fails
        
    Raises:
        ImportError: If NumPy is not available
        ValueError: If image_frame is invalid
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for segmentation map conversion")
    
    if not image_frame or not image_frame.data:
        return None
    
    try:
        # Convert bytes to uint8 array
        seg_array = np.frombuffer(image_frame.data, dtype=np.uint8)
        if len(seg_array) >= image_frame.width * image_frame.height:
            return seg_array[:image_frame.width * image_frame.height].reshape((image_frame.height, image_frame.width))
        return None
    except Exception:
        return None


def to_colorized_segmentation_map(image_frame, colors=None, max_classes=256):
    """
    Convert ImageFrame containing segmentation data to colorized visualization.
    
    Args:
        image_frame (ImageFrame): ImageFrame containing segmentation data  
        colors: List of (B, G, R) color tuples for each class. If None, random colors are generated.
        max_classes: Maximum number of classes to generate colors for (default: 256)
        
    Returns:
        numpy.ndarray: Colorized segmentation map as BGR image, or None if conversion fails
        
    Raises:
        ImportError: If OpenCV and NumPy are not available
    """
    try:
        import numpy as np
        import cv2
    except ImportError as e:
        raise ImportError("OpenCV and NumPy are required for segmentation colorization: {}".format(e))
    
    seg_map = to_numpy_segmentation_map(image_frame)
    if seg_map is None:
        return None
    
    # Generate random colors if not provided
    if colors is None:
        colors = generate_class_colors(max_classes)
    
    # Create colorized image
    colorized = np.zeros((image_frame.height, image_frame.width, 3), dtype=np.uint8)
    unique_classes = np.unique(seg_map)
    for class_id in unique_classes:
        if class_id < len(colors):
            mask = seg_map == class_id
            colorized[mask] = colors[class_id]
    
    return colorized


def generate_class_colors(class_count):
    """
    Generate colors exactly like C++ generateClassColors function.
    
    Args:
        class_count (int): Number of classes to generate colors for
        
    Returns:
        list: List of (B, G, R) color tuples
    """
    colors = []
    
    # Set background (index 0) to black for transparency effect (like C++)
    colors.append((0, 0, 0))
    
    # Generate random colors for other classes (like C++)
    if NUMPY_AVAILABLE:
        import numpy as np
        np.random.seed(42)  # For consistent colors
        for i in range(1, max(100, class_count + 20)):
            colors.append((
                int(np.random.randint(50, 256)),  # B
                int(np.random.randint(50, 256)),  # G  
                int(np.random.randint(50, 256))   # R
            ))
    else:
        import random
        random.seed(42)  # For consistent colors
        for i in range(1, max(100, class_count + 20)):
            colors.append((
                random.randint(50, 255),  # B
                random.randint(50, 255),  # G  
                random.randint(50, 255)   # R
            ))
    
    return colors


def manual_colorize_segmentation(seg_map, colors):
    """
    Manual colorization (matching C++ colorizeSegmentationMap exactly).
    
    Args:
        seg_map (numpy.ndarray): 2D segmentation map with class IDs
        colors: List of (B, G, R) color tuples
        
    Returns:
        numpy.ndarray: Colorized segmentation map as BGR image, or None if failed
    """
    if seg_map is None or len(colors) == 0:
        return None
    
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for manual colorization")
    
    import numpy as np
    
    height, width = seg_map.shape
    colorized = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Colorize each pixel exactly like C++ code
    for y in range(height):
        for x in range(width):
            class_id = seg_map[y, x]
            if class_id < len(colors):
                colorized[y, x] = colors[class_id]
            else:
                colorized[y, x] = [128, 128, 128]  # Gray for unknown classes
    
    return colorized


def get_colorized_segmentation(image_frame, colors):
    """
    Get colorized segmentation with C API fallback.
    
    Args:
        image_frame (ImageFrame): ImageFrame containing segmentation data
        colors: List of (B, G, R) color tuples
        
    Returns:
        numpy.ndarray: Colorized segmentation map, or None if failed
    """
    if image_frame is None:
        return None
    
    try:
        # Try using to_colorized_segmentation_map first (unified approach)
        colorized = to_colorized_segmentation_map(image_frame, colors)
        
        # Check if colorization worked
        if colorized is not None:
            if NUMPY_AVAILABLE:
                import numpy as np
                non_black = np.sum(~np.all(colorized == [0, 0, 0], axis=2))
                total = colorized.shape[0] * colorized.shape[1]
                
                # If less than 0.1% non-black pixels, colorization probably failed
                if non_black / total < 0.001:
                    seg_map = to_numpy_segmentation_map(image_frame)
                    if seg_map is not None:
                        return manual_colorize_segmentation(seg_map, colors)
                else:
                    return colorized
            else:
                return colorized
        else:
            # Colorization failed completely
            seg_map = to_numpy_segmentation_map(image_frame)
            if seg_map is not None:
                return manual_colorize_segmentation(seg_map, colors)
    except Exception as e:
        print(f"Colorization error: {e}")
    
    return None


def get_class_at_position(image_frame, x, y):
    """
    Get class ID at given pixel position in segmentation frame.
    
    Args:
        image_frame (ImageFrame): ImageFrame containing segmentation data
        x (int): X coordinate
        y (int): Y coordinate
        
    Returns:
        int: Class ID at position, or None if invalid position or no data
    """
    seg_map = to_numpy_segmentation_map(image_frame)
    if seg_map is None or x < 0 or x >= image_frame.width or y < 0 or y >= image_frame.height:
        return None
    
    class_id = int(seg_map[y, x])
    return class_id