"""
Aurora SDK Enhanced Imaging component (SDK 2.0).

Handles Enhanced Imaging operations including depth camera frames, semantic segmentation,
camera calibration, and transform calibration.
"""

import time
from .c_bindings import get_c_bindings
from .data_types import (
    CameraCalibrationInfo, TransformCalibrationInfo, ImageFrame,
    DEPTHCAM_FRAME_TYPE_DEPTH_MAP, DEPTHCAM_FRAME_TYPE_POINT3D
)
from .exceptions import AuroraSDKError, ConnectionError, DataNotReadyError


class EnhancedImaging:
    """
    Enhanced Imaging component for Aurora SDK 2.0.
    
    Responsible for:
    - Depth camera frame retrieval and processing
    - Semantic segmentation frame retrieval and processing
    - Camera calibration data access
    - Transform calibration data access
    - Model switching for semantic segmentation
    - Depth-aligned segmentation map calculation
    """
    
    def __init__(self, controller, c_bindings=None):
        """
        Initialize Enhanced Imaging component.
        
        Args:
            controller: Controller component instance
            c_bindings: Optional C bindings instance
        """
        self._controller = controller
        self._data_provider = None  # Will be set by SDK
        try:
            self._c_bindings = c_bindings or get_c_bindings()
        except Exception as e:
            # Store the error for later when methods are actually called
            self._c_bindings = None
            self._c_bindings_error = str(e)
    
    def _set_data_provider(self, data_provider):
        """Set data provider reference (called by SDK)."""
        self._data_provider = data_provider
    
    def _ensure_c_bindings(self):
        """Ensure C bindings are available or raise appropriate error."""
        if self._c_bindings is None:
            raise AuroraSDKError(f"Aurora SDK not available: {getattr(self, '_c_bindings_error', 'Unknown error')}")
    
    def _ensure_connected(self):
        """Ensure we're connected to a device."""
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")
    
    # Depth Camera Operations
    
    def is_depth_camera_ready(self):
        """
        Check if depth camera is ready for frame capture.
        
        Returns:
            bool: True if depth camera is ready, False otherwise
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.depthcam_is_ready(self._controller.session_handle)
        except Exception:
            return False
    
    def wait_depth_camera_next_frame(self, timeout_ms=1000):
        """
        Wait for the next depth camera frame.
        
        Args:
            timeout_ms (int): Timeout in milliseconds
            
        Returns:
            bool: True if frame is available, False if timeout
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.depthcam_wait_next_frame(self._controller.session_handle, timeout_ms)
        except Exception:
            return False
    
    def peek_depth_camera_frame(self, frame_type=DEPTHCAM_FRAME_TYPE_DEPTH_MAP, timestamp_ns=0, allow_nearest_frame=True):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            frame_desc, frame_data = self._c_bindings.peek_depth_camera_frame(
                self._controller.session_handle, frame_type
            )
            
            if frame_data:
                # Use appropriate format based on frame type
                if frame_type == DEPTHCAM_FRAME_TYPE_POINT3D:
                    return ImageFrame.from_point3d_struct(frame_desc, frame_data)
                else:  # DEPTHCAM_FRAME_TYPE_DEPTH_MAP
                    return ImageFrame.from_depth_camera_struct(frame_desc, frame_data)
            return None
            
        except AuroraSDKError as e:
            if "NOT_READY" in str(e):
                return None
            raise e
        except Exception as e:
            raise AuroraSDKError(f"Failed to get depth camera frame: {e}")
    
    def peek_depth_camera_related_rectified_image(self, timestamp_ns):
        """
        Get the related rectified camera image for a depth frame.
        
        Args:
            timestamp_ns (int): Timestamp of the depth frame to get related image for
            
        Returns:
            ImageFrame: Camera image frame data with rectified image
            None: If no frame is available
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve image
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            frame_desc, frame_data = self._c_bindings.peek_depth_camera_related_rectified_image(
                self._controller.session_handle, timestamp_ns
            )
            
            if frame_data:
                # Create ImageFrame from the enhanced imaging frame descriptor
                image_frame = ImageFrame(
                    width=frame_desc.image_desc.width,
                    height=frame_desc.image_desc.height,
                    pixel_format=frame_desc.image_desc.format,
                    timestamp_ns=frame_desc.timestamp_ns,
                    data=frame_data
                )
                return image_frame
            return None
            
        except AuroraSDKError as e:
            if "NOT_READY" in str(e):
                return None
            raise e
        except Exception as e:
            raise AuroraSDKError(f"Failed to get rectified image: {e}")
    
    # Semantic Segmentation Operations
    
    def is_semantic_segmentation_ready(self):
        """
        Check if semantic segmentation is ready for frame capture.
        
        Returns:
            bool: True if semantic segmentation is ready, False otherwise
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.semantic_segmentation_is_ready(self._controller.session_handle)
        except Exception:
            return False
    
    def wait_semantic_segmentation_next_frame(self, timeout_ms=1000):
        """
        Wait for the next semantic segmentation frame.
        
        Args:
            timeout_ms (int): Timeout in milliseconds
            
        Returns:
            bool: True if frame is available, False if timeout
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.wait_semantic_segmentation_next_frame(
                self._controller.session_handle, timeout_ms
            )
        except Exception as e:
            return False
    
    def get_semantic_segmentation_config(self):
        """
        Get semantic segmentation configuration information.
        
        Returns:
            SemanticSegmentationConfig: Configuration including model type, class count, etc.
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve configuration
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            config = self._c_bindings.get_semantic_segmentation_config(self._controller.session_handle)
            return config
        except Exception as e:
            raise AuroraSDKError(f"Failed to get semantic segmentation config: {e}")
    
    def get_semantic_segmentation_labels(self):
        """
        Get semantic segmentation label information.
        
        Returns:
            SemanticSegmentationLabelInfo: Label set name and label names
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve label information
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            label_info = self._c_bindings.get_semantic_segmentation_labels(self._controller.session_handle)
            return label_info
        except Exception as e:
            raise AuroraSDKError(f"Failed to get semantic segmentation labels: {e}")
    
    def get_semantic_segmentation_label_set_name(self):
        """
        Get the current semantic segmentation label set name.
        
        Returns:
            str: Label set name (e.g., "indoor_80_classes", "outdoor_18_classes")
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_semantic_segmentation_label_set_name(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get label set name: {e}")
    
    def peek_semantic_segmentation_frame(self, timestamp_ns=0, allow_nearest_frame=True):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            frame_desc, segmentation_data = self._c_bindings.peek_semantic_segmentation_frame(
                self._controller.session_handle, timestamp_ns, allow_nearest_frame
            )
            
            if segmentation_data:
                # Create unified ImageFrame from the enhanced imaging frame descriptor
                image_frame = ImageFrame(
                    width=frame_desc.image_desc.width,
                    height=frame_desc.image_desc.height,
                    pixel_format=frame_desc.image_desc.format,
                    timestamp_ns=frame_desc.timestamp_ns,
                    data=segmentation_data
                )
                return image_frame
            return None
            
        except AuroraSDKError as e:
            if "NOT_READY" in str(e):
                return None
            raise e
        except Exception as e:
            raise AuroraSDKError(f"Failed to get semantic segmentation frame: {e}")
    
    def calc_depth_camera_aligned_segmentation_map(self, segmentation_frame):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        if not isinstance(segmentation_frame, ImageFrame):
            raise ValueError("segmentation_frame must be an ImageFrame instance")
        
        if not segmentation_frame.data:
            raise ValueError("segmentation_frame must contain image data")
        
        try:
            aligned_data, aligned_width, aligned_height = self._c_bindings.calc_depth_aligned_segmentation_map(
                self._controller.session_handle,
                segmentation_frame.data,
                segmentation_frame.width,
                segmentation_frame.height
            )
            
            return aligned_data, aligned_width, aligned_height
            
        except Exception as e:
            raise AuroraSDKError(f"Failed to calculate depth aligned segmentation map: {e}")
    
    # Convenience methods (delegating to DeviceBasicInfo for proper capability checking)
    def is_depth_camera_supported(self):
        """
        Check if depth camera is supported by the current device.
        
        This is a convenience method that delegates to DeviceBasicInfo.isSupportDepthCamera().
        
        Returns:
            bool: True if depth camera is supported, False otherwise
        """
        try:
            if self._data_provider:
                device_basic_info = self._data_provider.get_last_device_basic_info()
                return device_basic_info.isSupportDepthCamera()
            return False
        except:
            return False
    
    def is_semantic_segmentation_supported(self):
        """
        Check if semantic segmentation is supported by the current device.
        
        This is a convenience method that delegates to DeviceBasicInfo.isSupportSemanticSegmentation().
        
        Returns:
            bool: True if semantic segmentation is supported, False otherwise
        """
        try:
            if self._data_provider:
                device_basic_info = self._data_provider.get_last_device_basic_info()
                return device_basic_info.isSupportSemanticSegmentation()
            return False
        except:
            return False
    
    def is_semantic_segmentation_alternative_model(self):
        """
        Check if semantic segmentation is currently using the alternative model.
        
        Returns:
            bool: True if using alternative model, False if using default model
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to check model status
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.is_semantic_segmentation_using_alternative_model(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to check semantic segmentation model: {e}")
    
    
    def get_depth_camera_config(self):
        """
        Get depth camera configuration information.
        
        Returns:
            DepthcamConfigInfo: Configuration information
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to retrieve configuration
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.depthcam_get_config_info(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError(f"Failed to get depth camera config: {e}")
    
    
