"""
Aurora SDK Controller component.

Handles device connection, session management, and control operations.
"""

from .c_bindings import get_c_bindings
from .data_types import DeviceInfo
from .exceptions import AuroraSDKError, ConnectionError


class Controller:
    """
    Controller component for Aurora SDK.
    
    Responsible for:
    - Device discovery and connection management
    - Session lifecycle (create, release)
    - Device control operations (reset, reboot, etc.)
    - Configuration management
    """
    
    def __init__(self, c_bindings=None):
        """Initialize Controller component."""
        try:
            self._c_bindings = c_bindings or get_c_bindings()
        except Exception as e:
            # Store the error for later when methods are actually called
            self._c_bindings = None
            self._c_bindings_error = str(e)
        
        self._session_handle = None
        self._connected = False
        self._device_info = None
        self._current_server_info = None
    
    def _ensure_c_bindings(self):
        """Ensure C bindings are available or raise appropriate error."""
        if self._c_bindings is None:
            raise AuroraSDKError("Aurora SDK not available: {}".format(getattr(self, '_c_bindings_error', 'Unknown error')))
    
    def get_version_info(self):
        """
        Get SDK version information.
        
        Returns:
            dict containing version information
        """
        self._ensure_c_bindings()
        version_info = self._c_bindings.get_version_info()
        return {
            'sdk_name': version_info.sdk_name.decode('utf-8') if version_info.sdk_name else 'Unknown',
            'version_string': version_info.sdk_version_string.decode('utf-8') if version_info.sdk_version_string else 'Unknown',
            'build_time': version_info.sdk_build_time.decode('utf-8') if version_info.sdk_build_time else 'Unknown',
            'feature_flags': version_info.sdk_feature_flags
        }
    
    def create_session(self):
        """
        Create SDK session.
        
        Raises:
            AuroraSDKError: If session creation fails
        """
        self._ensure_c_bindings()
        
        if self._session_handle is not None:
            raise AuroraSDKError("Session already created")
        
        try:
            self._session_handle = self._c_bindings.create_session()
        except Exception as e:
            raise AuroraSDKError("Failed to create session: {}".format(e))
    
    def release_session(self):
        """Release SDK session."""
        if self._session_handle is not None:
            try:
                self._c_bindings.release_session(self._session_handle)
            except:
                pass  # Ignore errors during cleanup
            finally:
                self._session_handle = None
                self._connected = False
                self._device_info = None
                self._current_server_info = None
    
    def discover_devices(self, timeout=10.0):
        """
        Discover Aurora devices on the network.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered device information dictionaries
            
        Raises:
            AuroraSDKError: If discovery fails
        """
        self._ensure_c_bindings()
        
        if self._session_handle is None:
            raise AuroraSDKError("Session not created")
        
        try:
            return self._c_bindings.discover_devices(self._session_handle, timeout)
        except Exception as e:
            raise AuroraSDKError("Device discovery failed: {}".format(e))
    
    def connect(self, device_info=None, connection_string=None):
        """
        Connect to an Aurora device.
        
        Args:
            device_info: Device info from discovery (preferred)
            connection_string: Direct connection string (fallback)
            
        Raises:
            ConnectionError: If connection fails
            AuroraSDKError: If session not created or invalid parameters
        """
        self._ensure_c_bindings()
        
        if self._session_handle is None:
            raise AuroraSDKError("Session not created")
        
        if self._connected:
            raise ConnectionError("Already connected to a device")
        
        if device_info is None and connection_string is None:
            raise AuroraSDKError("Either device_info or connection_string must be provided")
        
        try:
            if device_info:
                self._current_server_info = self._c_bindings.connect_device(self._session_handle, device_info)
            else:
                self._current_server_info = self._c_bindings.connect_string(self._session_handle, connection_string)
            
            self._connected = True
            
        except Exception as e:
            raise ConnectionError("Failed to connect: {}".format(e))
    
    def disconnect(self):
        """Disconnect from current device."""
        if self._connected and self._session_handle is not None:
            try:
                self._c_bindings.disconnect(self._session_handle)
            except:
                pass  # Ignore errors during cleanup
            finally:
                self._connected = False
                self._current_server_info = None
    
    def is_connected(self):
        """
        Check if connected to a device.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected and self._session_handle is not None
    
    def get_device_info(self):
        """
        Get connected device information.
        
        Returns:
            DeviceInfo object containing device details
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to get device info
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            device_basic_info, timestamp = self._c_bindings.get_device_basic_info(self._session_handle)
            return DeviceInfo.from_c_struct(device_basic_info)
        except Exception as e:
            raise AuroraSDKError("Failed to get device info: {}".format(e))
    
    def enable_raw_data_subscription(self, enable):
        """
        Enable/disable raw data subscription for better image quality.
        
        Args:
            enable: True to enable, False to disable
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.enable_raw_data_subscription(self._session_handle, enable)
        except Exception as e:
            raise AuroraSDKError("Failed to set raw data subscription: {}".format(e))
    
    def reset_device(self):
        """
        Reset the connected device.
        
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If reset fails
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            # Implementation would depend on C SDK having reset function
            raise AuroraSDKError("Device reset not implemented in C SDK")
        except Exception as e:
            raise AuroraSDKError("Failed to reset device: {}".format(e))
    
    def enable_map_data_syncing(self, enable):
        """
        Enable/disable map data syncing.
        
        Args:
            enable: True to enable, False to disable
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.set_map_data_syncing(self._session_handle, enable)
        except Exception as e:
            raise AuroraSDKError("Failed to set map data syncing: {}".format(e))
    
    def require_mapping_mode(self, timeout_ms=10000):
        """
        Require device to enter mapping mode.
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.require_mapping_mode(self._session_handle, timeout_ms)
        except Exception as e:
            raise AuroraSDKError("Failed to require mapping mode: {}".format(e))
    
    def resync_map_data(self, invalidate_cache=True):
        """
        Force resync of map data.
        
        Args:
            invalidate_cache: Whether to invalidate cache
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.resync_map_data(self._session_handle, invalidate_cache)
        except Exception as e:
            raise AuroraSDKError("Failed to resync map data: {}".format(e))
    
    # Enhanced Imaging Operations (SDK 2.0)
    def set_enhanced_imaging_subscription(self, enhanced_image_type, enable):
        """
        Set enhanced imaging subscription for specific image type.
        
        Args:
            enhanced_image_type (int): Type of enhanced image (0: depth, 1: semantic segmentation)
            enable (bool): True to enable, False to disable
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.set_enhanced_imaging_subscription(self._session_handle, enhanced_image_type, enable)
            return True
        except Exception as e:
            # Log the error but return False instead of raising
            print("Warning: Failed to set enhanced imaging subscription: {}".format(e))
            return False
    
    def is_enhanced_imaging_subscribed(self, enhanced_image_type):
        """
        Check if enhanced imaging is subscribed for specific image type.
        
        Args:
            enhanced_image_type (int): Type of enhanced image (0: depth, 1: semantic segmentation)
            
        Returns:
            bool: True if subscribed, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            return self._c_bindings.is_enhanced_imaging_subscribed(self._session_handle, enhanced_image_type)
        except Exception as e:
            raise AuroraSDKError("Failed to check enhanced imaging subscription: {}".format(e))
    
    def require_semantic_segmentation_alternative_model(self, use_alternative_model, timeout_ms=5000):
        """
        Require semantic segmentation to use alternative model.
        
        Args:
            use_alternative_model (bool): True to use alternative model, False for default
            timeout_ms (int): Timeout in milliseconds
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.require_semantic_segmentation_alternative_model(
                self._session_handle, use_alternative_model, timeout_ms
            )
        except Exception as e:
            raise AuroraSDKError("Failed to set semantic segmentation model: {}".format(e))
    
    def require_relocalization(self, timeout_ms=5000):
        """
        Require the device to perform relocalization.
        
        This method tells the Aurora device to perform relocalization to determine
        its position within a previously built map. The device will use its current
        sensor readings to match against the existing map.
        
        Args:
            timeout_ms (int): Timeout in milliseconds (default: 5000)
            
        Returns:
            bool: True if relocalization was successful, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If relocalization operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            from .data_types import ERRORCODE_OK
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_controller_require_relocalization(
                self._session_handle, 
                timeout_ms
            )
            
            if error_code == ERRORCODE_OK:
                return True
            else:
                return False
                
        except Exception as e:
            raise AuroraSDKError("Failed to perform relocalization: {}".format(e))
    
    def cancel_relocalization(self):
        """
        Cancel an ongoing relocalization operation.
        
        Returns:
            bool: True if cancellation was successful, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If cancellation operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            from .data_types import ERRORCODE_OK
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_controller_cancel_relocalization(
                self._session_handle
            )
            
            if error_code == ERRORCODE_OK:
                return True
            else:
                return False
                
        except Exception as e:
            raise AuroraSDKError("Failed to cancel relocalization: {}".format(e))

    def require_local_relocalization(self, center_pose, search_radius, timeout_ms=5000):
        """
        Require the device to perform local relocalization within a specified area.

        This method is more efficient than global relocalization as it searches
        only within a limited area around the specified center pose.

        Args:
            center_pose: Center pose for the search area. Can be:
                - PoseSE3 object
                - Tuple of (position, quaternion) where:
                  * position is (x, y, z)
                  * quaternion is (qx, qy, qz, qw)
            search_radius (float): Search radius in meters
            timeout_ms (int): Timeout in milliseconds (default: 5000)

        Returns:
            bool: True if relocalization was successful, False otherwise

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If local relocalization operation fails

        Example:
            center = ((1.0, 2.0, 0.0), (0.0, 0.0, 0.0, 1.0))
            sdk.controller.require_local_relocalization(center, search_radius=5.0)
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")

        try:
            from .data_types import ERRORCODE_OK, PoseSE3
            import ctypes

            # Convert pose to PoseSE3 if needed
            if isinstance(center_pose, tuple):
                position, quaternion = center_pose
                pose_se3 = PoseSE3()
                pose_se3.translation.x, pose_se3.translation.y, pose_se3.translation.z = position
                pose_se3.quaternion.x, pose_se3.quaternion.y, pose_se3.quaternion.z, pose_se3.quaternion.w = quaternion
            else:
                pose_se3 = center_pose

            error_code = self._c_bindings.lib.slamtec_aurora_sdk_controller_require_local_relocalization(
                self._session_handle,
                ctypes.byref(pose_se3),
                float(search_radius),
                timeout_ms
            )

            return error_code == ERRORCODE_OK

        except Exception as e:
            raise AuroraSDKError("Failed to perform local relocalization: {}".format(e))

    def require_local_map_merge(self, center_pose, search_radius, timeout_ms=5000):
        """
        Require the device to perform local map merge within a specified area.

        This merges map segments within a specified area around the center pose.

        Args:
            center_pose: Center pose for the merge area. Can be:
                - PoseSE3 object
                - Tuple of (position, quaternion) where:
                  * position is (x, y, z)
                  * quaternion is (qx, qy, qz, qw)
            search_radius (float): Search radius in meters
            timeout_ms (int): Timeout in milliseconds (default: 5000)

        Returns:
            bool: True if map merge was successful, False otherwise

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If local map merge operation fails

        Example:
            center = ((1.0, 2.0, 0.0), (0.0, 0.0, 0.0, 1.0))
            sdk.controller.require_local_map_merge(center, search_radius=5.0)
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")

        try:
            from .data_types import ERRORCODE_OK, PoseSE3
            import ctypes

            # Convert pose to PoseSE3 if needed
            if isinstance(center_pose, tuple):
                position, quaternion = center_pose
                pose_se3 = PoseSE3()
                pose_se3.translation.x, pose_se3.translation.y, pose_se3.translation.z = position
                pose_se3.quaternion.x, pose_se3.quaternion.y, pose_se3.quaternion.z, pose_se3.quaternion.w = quaternion
            else:
                pose_se3 = center_pose

            error_code = self._c_bindings.lib.slamtec_aurora_sdk_controller_require_local_map_merge(
                self._session_handle,
                ctypes.byref(pose_se3),
                float(search_radius),
                timeout_ms
            )

            return error_code == ERRORCODE_OK

        except Exception as e:
            raise AuroraSDKError("Failed to perform local map merge: {}".format(e))

    def get_last_relocalization_status(self, timeout_ms=1000):
        """
        Get the last relocalization status from the device.

        Args:
            timeout_ms (int): Timeout in milliseconds (default: 1000)

        Returns:
            int: Relocalization status value:
                - DEVICE_RELOCALIZATION_STATUS_NONE (0)
                - DEVICE_RELOCALIZATION_STATUS_IN_PROGRESS (1)
                - DEVICE_RELOCALIZATION_STATUS_SUCCEED (2)
                - DEVICE_RELOCALIZATION_STATUS_FAILED (3)

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to query relocalization status

        Example:
            from slamtec_aurora_sdk.data_types import DEVICE_RELOCALIZATION_STATUS_SUCCEED
            status = sdk.controller.get_last_relocalization_status()
            if status == DEVICE_RELOCALIZATION_STATUS_SUCCEED:
                print("Relocalization succeeded!")
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")

        try:
            from .data_types import ERRORCODE_OK
            import ctypes

            status_out = ctypes.c_uint32()

            error_code = self._c_bindings.lib.slamtec_aurora_sdk_controller_get_last_relocalization_status(
                self._session_handle,
                ctypes.byref(status_out),
                timeout_ms
            )

            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to get relocalization status (error code: {})".format(error_code))

            return status_out.value

        except Exception as e:
            raise AuroraSDKError("Failed to get relocalization status: {}".format(e))

    def require_map_reset(self, timeout_ms=10000):
        """
        Require the device to reset its map.
        
        This will clear the current SLAM map and start mapping from scratch.
        
        Args:
            timeout_ms (int): Timeout in milliseconds (default: 10000)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If map reset operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.require_map_reset(self._session_handle, timeout_ms)
        except Exception as e:
            raise AuroraSDKError("Failed to reset map: {}".format(e))
    
    def require_pure_localization_mode(self, timeout_ms=10000):
        """
        Require the device to enter pure localization mode.
        
        In this mode, the device will not add new features to the map but will
        only use existing map features for localization.
        
        Args:
            timeout_ms (int): Timeout in milliseconds (default: 10000)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If mode switch operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.require_pure_localization_mode(self._session_handle, timeout_ms)
        except Exception as e:
            raise AuroraSDKError("Failed to enter pure localization mode: {}".format(e))
    
    def is_device_connection_alive(self):
        """
        Check if the device connection is alive and healthy.
        
        Returns:
            bool: True if connection is alive, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            return False
        
        try:
            return self._c_bindings.is_device_connection_alive(self._session_handle)
        except Exception:
            return False
    
    def is_raw_data_subscribed(self):
        """
        Check if raw data subscription is active.
        
        Returns:
            bool: True if raw data is subscribed, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            return False
        
        try:
            return self._c_bindings.is_raw_data_subscribed(self._session_handle)
        except Exception:
            return False
    
    # SUPERVISOR FIX: Additional critical missing Controller methods
    def set_low_rate_mode(self, enable):
        """
        Enable/disable low rate mode for bandwidth management.
        
        Args:
            enable (bool): True to enable low rate mode, False to disable
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.set_low_rate_mode(self._session_handle, enable)
        except Exception as e:
            raise AuroraSDKError("Failed to set low rate mode: {}".format(e))
    
    def set_loop_closure(self, enable, timeout_ms=5000):
        """
        Enable/disable loop closure detection.
        
        Args:
            enable (bool): True to enable loop closure, False to disable
            timeout_ms (int): Timeout in milliseconds (default: 5000)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If operation fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.set_loop_closure(self._session_handle, enable, timeout_ms)
        except Exception as e:
            raise AuroraSDKError("Failed to set loop closure: {}".format(e))
    
    def force_map_global_optimization(self, timeout_ms=30000):
        """
        Force global map optimization.
        
        Args:
            timeout_ms (int): Timeout in milliseconds (default: 30000)
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If optimization fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            self._c_bindings.force_map_global_optimization(self._session_handle, timeout_ms)
        except Exception as e:
            raise AuroraSDKError("Failed to force global optimization: {}".format(e))
    
    def send_custom_command(self, command_id, data=None, timeout_ms=5000):
        """
        Send custom command to device.
        
        Args:
            command_id (int): Command ID (uint64)
            data (bytes or str, optional): Command data
            timeout_ms (int): Timeout in milliseconds (default: 5000)
            
        Returns:
            bytes: Response data from device
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If command fails
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        try:
            return self._c_bindings.send_custom_command(self._session_handle, command_id, data, timeout_ms)
        except Exception as e:
            raise AuroraSDKError("Failed to send custom command: {}".format(e))
    
    def set_keyframe_fetch_flags(self, flags):
        """
        Set keyframe fetch flags to control what data is fetched.
        
        Args:
            flags (int): Fetch flags (e.g. SLAMTEC_AURORA_SDK_KEYFRAME_FETCH_FLAG_RELATED_MP)
            
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        self._c_bindings.set_keyframe_fetch_flags(self._session_handle, flags)
    
    def get_keyframe_fetch_flags(self):
        """
        Get current keyframe fetch flags.
        
        Returns:
            int: Current fetch flags
            
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        return self._c_bindings.get_keyframe_fetch_flags(self._session_handle)
    
    def set_map_point_fetch_flags(self, flags):
        """
        Set map point fetch flags to control what data is fetched.
        
        Args:
            flags (int): Fetch flags
            
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        self._c_bindings.set_map_point_fetch_flags(self._session_handle, flags)
    
    def get_map_point_fetch_flags(self):
        """
        Get current map point fetch flags.
        
        Returns:
            int: Current fetch flags
            
        Raises:
            ConnectionError: If not connected to a device
        """
        self._ensure_c_bindings()
        if not self.is_connected():
            raise ConnectionError("Not connected to any device")
        
        return self._c_bindings.get_map_point_fetch_flags(self._session_handle)
    
    @property
    def session_handle(self):
        """Get the session handle for use by other components."""
        return self._session_handle