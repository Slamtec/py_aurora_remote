"""
Aurora SDK v2 - Component-based architecture.

This is the new component-based implementation following C++ SDK patterns.
"""

from .controller import Controller
from .data_provider import DataProvider
from .map_manager import MapManager
from .lidar_2d_map_builder import LIDAR2DMapBuilder
from .floor_detector import FloorDetector
from .enhanced_imaging import EnhancedImaging
from .data_recorder import DataRecorder
from .exceptions import AuroraSDKError


class AuroraSDK:
    """
    Aurora SDK main class with component-based architecture.
    
    This class provides access to Aurora device functionality through separate
    components following the C++ SDK design pattern:
    - Controller: Device connection and control
    - DataProvider: Data retrieval (pose, images, sensors)
    - MapManager: VSLAM (3D visual mapping) operations
    - LIDAR2DMapBuilder: CoMap (2D LIDAR mapping) operations
    - EnhancedImaging: Enhanced imaging features (depth camera, semantic segmentation)
    - DataRecorder: Sensor data recording for dataset generation
    
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
    """
    
    def __init__(self):
        """Initialize Aurora SDK with component-based architecture."""
        # Create core controller
        self._controller = Controller()
        
        # Create session automatically - one session per SDK object
        try:
            self._controller.create_session()
        except Exception as e:
            raise AuroraSDKError("Failed to initialize Aurora SDK session: {}".format(e))
        
        # Create components that depend on controller
        self._data_provider = DataProvider(self._controller)
        self._map_manager = MapManager(self._controller)
        self._lidar_2d_map_builder = LIDAR2DMapBuilder(self._controller)
        self._enhanced_imaging = EnhancedImaging(self._controller)
        self._floor_detector = FloorDetector(self._controller)
        self._data_recorder = DataRecorder(self._controller)

        # Set cross-component references
        self._enhanced_imaging._set_data_provider(self._data_provider)
    
    @property
    def controller(self):
        """
        Get the Controller component.
        
        The Controller handles:
        - Device discovery and connection
        - Session management
        - Device control operations
        - Configuration management
        
        Returns:
            Controller: Controller component instance
        """
        return self._controller
    
    @property
    def data_provider(self):
        """
        Get the DataProvider component.
        
        The DataProvider handles:
        - Pose data retrieval
        - Camera image data
        - LiDAR scan data
        - IMU sensor data
        - Tracking data
        
        Returns:
            DataProvider: DataProvider component instance
        """
        return self._data_provider
    
    @property
    def map_manager(self):
        """
        Get the MapManager component.
        
        The MapManager component handles VSLAM (3D visual mapping):
        - VSLAM map creation and management
        - 3D SLAM operations
        - Relocalization in VSLAM maps
        - VSLAM map file operations
        
        Returns:
            MapManager: MapManager component instance
        """
        return self._map_manager
    
    @property
    def lidar_2d_map_builder(self):
        """
        Get the LIDAR2DMapBuilder component.
        
        The LIDAR2DMapBuilder component handles CoMap (2D LIDAR mapping):
        - 2D occupancy grid map generation
        - Real-time 2D map preview
        - 2D LIDAR map management
        - CoMap configuration and rendering
        
        Returns:
            LIDAR2DMapBuilder: LIDAR2DMapBuilder component instance
        """
        return self._lidar_2d_map_builder
    
    @property
    def floor_detector(self):
        """
        Get the FloorDetector component.
        
        The FloorDetector handles:
        - Auto floor detection histogram
        - Floor descriptions and current floor
        - Multi-floor environment detection
        
        Returns:
            FloorDetector: FloorDetector component instance
        """
        return self._floor_detector
    
    @property
    def enhanced_imaging(self):
        """
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
        """
        return self._enhanced_imaging

    @property
    def data_recorder(self):
        """
        Get the DataRecorder component.

        The DataRecorder component handles:
        - Recording raw sensor data to disk
        - Generating COLMAP-compatible datasets
        - Recording configuration and status monitoring
        - Dataset generation for offline processing

        Returns:
            DataRecorder: DataRecorder component instance
        """
        return self._data_recorder

    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self._cleanup()
    
    def __del__(self):
        """Destructor to ensure proper cleanup when object is garbage collected."""
        self._cleanup()
    
    def _cleanup(self):
        """Internal cleanup method called by both __exit__ and __del__."""
        try:
            if hasattr(self, '_controller') and self._controller:
                if self._controller.is_connected():
                    self._controller.disconnect()
                self._controller.release_session()
        except Exception:
            # Suppress exceptions during cleanup to avoid issues during garbage collection
            pass
    
    # Convenience helper methods for ease of use
    def create_session(self):
        """
        Convenience helper: Create SDK session.
        
        NOTE: Session is created automatically during SDK initialization.
        This method is deprecated and should not be called manually.
        
        Raises:
            AuroraSDKError: If session is already created
        """
        if self.controller.session_handle is not None:
            raise AuroraSDKError("Session already created automatically during SDK initialization. Do not call create_session() manually.")
        return self.controller.create_session()
    
    def connect(self, device_info=None, connection_string=None):
        """
        Convenience helper: Connect to an Aurora device.
        
        Args:
            device_info: Device info from discovery (preferred)
            connection_string: Direct connection string (fallback)
            
        Raises:
            ConnectionError: If connection fails
            AuroraSDKError: If session not created or invalid parameters
        """
        return self.controller.connect(device_info, connection_string)
    
    def disconnect(self):
        """Convenience helper: Disconnect from current device."""
        return self.controller.disconnect()
    
    def is_connected(self):
        """
        Convenience helper: Check if connected to a device.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.controller.is_connected()
    
    def discover_devices(self, timeout=10.0):
        """
        Convenience helper: Discover Aurora devices on the network.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered device information dictionaries
        """
        return self.controller.discover_devices(timeout)
    
    def get_version_info(self):
        """
        Convenience helper: Get SDK version information.
        
        Returns:
            dict containing version information
        """
        return self.controller.get_version_info()
    
    def connect_and_start(self, connection_string=None, auto_discover=True):
        """
        Convenience method to create session and connect to device.
        
        Args:
            connection_string: Optional specific device to connect to
            auto_discover: If True, discover devices if connection_string not provided
            
        Returns:
            bool: True if successfully connected
            
        Raises:
            AuroraSDKError: If connection fails
        """
        try:
            # Session already created automatically in constructor
            
            if connection_string:
                # Try to connect to specific device
                self.connect(connection_string=connection_string)
            elif auto_discover:
                # Discover and connect to first available device
                devices = self.discover_devices(timeout=5.0)
                if not devices:
                    raise AuroraSDKError("No Aurora devices found")
                
                # Try to connect to first device
                self.connect(device_info=devices[0])
            else:
                raise AuroraSDKError("No connection method specified")
            
            return True
            
        except Exception as e:
            # Cleanup on failure
            self._cleanup()
            raise AuroraSDKError("Failed to connect and start: {}".format(e))
    
    def get_device_status(self):
        """
        Get comprehensive device status information.
        
        Returns:
            dict: Device status including connection state, device info, etc.
        """
        status = {
            'connected': self.is_connected(),
            'session_active': self.controller.session_handle is not None,
            'device_info': None,
            'sdk_version': self.get_version_info()
        }
        
        if status['connected']:
            try:
                status['device_info'] = self.controller.get_device_info()
            except:
                status['device_info'] = None
        
        return status
    
    def quick_start_preview(self, connection_string=None):
        """
        Quick start method for camera preview applications.
        
        Args:
            connection_string: Optional specific device to connect to
            
        Returns:
            bool: True if successfully started
        """
        try:
            self.connect_and_start(connection_string)
            return True
        except Exception:
            return False
    
    def release(self):
        """
        Convenience helper: Release SDK session and cleanup resources.
        
        This method provides a simple way to cleanup the SDK session,
        disconnecting from the device if connected and releasing the session.
        """
        self._cleanup()
    
    def get_device_info(self):
        """
        Convenience helper: Get device information.
        
        Returns:
            Device information object
        """
        return self.controller.get_device_info()
    
    def get_current_pose(self, use_se3=False):
        """
        Convenience helper: Get current device pose with timestamp.
        
        Args:
            use_se3: If True, return pose in SE3 format (position + quaternion)
                    If False, return pose in Euler format (position + roll/pitch/yaw)
                    
        Returns:
            tuple: (position, rotation, timestamp_ns) where:
                - position: (x, y, z) coordinates in meters
                - rotation: (qx, qy, qz, qw) quaternion if use_se3=True, 
                           (roll, pitch, yaw) Euler angles if use_se3=False
                - timestamp_ns: timestamp in nanoseconds
        """
        return self.data_provider.get_current_pose(use_se3)
    
    def get_tracking_frame(self):
        """
        Convenience helper: Get tracking frame with images and keypoints.
        
        Returns:
            TrackingFrame object with left/right images and keypoints
        """
        return self.data_provider.get_tracking_frame()
    
    def get_camera_preview(self):
        """
        Convenience helper: Get camera preview images.
        
        Returns:
            tuple: (left_image, right_image) as ImageFrame objects
        """
        return self.data_provider.get_camera_preview()
    
    def get_map_info(self):
        """
        Convenience helper: Get global mapping information.

        Returns:
            GlobalMappingInfo: Object containing map status, active map ID, map count, etc.
        """
        return self.data_provider.get_global_mapping_info()
    
    def get_recent_lidar_scan(self, max_points=8192):
        """
        Convenience helper: Get recent LiDAR scan data.
        
        Args:
            max_points: Maximum number of scan points to retrieve
        
        Returns:
            LidarScanData object with scan points and metadata
        """
        return self.data_provider.get_recent_lidar_scan(max_points)
    
    def start_lidar_2d_map_preview(self, resolution=0.05):
        """
        Convenience helper: Start LIDAR 2D map preview generation.
        
        Args:
            resolution: Map resolution in meters per pixel (default: 0.05m = 5cm)
        """
        return self.lidar_2d_map_builder.start_lidar_2d_map_preview(resolution)
    
    def stop_lidar_2d_map_preview(self):
        """
        Convenience helper: Stop LIDAR 2D map preview generation.
        """
        return self.lidar_2d_map_builder.stop_lidar_2d_map_preview()
    
    def enable_map_data_syncing(self, enable):
        """
        Convenience helper: Enable/disable map data syncing.
        
        Args:
            enable: True to enable, False to disable
        """
        return self.controller.enable_map_data_syncing(enable)
    
    def get_map_data(self, map_ids=None, fetch_kf=True, fetch_mp=True, fetch_mapinfo=False,
                     kf_fetch_flags=None, mp_fetch_flags=None):
        """
        Convenience helper: Get visual map data (map points and keyframes).
        
        Args:
            map_ids: Optional list/tuple of map IDs to fetch.
                    - None (default): fetches only the active map
                    - Empty list []: fetches all maps
                    - List of IDs: fetches specific maps
            fetch_kf: Whether to fetch keyframes (default: True)
            fetch_mp: Whether to fetch map points (default: True)
            fetch_mapinfo: Whether to fetch map info (default: False)
            kf_fetch_flags: Keyframe fetch flags (default: None, uses FETCH_ALL)
            mp_fetch_flags: Map point fetch flags (default: None, uses FETCH_ALL)
        
        Returns:
            dict: Dictionary containing 'map_points', 'keyframes', 'loop_closures', and 'map_info'
        """
        return self.data_provider.get_map_data(
            map_ids=map_ids,
            fetch_kf=fetch_kf,
            fetch_mp=fetch_mp,
            fetch_mapinfo=fetch_mapinfo,
            kf_fetch_flags=kf_fetch_flags,
            mp_fetch_flags=mp_fetch_flags
        )
    
    def require_mapping_mode(self, timeout_ms=10000):
        """
        Convenience helper: Require device to enter mapping mode.
        
        Args:
            timeout_ms: Timeout in milliseconds
        """
        return self.controller.require_mapping_mode(timeout_ms)
    
    def resync_map_data(self, invalidate_cache=True):
        """
        Convenience helper: Force resync of map data.
        
        Args:
            invalidate_cache: Whether to invalidate cache
        """
        return self.controller.resync_map_data(invalidate_cache)
    
    def convert_quaternion_to_euler(self, qx, qy, qz, qw):
        """
        Convert quaternion to Euler angles.
        
        Args:
            qx, qy, qz, qw: Quaternion components
            
        Returns:
            tuple: (roll, pitch, yaw) in radians
            
        Raises:
            AuroraSDKError: If conversion fails
        """
        # Use controller's c_bindings since we don't store our own
        self.controller._ensure_c_bindings()
        return self.controller._c_bindings.convert_quaternion_to_euler(qx, qy, qz, qw)
    
