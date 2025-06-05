"""
Aurora SDK LIDAR2DMapBuilder component.

Handles CoMap (2D LIDAR-based mapping) operations.
"""

from .c_bindings import get_c_bindings
from .exceptions import AuroraSDKError, ConnectionError


class LIDAR2DMapBuilder:
    """
    LIDAR2DMapBuilder component for Aurora SDK.
    
    Responsible for CoMap (2D LIDAR-based mapping) operations:
    - 2D LIDAR map preview generation and rendering
    - 2D occupancy grid map management
    - Real-time 2D map building from LIDAR data
    - Map preview image retrieval
    - 2D map configuration and parameters
    
    Note: This handles the 2D LIDAR-based mapping system (CoMap). 
    For the main 3D VSLAM mapping, see the MapManager component.
    """
    
    def __init__(self, controller, c_bindings=None):
        """
        Initialize LIDAR2DMapBuilder component.
        
        Args:
            controller: Controller component instance
            c_bindings: Optional C bindings instance
        """
        self._controller = controller
        try:
            self._c_bindings = c_bindings or get_c_bindings()
        except Exception as e:
            # Store the error for later when methods are actually called
            self._c_bindings = None
            self._c_bindings_error = str(e)
    
    def _ensure_c_bindings(self):
        """Ensure C bindings are available or raise appropriate error."""
        if self._c_bindings is None:
            raise AuroraSDKError(f"Aurora SDK not available: {getattr(self, '_c_bindings_error', 'Unknown error')}")
    
    def _ensure_connected(self):
        """Ensure we're connected to a device."""
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")
    
    def start_lidar_2d_map_preview(self, resolution=0.05):
        """
        Start LIDAR 2D map preview generation.
        
        This starts the real-time generation of a 2D occupancy grid map
        from LIDAR scan data, which can be retrieved as preview images.
        
        Args:
            resolution: Map resolution in meters per pixel (default: 0.05m = 5cm)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to start 2D map preview
        """
        self._ensure_connected()
        
        try:
            self._c_bindings.start_lidar2d_preview_map(self._controller.session_handle, resolution)
        except Exception as e:
            raise AuroraSDKError(f"Failed to start LIDAR 2D map preview: {e}")
    
    def stop_lidar_2d_map_preview(self):
        """
        Stop LIDAR 2D map preview generation.
        
        Stops the real-time 2D map generation process.
        
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to stop 2D map preview
        """
        self._ensure_connected()
        
        try:
            self._c_bindings.stop_lidar2d_preview_map(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to stop LIDAR 2D map preview: {e}")
    
    def get_lidar_2d_map_preview(self):
        """
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
        """
        self._ensure_connected()
        
        try:
            return self._c_bindings.get_lidar2d_preview_map(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get LIDAR 2D map preview: {e}")
    
    def save_lidar_2d_map(self, file_path, format="pgm"):
        """
        Save current 2D LIDAR map to file.
        
        Args:
            file_path: Path where to save the 2D map
            format: Map file format ("pgm", "png", "yaml", etc.)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to save 2D map or not implemented
        """
        self._ensure_connected()
        
        # Note: 2D map saving would need to be implemented in C bindings
        raise AuroraSDKError("LIDAR 2D map saving not yet implemented")
    
    def load_lidar_2d_map(self, file_path):
        """
        Load 2D LIDAR map from file.
        
        Args:
            file_path: Path to the 2D map file
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to load 2D map or not implemented
        """
        self._ensure_connected()
        
        # Note: 2D map loading would need to be implemented in C bindings
        raise AuroraSDKError("LIDAR 2D map loading not yet implemented")
    
    def clear_lidar_2d_map(self):
        """
        Clear the current 2D LIDAR map and restart building.
        
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to clear 2D map or not implemented
        """
        self._ensure_connected()
        
        # Note: 2D map clearing would need to be implemented in C bindings
        raise AuroraSDKError("LIDAR 2D map clearing not yet implemented")
    
    def set_lidar_2d_map_parameters(self, resolution=None, map_size=None, origin=None):
        """
        Set parameters for 2D LIDAR map building.
        
        Args:
            resolution: Map resolution in meters per pixel
            map_size: Map size as (width, height) in pixels
            origin: Map origin as (x, y) in world coordinates
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to set parameters or not implemented
        """
        self._ensure_connected()
        
        # Note: Parameter setting would need to be implemented in C bindings
        raise AuroraSDKError("LIDAR 2D map parameter setting not yet implemented")
    
    def get_lidar_2d_map_info(self):
        """
        Get information about the current 2D LIDAR map.
        
        Returns:
            Dict containing 2D map information (resolution, size, coverage, etc.)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to get 2D map info or not implemented
        """
        self._ensure_connected()
        
        # Note: 2D map info would need to be implemented in C bindings
        raise AuroraSDKError("LIDAR 2D map info retrieval not yet implemented")
    
    # New 2D Grid Map Preview API
    def start_preview_map_background_update(self, options):
        """
        Start LIDAR 2D preview map background update.
        
        Args:
            options: GridMapGenerationOptions instance with map generation parameters
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to start background update
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            self._c_bindings.start_lidar2dmap_preview(self._controller.session_handle, options)
        except Exception as e:
            raise AuroraSDKError(f"Failed to start preview map background update: {e}")
    
    def stop_preview_map_background_update(self):
        """
        Stop LIDAR 2D preview map background update.
        
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            self._c_bindings.stop_lidar2dmap_preview(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to stop preview map background update: {e}")
    
    def is_preview_map_background_updating(self):
        """
        Check if preview map background update is running.
        
        Returns:
            bool: True if background update is running
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to check status
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.is_lidar2dmap_preview_updating(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to check preview map status: {e}")
    
    def require_preview_map_redraw(self):
        """
        Require a redraw of the preview map.
        
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to require redraw
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            self._c_bindings.require_lidar2dmap_redraw(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to require preview map redraw: {e}")
    
    def get_and_reset_preview_map_dirty_rect(self):
        """
        Get and reset the dirty rectangle of the preview map.
        
        Returns:
            Tuple of (dirty_rect, map_changed) where:
            - dirty_rect: Rect instance with dirty area
            - map_changed: bool indicating if map has changed
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to get dirty rect
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            result = self._c_bindings.get_lidar2dmap_dirty_rect(self._controller.session_handle)
            return result
        except Exception as e:
            raise AuroraSDKError(f"Failed to get preview map dirty rect: {e}")
    
    def set_preview_map_auto_floor_detection(self, enable):
        """
        Enable/disable auto floor detection for preview map.
        
        Args:
            enable: bool, True to enable auto floor detection
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to set auto floor detection
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            self._c_bindings.set_lidar2dmap_auto_floor_detection(self._controller.session_handle, enable)
        except Exception as e:
            raise AuroraSDKError(f"Failed to set auto floor detection: {e}")
    
    def is_preview_map_auto_floor_detection(self):
        """
        Check if auto floor detection is enabled.
        
        Returns:
            bool: True if auto floor detection is enabled
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to check status
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.is_lidar2dmap_auto_floor_detection(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to check auto floor detection status: {e}")
    
    def get_preview_map(self):
        """
        Get the preview map handle and data.
        
        Returns:
            OccupancyGridMap2DRef-like object for accessing map data
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to get preview map
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            gridmap_handle = self._c_bindings.get_lidar2dmap_preview_handle(self._controller.session_handle)
            if not gridmap_handle:
                return None
            # Preview map is NOT owned - should not be released
            return GridMapRef(self._c_bindings, gridmap_handle, owns_handle=False)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get preview map: {e}")
    
    def generate_fullmap_ondemand(self, options, wait_for_data_sync=True, timeout_ms=60000):
        """
        Generate a full 2D LiDAR map on-demand using slamtec_aurora_sdk_lidar2dmap_generate_fullmap.
        
        This is the proper interface for on-demand map building, different from preview map
        background update which is meant for real-time visualization.
        
        Args:
            options: GridMapGenerationOptions for the map generation
            wait_for_data_sync: Whether to wait for map data sync (default: True)
            timeout_ms: Timeout in milliseconds (default: 60000)
            
        Returns:
            GridMapRef: Reference to the generated map handle
        """
        self._ensure_c_bindings()
        self._ensure_connected()
        
        # Generate the full map
        generated_handle = self._c_bindings.generate_lidar_2d_fullmap(
            self._controller.session_handle,
            options,
            wait_for_data_sync,
            timeout_ms
        )
        
        # Generated map IS owned - should be released when done
        return GridMapRef(self._c_bindings, generated_handle, owns_handle=True)


class GridMapRef:
    """Reference to a 2D grid map for accessing map data with automatic cleanup.
    
    This class handles both owned gridmaps (that need to be released) and
    non-owned gridmaps (like preview map that should not be released).
    """
    
    def __init__(self, c_bindings, gridmap_handle, owns_handle=True):
        """
        Initialize GridMapRef.
        
        Args:
            c_bindings: C bindings instance
            gridmap_handle: Handle to the grid map
            owns_handle: If True, this object owns the handle and will release it.
                        If False (e.g., for preview map), the handle won't be released.
        """
        self._c_bindings = c_bindings
        self._gridmap_handle = gridmap_handle
        self._owns_handle = owns_handle
        self._released = False
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.release()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.release()
    
    def release(self):
        """
        Release the grid map resources if owned.
        
        This method is safe to call multiple times. It only releases
        the gridmap if this object owns it (e.g., generated maps).
        Built-in gridmaps like preview map are not released.
        """
        if not self._released and self._gridmap_handle and self._owns_handle:
            try:
                self._c_bindings.gridmap_release(self._gridmap_handle)
            except:
                pass  # Ignore errors during cleanup
            finally:
                self._released = True
                self._gridmap_handle = None
        elif not self._released:
            # Mark as released even if we don't own it
            self._released = True
    
    @property
    def owns_handle(self):
        """Check if this object owns the gridmap handle."""
        return self._owns_handle
    
    @property
    def is_valid(self):
        """Check if the gridmap is still valid."""
        return not self._released and self._gridmap_handle is not None
    
    def get_map_dimension(self):
        """Get map dimension."""
        if self._released:
            raise AuroraSDKError("GridMap has been released")
        return self._c_bindings.get_gridmap_dimension(self._gridmap_handle)
    
    def read_cell_data(self, fetch_rect, resolution=0.05, l2p_mapping=True):
        """
        Read cell data from the map.
        
        Args:
            fetch_rect: Rectangle area to fetch (in meters)
            resolution: Map resolution in meters per cell (default: 0.05m = 5cm)
            l2p_mapping: If True, perform log-odd to linear (0-255) mapping for visualization.
                        If False, return raw data for navigation (default: True)
        
        Returns:
            tuple: (cell_data_list, fetch_info)
        """
        if self._released:
            raise AuroraSDKError("GridMap has been released")
        return self._c_bindings.read_gridmap_cell_data(self._gridmap_handle, fetch_rect, resolution, l2p_mapping)