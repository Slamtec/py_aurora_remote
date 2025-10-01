"""
Aurora SDK DataProvider component.

Handles data retrieval operations including pose, images, tracking data, and sensor data.
"""

import time
from .c_bindings import get_c_bindings
from .data_types import ImageFrame, TrackingFrame, ScanData, LidarScanData, DeviceBasicInfoWrapper, DeviceInfo
from .exceptions import AuroraSDKError, ConnectionError, DataNotReadyError


class DataProvider:
    """
    DataProvider component for Aurora SDK.
    
    Responsible for:
    - Pose data retrieval (current pose, pose history)
    - Camera image data (preview, tracking frames)
    - LiDAR scan data
    - IMU sensor data
    - Tracking and mapping data
    """
    
    def __init__(self, controller, c_bindings=None):
        """
        Initialize DataProvider component.
        
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
    
    def get_current_pose(self, use_se3=True):
        """
        Get current device pose with timestamp.
        
        Args:
            use_se3: If True, return SE3 format (position + quaternion),
                    if False, return Euler format (position + euler angles)
                    
        Returns:
            Tuple of (position, rotation, timestamp_ns)
            - position: (x, y, z) tuple in meters
            - rotation: (qx, qy, qz, qw) if use_se3, (roll, pitch, yaw) otherwise
            - timestamp_ns: timestamp in nanoseconds
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to get pose
        """
        self._ensure_connected()
        
        try:
            if use_se3:
                pose, timestamp_ns = self._c_bindings.get_current_pose_se3(self._controller.session_handle)
                position = pose.translation.to_tuple()
                rotation = pose.quaternion.to_tuple()
            else:
                pose, timestamp_ns = self._c_bindings.get_current_pose(self._controller.session_handle)
                position = pose.translation.to_tuple()
                rotation = pose.rpy.to_tuple()
            
            return position, rotation, timestamp_ns
            
        except Exception as e:
            raise AuroraSDKError(f"Failed to get current pose: {e}")
    
    def get_camera_preview(self, timestamp_ns=0, allow_nearest_frame=True):
        """
        Get camera preview frames.
        
        Args:
            timestamp_ns (int): Timestamp in nanoseconds (0 for latest frame)
            allow_nearest_frame (bool): Allow nearest frame if exact timestamp not available
        
        Returns:
            Tuple of (left_frame, right_frame) ImageFrame objects
            
        Raises:
            ConnectionError: If not connected to a device
            DataNotReadyError: If camera data is not ready
            AuroraSDKError: If failed to get camera preview
        """
        self._ensure_connected()
        
        try:
            desc, left_data, right_data = self._c_bindings.peek_camera_preview_image(
                self._controller.session_handle, timestamp_ns, allow_nearest_frame)
            
            # Create ImageFrame objects
            left_frame = ImageFrame.from_c_desc(desc.left_image_desc, data=left_data)
            right_frame = ImageFrame.from_c_desc(desc.right_image_desc, data=right_data)
            
            # Set timestamp from stereo pair
            left_frame.timestamp_ns = desc.timestamp_ns
            right_frame.timestamp_ns = desc.timestamp_ns
            
            return left_frame, right_frame
            
        except Exception as e:
            if "error code: -7" in str(e):  # NOT_READY
                raise DataNotReadyError("Camera data not ready")
            elif "error code: -2" in str(e):  # INVALID_ARGUMENT
                raise AuroraSDKError(f"Invalid camera preview parameters: {e}")
            else:
                raise AuroraSDKError(f"Failed to get camera preview: {e}")
    
    def get_tracking_frame(self):
        """
        Get tracking frame data with keypoints and images.
        
        Returns:
            TrackingFrame object containing images, keypoints, pose, and tracking status
            
        Raises:
            ConnectionError: If not connected to a device
            DataNotReadyError: If tracking data is not ready
            AuroraSDKError: If failed to get tracking data
        """
        self._ensure_connected()
        
        try:
            tracking_info, left_keypoints, right_keypoints, left_image_data, right_image_data = self._c_bindings.peek_tracking_data(self._controller.session_handle)
            
            # Create TrackingFrame object with image data
            tracking_frame = TrackingFrame.from_c_struct(
                tracking_info, 
                left_keypoints=left_keypoints,
                right_keypoints=right_keypoints,
                left_image_data=left_image_data,
                right_image_data=right_image_data
            )
            
            return tracking_frame
            
        except Exception as e:
            if "error code: -7" in str(e):  # NOT_READY
                raise DataNotReadyError("Tracking data not ready")
            elif "error code: -2" in str(e):  # INVALID_ARGUMENT  
                raise AuroraSDKError(f"Invalid tracking parameters: {e}")
            else:
                raise AuroraSDKError(f"Failed to get tracking frame: {e}")
    
    def get_recent_lidar_scan(self, max_points=8192):
        """
        Get recent LiDAR scan data.
        
        Args:
            max_points: Maximum number of scan points to retrieve
            
        Returns:
            LidarScanData object containing scan points and metadata, or None if not available
            
        Raises:
            ConnectionError: If not connected to a device
            DataNotReadyError: If LiDAR data is not ready
            AuroraSDKError: If failed to get scan data
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            result = self._c_bindings.peek_recent_lidar_scan(self._controller.session_handle, max_points)
            if result is None:
                return None  # No scan data available
            
            scan_info, scan_points, scan_pose = result
            
            # Create LidarScanData object
            from .data_types import LidarScanData
            scan_data = LidarScanData.from_c_data(scan_info, scan_points)
            
            return scan_data
            
        except Exception as e:
            if "error code: -7" in str(e):  # NOT_READY
                raise DataNotReadyError("LiDAR data not ready")
            else:
                raise AuroraSDKError(f"Failed to get LiDAR scan: {e}")
    
    def get_imu_data(self):
        """
        Get IMU sensor data.
        
        Returns:
            List of IMUData objects containing accelerometer and gyroscope data
            
        Raises:
            ConnectionError: If not connected to a device
            DataNotReadyError: If IMU data is not ready
            AuroraSDKError: If failed to get IMU data
        """
        return self.peek_imu_data()
    
    def peek_imu_data(self, max_count=100):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            import ctypes
            from .data_types import IMUData, ERRORCODE_OK, ERRORCODE_NOT_READY
            
            # Use fixed 4096 buffer like C++ implementation
            max_count = 4096
            
            # Prepare output arrays exactly like C++ version
            imu_data_array = (IMUData * max_count)()
            actual_count = ctypes.c_size_t(0)
            
            # Call C API function exactly like C++ version
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_dataprovider_peek_imu_data(
                self._controller.session_handle,
                ctypes.cast(imu_data_array, ctypes.POINTER(IMUData)),
                max_count,
                ctypes.byref(actual_count)
            )
            
            # Handle error codes as specified in C++ SDK behavior
            if error_code == ERRORCODE_NOT_READY:
                # No data available yet - return empty list (non-blocking behavior)
                return []
            elif error_code != ERRORCODE_OK:
                raise AuroraSDKError(f"Failed to get IMU data, error code: {error_code}")
            
            # Convert to Python list with proper data copying
            result = []
            count = actual_count.value
            for i in range(count):
                # Create a new IMUData instance and copy all fields
                imu_copy = IMUData()
                imu_copy.timestamp_ns = imu_data_array[i].timestamp_ns
                imu_copy.imu_id = imu_data_array[i].imu_id
                # Copy acceleration array
                for j in range(3):
                    imu_copy.acc[j] = imu_data_array[i].acc[j]
                # Copy gyroscope array
                for j in range(3):
                    imu_copy.gyro[j] = imu_data_array[i].gyro[j]
                result.append(imu_copy)
            
            return result
            
        except Exception as e:
            if isinstance(e, (DataNotReadyError, AuroraSDKError)):
                raise
            else:
                raise AuroraSDKError(f"Failed to get IMU data: {e}")
    
    def get_map_data(self, map_ids=None, fetch_kf=True, fetch_mp=True, fetch_mapinfo=False,
                     kf_fetch_flags=None, mp_fetch_flags=None):
        """
        Get visual map data including map points and keyframes.
        
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
            dict: Dictionary containing 'map_points', 'keyframes', 'loop_closures', and 'map_info'.
                  Each map point contains: {'position': (x,y,z), 'id': int, 'map_id': int, 'timestamp': float}
                  Each keyframe contains: {'position': (x,y,z), 'rotation': (qx,qy,qz,qw), 'id': int, 'map_id': int, 'timestamp': float, 'fixed': bool}
                  Loop closures are tuples: [(from_keyframe_id, to_keyframe_id), ...]
                  Map info is a dict keyed by map_id containing: {'id': int, 'point_count': int, 'keyframe_count': int, 'connection_count': int}
            
        Raises:
            ConnectionError: If not connected to a device
            DataNotReadyError: If map data is not ready
            AuroraSDKError: If failed to get map data
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        # Import default flags
        from .data_types import SLAMTEC_AURORA_SDK_KF_FETCH_FLAG_ALL, SLAMTEC_AURORA_SDK_MP_FETCH_FLAG_ALL
        
        # Use default flags if not specified
        if kf_fetch_flags is None:
            kf_fetch_flags = SLAMTEC_AURORA_SDK_KF_FETCH_FLAG_ALL
        if mp_fetch_flags is None:
            mp_fetch_flags = SLAMTEC_AURORA_SDK_MP_FETCH_FLAG_ALL
        
        try:
            return self._c_bindings.access_map_data(
                self._controller.session_handle, 
                map_ids=map_ids,
                fetch_kf=fetch_kf,
                fetch_mp=fetch_mp,
                fetch_mapinfo=fetch_mapinfo,
                kf_fetch_flags=kf_fetch_flags,
                mp_fetch_flags=mp_fetch_flags
            )
            
        except Exception as e:
            if "NOT_READY" in str(e) or "timeout" in str(e).lower():
                raise DataNotReadyError("Map data not ready")
            # Return empty data on any error to prevent crashes
            return {'map_points': [], 'keyframes': [], 'loop_closures': [], 'map_info': {}}
    
    def peek_recent_lidar_scan_raw(self):
        """
        Get the most recent LiDAR scan data in raw format.
        
        Returns:
            tuple: (scan_info, scan_points) or None if not available
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.peek_recent_lidar_scan(self._controller.session_handle)
        except Exception as e:
            if "NOT_READY" in str(e):
                return None
            raise AuroraSDKError(f"Failed to get raw LiDAR scan data: {e}")
    
    def get_global_mapping_info(self):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_global_mapping_info(self._controller.session_handle)
            
        except Exception as e:
            raise AuroraSDKError(f"Failed to get global mapping info: {e}")
    
    # Camera Calibration Operations (SDK 2.0)
    def get_camera_calibration(self):
        """
        Get camera calibration parameters from the device.
        
        Returns:
            CameraCalibrationInfo: Camera calibration data including intrinsic and extrinsic parameters
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve calibration data
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            calibration_info = self._c_bindings.get_camera_calibration(self._controller.session_handle)
            return calibration_info
        except Exception as e:
            raise AuroraSDKError(f"Failed to get camera calibration: {e}")
    
    def get_transform_calibration(self):
        """
        Get transform calibration parameters from the device.
        
        Returns:
            TransformCalibrationInfo: Transform calibration data including camera-to-LiDAR transforms
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve transform calibration data
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            transform_info = self._c_bindings.get_transform_calibration(self._controller.session_handle)
            return transform_info
        except Exception as e:
            raise AuroraSDKError(f"Failed to get transform calibration: {e}")
    
    def get_last_device_basic_info(self):
        """
        Get the last device basic information.
        
        Returns:
            DeviceBasicInfoWrapper: Device basic information wrapper with capability checking methods
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve device basic info
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            basic_info, timestamp_ns = self._c_bindings.get_device_basic_info(self._controller.session_handle)
            return DeviceBasicInfoWrapper.from_c_struct(basic_info, timestamp_ns)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get device basic info: {e}")
    
    def get_device_info(self):
        """
        Get device information (legacy compatibility method).
        
        Returns:
            DeviceInfo: Legacy device info for backward compatibility
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve device info
        """
        # Get the new DeviceBasicInfo and convert to legacy format
        device_basic_info = self.get_last_device_basic_info()
        return DeviceInfo(
            device_name=device_basic_info.device_name,
            device_model_string=device_basic_info.device_model_string,
            firmware_version=device_basic_info.firmware_version,
            hardware_version=device_basic_info.hardware_version,
            serial_number=device_basic_info.serial_number,
            model_major=device_basic_info.model_major,
            model_sub=device_basic_info.model_sub,
            model_revision=device_basic_info.model_revision
        )
    
    # New high-priority DataProvider methods - ADDED
    def get_last_device_status(self):
        """
        Get the last device status information.
        
        Returns:
            Tuple of (DeviceStatus, timestamp_ns): Device status and timestamp
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve device status
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            status, timestamp_ns = self._c_bindings.get_last_device_status(self._controller.session_handle)
            return status, timestamp_ns
        except Exception as e:
            raise AuroraSDKError(f"Failed to get device status: {e}")
    
    def get_relocalization_status(self):
        """
        Get relocalization status information.
        
        Returns:
            RelocalizationStatus: Current relocalization status
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve relocalization status
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            status = self._c_bindings.get_relocalization_status(self._controller.session_handle)
            return status
        except Exception as e:
            raise AuroraSDKError(f"Failed to get relocalization status: {e}")
    
    def get_mapping_flags(self):
        """
        Get current mapping flags.
        
        Returns:
            int: Current mapping flags as bitmask
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve mapping flags
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            flags = self._c_bindings.get_mapping_flags(self._controller.session_handle)
            return flags
        except Exception as e:
            raise AuroraSDKError(f"Failed to get mapping flags: {e}")
    
    # CRITICAL MISSING METHODS that supervisor overlooked
    def get_imu_info(self):
        """
        Get IMU information.
        
        Returns:
            IMUInfo: IMU configuration and capabilities
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve IMU info
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_imu_info(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get IMU info: {e}")
    
    def get_all_map_info(self, max_count=32):
        """
        Get information about all maps.
        
        Args:
            max_count (int): Maximum number of maps to retrieve (default: 32)
            
        Returns:
            list: List of MapDesc objects containing map information
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve map info
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_all_map_info(self._controller.session_handle, max_count)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get all map info: {e}")
    
    def peek_history_pose(self, timestamp_ns, allow_interpolation=False, max_time_diff_ns=1000000000):
        """
        Peek historical pose at specific timestamp.
        
        This function retrieves pose data from the device's pose history buffer at the specified
        timestamp. The timestamp must be a valid sensor timestamp from actual sensor data 
        (e.g., from depth camera frames, IMU data, etc.). Using timestamp_ns=0 or system time
        will not work reliably.
        
        Args:
            timestamp_ns (int): REQUIRED valid sensor timestamp in nanoseconds. Must be an actual
                               timestamp from sensor data (e.g., depth_frame.timestamp_ns).
                               Do not use 0 or system time - these will not work.
            allow_interpolation (bool): Allow pose interpolation if exact timestamp not found.
                                      Set to False for exact timestamp matching (default: False)
            max_time_diff_ns (int): Maximum time difference in nanoseconds for matching 
                                   (default: 1 second)
            
        Returns:
            PoseSE3: Historical pose data containing position and quaternion
            
        Raises:
            ConnectionError: If not connected to a device
            DataNotReadyError: If historical pose data is not ready for the given timestamp
            AuroraSDKError: If failed to retrieve historical pose
            
        Example:
            # Get a depth frame first to obtain a valid timestamp
            depth_frame = sdk.enhanced_imaging.peek_depth_camera_frame(...)
            if depth_frame:
                # Use the depth frame's timestamp to get corresponding pose
                pose = sdk.data_provider.peek_history_pose(
                    timestamp_ns=depth_frame.timestamp_ns,
                    allow_interpolation=False
                )
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        
        try:
            return self._c_bindings.peek_history_pose(
                self._controller.session_handle, timestamp_ns, allow_interpolation, max_time_diff_ns
            )
        except Exception as e:
            if "error code: -7" in str(e):  # NOT_READY
                raise DataNotReadyError("Historical pose data not ready")
            else:
                raise AuroraSDKError(f"Failed to peek history pose: {e}")
    
