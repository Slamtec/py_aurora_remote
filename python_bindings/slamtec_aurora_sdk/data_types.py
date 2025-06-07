"""
Data types and structures for Aurora SDK Python bindings.
"""

import ctypes
import math

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class Vector3(ctypes.Structure):
    """3D vector structure (slamtec_aurora_sdk_position3d_t)."""
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double)
    ]
    
    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    def to_numpy(self):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for to_numpy() method")
        return np.array([self.x, self.y, self.z])


class Quaternion(ctypes.Structure):
    """Quaternion structure (slamtec_aurora_sdk_quaternion_t)."""
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
        ("w", ctypes.c_double)
    ]
    
    def to_tuple(self):
        return (self.x, self.y, self.z, self.w)
    
    def to_numpy(self):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for to_numpy() method")
        return np.array([self.x, self.y, self.z, self.w])


class EulerAngle(ctypes.Structure):
    """Euler angle structure (slamtec_aurora_sdk_euler_angle_t)."""
    _fields_ = [
        ("roll", ctypes.c_double),
        ("pitch", ctypes.c_double),
        ("yaw", ctypes.c_double)
    ]
    
    def to_tuple(self):
        return (self.roll, self.pitch, self.yaw)
    
    def to_numpy(self):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for to_numpy() method")
        return np.array([self.roll, self.pitch, self.yaw])


class Pose(ctypes.Structure):
    """Pose structure with translation and rotation (slamtec_aurora_sdk_pose_t)."""
    _fields_ = [
        ("translation", Vector3),
        ("rpy", EulerAngle)
    ]
    
    @property
    def position(self):
        return self.translation.to_tuple()
    
    @property
    def rotation(self):
        return self.rpy.to_tuple()


class PoseSE3(ctypes.Structure):
    """Pose structure in SE3 format (slamtec_aurora_sdk_pose_se3_t)."""
    _fields_ = [
        ("translation", Vector3),
        ("quaternion", Quaternion)
    ]
    
    @property
    def position(self):
        return self.translation.to_tuple()
    
    @property
    def rotation(self):
        return self.quaternion.to_tuple()


class ConnectionInfo(ctypes.Structure):
    """Connection info structure (slamtec_aurora_sdk_connection_info_t)."""
    _fields_ = [
        ("protocol_type", ctypes.c_char * 16),
        ("address", ctypes.c_char * 64),
        ("port", ctypes.c_uint16)
    ]


class ServerConnectionInfo(ctypes.Structure):
    """Server connection info structure (slamtec_aurora_sdk_server_connection_info_t)."""
    _fields_ = [
        ("connection_info", ConnectionInfo * 8),
        ("connection_count", ctypes.c_uint32)
    ]


class DeviceBasicInfo(ctypes.Structure):
    """Device basic info structure (slamtec_aurora_sdk_device_basic_info_t)."""
    _fields_ = [
        ("model_major", ctypes.c_uint16),
        ("model_sub", ctypes.c_uint16),
        ("model_revision", ctypes.c_uint16),
        ("firmware_version_string", ctypes.c_char * 32),
        ("firmware_build_date", ctypes.c_char * 16),
        ("firmware_build_time", ctypes.c_char * 16),
        ("device_sn", ctypes.c_uint8 * 16),
        ("device_name", ctypes.c_char * 16),
        ("hwfeature_bitmaps", ctypes.c_uint64),
        ("sensing_feature_bitmaps", ctypes.c_uint64),
        ("swfeature_bitmaps", ctypes.c_uint64),
        ("device_uptime_us", ctypes.c_uint64)
    ]


class ImageDesc(ctypes.Structure):
    """Image description structure (slamtec_aurora_sdk_image_desc_t)."""
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("stride", ctypes.c_uint32),
        ("format", ctypes.c_uint32),  # 0: gray, 1: rgb, 2: rgba, 3: depth, 4: point3D
        ("data_size", ctypes.c_uint32)
    ]


class StereoImagePairDesc(ctypes.Structure):
    """Stereo image pair description (slamtec_aurora_sdk_stereo_image_pair_desc_t)."""
    _fields_ = [
        ("timestamp_ns", ctypes.c_uint64),
        ("is_stereo", ctypes.c_uint32),
        ("left_image_desc", ImageDesc),
        ("right_image_desc", ImageDesc)
    ]


class StereoImagePairBuffer(ctypes.Structure):
    """Stereo image pair buffer (slamtec_aurora_sdk_stereo_image_pair_buffer_t)."""
    _fields_ = [
        ("imgdata_left", ctypes.c_void_p),
        ("imgdata_right", ctypes.c_void_p),
        ("imgdata_left_size", ctypes.c_size_t),
        ("imgdata_right_size", ctypes.c_size_t)
    ]


class Keypoint(ctypes.Structure):
    """Keypoint structure (slamtec_aurora_sdk_keypoint_t)."""
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("flags", ctypes.c_uint8)  # 0: unmatched, non-zero: matched
    ]


class TrackingDataBuffer(ctypes.Structure):
    """Tracking data buffer (slamtec_aurora_sdk_tracking_data_buffer_t)."""
    _fields_ = [
        ("imgdata_left", ctypes.c_void_p),
        ("imgdata_left_size", ctypes.c_size_t),
        ("imgdata_right", ctypes.c_void_p),
        ("imgdata_right_size", ctypes.c_size_t),
        ("keypoints_left", ctypes.POINTER(Keypoint)),
        ("keypoints_left_buffer_count", ctypes.c_size_t),
        ("keypoints_right", ctypes.POINTER(Keypoint)),
        ("keypoints_right_buffer_count", ctypes.c_size_t)
    ]


class TrackingInfo(ctypes.Structure):
    """Tracking info structure (slamtec_aurora_sdk_tracking_info_t)."""
    _fields_ = [
        ("timestamp_ns", ctypes.c_uint64),
        ("left_image_desc", ImageDesc),
        ("right_image_desc", ImageDesc),
        ("is_stereo", ctypes.c_uint32),
        ("tracking_status", ctypes.c_uint32),
        ("pose", PoseSE3),
        ("keypoints_left_count", ctypes.c_uint32),
        ("keypoints_right_count", ctypes.c_uint32)
    ]


class LidarScanPoint(ctypes.Structure):
    """Single LiDAR scan point."""
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("distance", ctypes.c_float),
        ("angle", ctypes.c_float),
        ("quality", ctypes.c_uint8)
    ]


class LidarScanData(ctypes.Structure):
    """LiDAR scan data header."""
    _fields_ = [
        ("timestamp_ns", ctypes.c_uint64),
        ("point_count", ctypes.c_size_t),
        ("angle_min", ctypes.c_float),
        ("angle_max", ctypes.c_float),
        ("angle_increment", ctypes.c_float),
        ("range_min", ctypes.c_float),
        ("range_max", ctypes.c_float)
    ]


class VersionInfo(ctypes.Structure):
    """SDK version info structure."""
    _fields_ = [
        ("sdk_name", ctypes.c_char_p),
        ("sdk_version_string", ctypes.c_char_p),
        ("sdk_build_time", ctypes.c_char_p),
        ("sdk_feature_flags", ctypes.c_uint32)
    ]


# Error codes
ERRORCODE_OK = 0
ERRORCODE_OP_FAILED = -1
ERRORCODE_INVALID_ARGUMENT = -2
ERRORCODE_NOT_SUPPORTED = -3
ERRORCODE_NOT_IMPLEMENTED = -4
ERRORCODE_TIMEOUT = -5
ERRORCODE_IO_ERROR = -6
ERRORCODE_NOT_READY = -7

# Enhanced Image Types (SDK 2.0)
ENHANCED_IMAGE_TYPE_NONE = 0
ENHANCED_IMAGE_TYPE_DEPTH = 1
ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION = 2

# Depth Camera Frame Types (SDK 2.0)
DEPTHCAM_FRAME_TYPE_DEPTH_MAP = 0
DEPTHCAM_FRAME_TYPE_POINT3D = 1

# Feature Bitmap Constants (SDK 2.0)
# Hardware Feature Bits
SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_LIDAR = (1 << 0)
SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_IMU = (1 << 1)
SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_STEREO_CAMERA = (1 << 2)

# Sensing Feature Bits  
SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_VSLAM = (1 << 0)
SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_COMAP = (1 << 1)
SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_STEREO_DENSE_DISPARITY = (1 << 2)
SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_SEMANTIC_SEGMENTATION = (1 << 3)

# Software Feature Bits
SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_CAMERA_PREVIEW_STREAM = (1 << 0)
SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_ENHANCED_IMAGING = (1 << 1)

# Map Storage Session Types
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_UPLOAD = 0
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_DOWNLOAD = 1

# Map Storage Session Status Flags
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FINISHED = 2
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_WORKING = 1
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_IDLE = 0
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FAILED = -1

# Keyframe Flags
SLAMTEC_AURORA_SDK_KEYFRAME_FLAG_NONE = 0
SLAMTEC_AURORA_SDK_KEYFRAME_FLAG_BAD = (1 << 0)  # 0x1
SLAMTEC_AURORA_SDK_KEYFRAME_FLAG_FIXED = (1 << 1)  # 0x2

# Map Data Fetch Flags
SLAMTEC_AURORA_SDK_MAP_FETCH_FLAG_ALL = 0xFFFFFFFF  # Fetch all available data
SLAMTEC_AURORA_SDK_KF_FETCH_FLAG_ALL = 0xFFFFFFFF   # Fetch all keyframe data
SLAMTEC_AURORA_SDK_MP_FETCH_FLAG_ALL = 0xFFFFFFFF   # Fetch all map point data
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_ABORTED = -2
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_REJECTED = -3
SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_TIMEOUT = -4


class MapStorageSessionStatus(ctypes.Structure):
    """Map storage session status structure (slamtec_aurora_sdk_mapstorage_session_status_t)."""
    _fields_ = [
        ("progress", ctypes.c_float),  # 0-100
        ("flags", ctypes.c_int8)       # status flags
    ]
    
    def is_finished(self):
        """Check if session finished successfully."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FINISHED
    
    def is_working(self):
        """Check if session is currently working."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_WORKING
    
    def is_idle(self):
        """Check if session is idle."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_IDLE
    
    def is_failed(self):
        """Check if session failed."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FAILED
    
    def is_aborted(self):
        """Check if session was aborted."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_ABORTED
    
    def is_rejected(self):
        """Check if session was rejected."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_REJECTED
    
    def is_timeout(self):
        """Check if session timed out."""
        return self.flags == SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_TIMEOUT
    
    def get_status_string(self):
        """Get human-readable status string."""
        status_map = {
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FINISHED: "Finished",
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_WORKING: "Working",
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_IDLE: "Idle",
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FAILED: "Failed",
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_ABORTED: "Aborted",
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_REJECTED: "Rejected",
            SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_TIMEOUT: "Timeout"
        }
        return status_map.get(self.flags, f"Unknown({self.flags})")


# Callback function type for C API map storage operations
MapStorageSessionResultCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int)


class IMUData(ctypes.Structure):
    """IMU data structure (slamtec_aurora_sdk_imu_data_t)."""
    _fields_ = [
        ("timestamp_ns", ctypes.c_uint64),  # Timestamp in nanoseconds
        ("imu_id", ctypes.c_uint32),        # IMU sensor ID
        ("acc", ctypes.c_double * 3),       # Acceleration in g units [x, y, z]
        ("gyro", ctypes.c_double * 3)       # Gyroscope in dps [x, y, z]
    ]
    
    def get_timestamp_seconds(self):
        """Get timestamp in seconds (floating point)."""
        return self.timestamp_ns / 1_000_000_000.0
    
    def get_acceleration(self):
        """Get acceleration as a tuple (x, y, z) in g units."""
        return (self.acc[0], self.acc[1], self.acc[2])
    
    def get_gyroscope(self):
        """Get gyroscope data as a tuple (x, y, z) in degrees per second."""
        return (self.gyro[0], self.gyro[1], self.gyro[2])
    
    def to_dict(self):
        """Convert IMU data to dictionary."""
        return {
            'timestamp_ns': self.timestamp_ns,
            'timestamp_s': self.get_timestamp_seconds(),
            'imu_id': self.imu_id,
            'acceleration': self.get_acceleration(),
            'gyroscope': self.get_gyroscope()
        }
    
    def __str__(self):
        """String representation of IMU data."""
        return (f"IMU(id={self.imu_id}, t={self.get_timestamp_seconds():.3f}s, "
                f"acc={self.get_acceleration()}, gyro={self.get_gyroscope()})")
    
    def to_numpy(self):
        """Convert IMU data to numpy arrays (if available)."""
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for to_numpy() method")
        import numpy as np
        return {
            'timestamp_ns': self.timestamp_ns,
            'imu_id': self.imu_id,
            'acceleration': np.array(self.get_acceleration()),
            'gyroscope': np.array(self.get_gyroscope())
        }


# Python wrapper classes for easier use
class DeviceBasicInfoWrapper:
    """
    Python wrapper for device basic information matching C++ RemoteDeviceBasicInfo.
    
    This class wraps slamtec_aurora_sdk_device_basic_info_t and provides
    capability checking methods matching the C++ SDK interface.
    """
    
    def __init__(self, c_struct, timestamp_ns=0):
        """Initialize from C structure."""
        self._c_struct = c_struct
        self._timestamp_ns = timestamp_ns
        
        # Extract basic info
        self._device_name = c_struct.device_name.decode('utf-8').rstrip('\0')
        self._firmware_version = c_struct.firmware_version_string.decode('utf-8').rstrip('\0')
        self._firmware_build_date = c_struct.firmware_build_date.decode('utf-8').rstrip('\0')
        self._firmware_build_time = c_struct.firmware_build_time.decode('utf-8').rstrip('\0')
        
        # Generate device model string using C++ logic
        if c_struct.model_major == 0 and c_struct.model_sub == 0:
            self._device_model_string = "A1M1"
        else:
            self._device_model_string = "A{}M{}".format(c_struct.model_major, c_struct.model_sub)
        
        if c_struct.model_revision:
            self._device_model_string += "-r{}".format(c_struct.model_revision)
        
        # Generate hardware version from model numbers
        self._hardware_version = "{}.{}.{}".format(c_struct.model_major, c_struct.model_sub, c_struct.model_revision)
        
        # Convert serial number from uint8 array to hex string
        serial_bytes = bytes(c_struct.device_sn)
        self._serial_number = ''.join('{:02X}'.format(b) for b in serial_bytes).rstrip('00')
    
    @classmethod
    def from_c_struct(cls, c_struct, timestamp_ns=0):
        """Create DeviceBasicInfo from C structure."""
        return cls(c_struct, timestamp_ns)
    
    # Property accessors matching C++ interface
    @property
    def device_name(self):
        """Get device name."""
        return self._device_name
    
    @property
    def device_model_string(self):
        """Get device model string (e.g., 'A1M1', 'A2M1-r1')."""
        return self._device_model_string
    
    @property
    def firmware_version(self):
        """Get firmware version string."""
        return self._firmware_version
    
    @property
    def firmware_build_date(self):
        """Get firmware build date."""
        return self._firmware_build_date
    
    @property
    def firmware_build_time(self):
        """Get firmware build time."""
        return self._firmware_build_time
    
    @property
    def hardware_version(self):
        """Get hardware version string."""
        return self._hardware_version
    
    @property
    def serial_number(self):
        """Get device serial number."""
        return self._serial_number
    
    @property
    def model_major(self):
        """Get model major version."""
        return self._c_struct.model_major
    
    @property
    def model_sub(self):
        """Get model sub version."""
        return self._c_struct.model_sub
    
    @property
    def model_revision(self):
        """Get model revision."""
        return self._c_struct.model_revision
    
    @property
    def device_uptime_us(self):
        """Get device uptime in microseconds."""
        return self._c_struct.device_uptime_us
    
    @property
    def timestamp_ns(self):
        """Get timestamp when this info was retrieved."""
        return self._timestamp_ns
    
    # Feature bitmap accessors
    @property
    def hwfeature_bitmaps(self):
        """Get hardware feature bitmaps."""
        return self._c_struct.hwfeature_bitmaps
    
    @property
    def sensing_feature_bitmaps(self):
        """Get sensing feature bitmaps."""
        return self._c_struct.sensing_feature_bitmaps
    
    @property
    def swfeature_bitmaps(self):
        """Get software feature bitmaps."""
        return self._c_struct.swfeature_bitmaps
    
    # Capability checking methods matching C++ RemoteDeviceBasicInfo
    def isSupportDepthCamera(self):
        """
        Check if depth camera is supported.
        
        Returns:
            bool: True if depth camera is supported, False otherwise
        """
        return bool(self.sensing_feature_bitmaps & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_STEREO_DENSE_DISPARITY)
    
    def isSupportSemanticSegmentation(self):
        """
        Check if semantic segmentation is supported.
        
        Returns:
            bool: True if semantic segmentation is supported, False otherwise
        """
        return bool(self.sensing_feature_bitmaps & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_SEMANTIC_SEGMENTATION)
    
    def isSupportCameraPreviewStream(self):
        """
        Check if camera preview stream is supported.
        
        Returns:
            bool: True if camera preview stream is supported, False otherwise
        """
        return bool(self.swfeature_bitmaps & SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_CAMERA_PREVIEW_STREAM)
    
    def isSupportVSLAM(self):
        """
        Check if VSLAM is supported.
        
        Returns:
            bool: True if VSLAM is supported, False otherwise
        """
        return bool(self.sensing_feature_bitmaps & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_VSLAM)
    
    def isSupportCoMap(self):
        """
        Check if CoMap (2D LIDAR mapping) is supported.
        
        Returns:
            bool: True if CoMap is supported, False otherwise
        """
        return bool(self.sensing_feature_bitmaps & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_COMAP)
    
    def isSupportLiDAR(self):
        """
        Check if LiDAR is supported.
        
        Returns:
            bool: True if LiDAR is supported, False otherwise
        """
        return bool(self.hwfeature_bitmaps & SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_LIDAR)
    
    def isSupportIMU(self):
        """
        Check if IMU is supported.
        
        Returns:
            bool: True if IMU is supported, False otherwise
        """
        return bool(self.hwfeature_bitmaps & SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_IMU)
    
    def isSupportStereoCamera(self):
        """
        Check if stereo camera is supported.
        
        Returns:
            bool: True if stereo camera is supported, False otherwise
        """
        return bool(self.hwfeature_bitmaps & SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_STEREO_CAMERA)
    
    def isSupportEnhancedImaging(self):
        """
        Check if enhanced imaging is supported.
        
        Returns:
            bool: True if enhanced imaging is supported, False otherwise
        """
        return bool(self.swfeature_bitmaps & SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_ENHANCED_IMAGING)


# Legacy DeviceInfo class for backward compatibility
class DeviceInfo:
    """Legacy device info wrapper for backward compatibility."""
    
    def __init__(self, device_name="", device_model_string="", 
                 firmware_version="", hardware_version="",
                 serial_number="", model_major=0, model_sub=0, model_revision=0):
        self.device_name = device_name
        self.device_model_string = device_model_string
        self.firmware_version = firmware_version
        self.hardware_version = hardware_version
        self.serial_number = serial_number
        self.model_major = model_major
        self.model_sub = model_sub
        self.model_revision = model_revision
    
    @classmethod
    def from_device_basic_info(cls, device_basic_info):
        """Create legacy DeviceInfo from DeviceBasicInfo."""
        return cls(
            device_name=device_basic_info.device_name,
            device_model_string=device_basic_info.device_model_string,
            firmware_version=device_basic_info.firmware_version,
            hardware_version=device_basic_info.hardware_version,
            serial_number=device_basic_info.serial_number,
            model_major=device_basic_info.model_major,
            model_sub=device_basic_info.model_sub,
            model_revision=device_basic_info.model_revision
        )
    
    @classmethod
    def from_c_struct(cls, c_struct, timestamp_ns=0):
        """Create DeviceInfo from C structure (DeviceBasicInfo)."""
        # First create a DeviceBasicInfoWrapper from the C struct
        wrapper = DeviceBasicInfoWrapper.from_c_struct(c_struct, timestamp_ns)
        # Then create a DeviceInfo from the wrapper
        return cls.from_device_basic_info(wrapper)


# New data types for missing API functions - ADDED
class DeviceStatus(ctypes.Structure):
    """Device status information structure."""
    _fields_ = [
        ("device_state", ctypes.c_uint32),
        ("battery_level", ctypes.c_float),
        ("temperature", ctypes.c_float),
        ("cpu_usage", ctypes.c_float),
        ("memory_usage", ctypes.c_float),
        ("tracking_quality", ctypes.c_uint32),
        ("error_flags", ctypes.c_uint32),
        ("reserved", ctypes.c_uint8 * 32)
    ]


class RelocalizationStatus(ctypes.Structure):
    """Relocalization status information structure."""
    _fields_ = [
        ("is_relocalization_active", ctypes.c_int),
        ("relocalization_progress", ctypes.c_float),
        ("confidence_score", ctypes.c_float),
        ("match_count", ctypes.c_uint32),
        ("time_elapsed_ms", ctypes.c_uint64),
        ("reserved", ctypes.c_uint8 * 16)
    ]


class ImageFrame:
    """Python wrapper for image frame data.
    
    This class handles various image formats including regular images (grayscale, RGB, RGBA)
    and depth data (float32 depth maps).
    """
    
    # Additional format constants for depth data
    FORMAT_DEPTH_FLOAT32 = 100  # Float32 depth data
    FORMAT_POINT3D_FLOAT32 = 101  # Float32 point3d data (x,y,z triplets)
    
    def __init__(self, width, height, pixel_format,
                 timestamp_ns, data = None, depth_scale=1.0, 
                 min_depth=0.0, max_depth=10.0):
        self.width = width
        self.height = height
        self.pixel_format = pixel_format
        self.timestamp_ns = timestamp_ns
        self.data = data
        # Additional fields for depth data
        self.depth_scale = depth_scale
        self.min_depth = min_depth
        self.max_depth = max_depth
    
    @classmethod
    def from_c_desc(cls, desc, data = None):
        return cls(
            width=desc.width,
            height=desc.height,
            pixel_format=desc.format,  # Use the format field from C structure
            timestamp_ns=0,  # Timestamp is in the parent stereo pair structure
            data=data
        )
    
    @classmethod
    def from_depth_camera_struct(cls, frame_desc, frame_data):
        """Create ImageFrame from depth camera C structures."""
        return cls(
            width=frame_desc.image_desc.width,
            height=frame_desc.image_desc.height,
            pixel_format=cls.FORMAT_DEPTH_FLOAT32,  # Mark as depth data
            timestamp_ns=frame_desc.timestamp_ns,
            data=frame_data,
            depth_scale=1.0,  # Default scale
            min_depth=0.0,    # Will be calculated from data
            max_depth=10.0    # Will be calculated from data
        )
    
    @classmethod
    def from_point3d_struct(cls, frame_desc, frame_data):
        """Create ImageFrame from point3d C structures."""
        return cls(
            width=frame_desc.image_desc.width,
            height=frame_desc.image_desc.height,
            pixel_format=cls.FORMAT_POINT3D_FLOAT32,  # Mark as point3d data
            timestamp_ns=frame_desc.timestamp_ns,
            data=frame_data
        )
    
    def to_opencv_image(self):
        """
        Convert image data to OpenCV-compatible numpy array.
        
        Returns:
            numpy.ndarray: BGR image array ready for OpenCV, or None if no data
            
        Note:
            Requires opencv-python and numpy to be installed.
        """
        if not self.data or len(self.data) == 0:
            return None
            
        try:
            import numpy as np
            import cv2
        except ImportError as e:
            raise ImportError("OpenCV and NumPy are required for image conversion: {}".format(e))
        
        # Convert image data to numpy array based on format
        if self.pixel_format == 0:  # Grayscale
            img_array = np.frombuffer(self.data, dtype=np.uint8)
            if len(img_array) >= self.width * self.height:
                img = img_array[:self.width * self.height].reshape((self.height, self.width))
                # Convert grayscale to BGR for OpenCV
                return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                
        elif self.pixel_format == 1:  # RGB
            img_array = np.frombuffer(self.data, dtype=np.uint8)
            if len(img_array) >= self.width * self.height * 3:
                img = img_array[:self.width * self.height * 3].reshape((self.height, self.width, 3))
                # Convert RGB to BGR for OpenCV
                return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
        elif self.pixel_format == 2:  # RGBA
            img_array = np.frombuffer(self.data, dtype=np.uint8)
            if len(img_array) >= self.width * self.height * 4:
                img = img_array[:self.width * self.height * 4].reshape((self.height, self.width, 4))
                # Convert RGBA to BGR for OpenCV
                return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        
        # If we get here, format is unsupported or data is insufficient
        return None
    
    def has_image_data(self):
        """Check if this frame contains actual image data."""
        return self.data is not None and len(self.data) > 0
    
    def is_depth_frame(self):
        """Check if this frame contains depth data."""
        return self.pixel_format == self.FORMAT_DEPTH_FLOAT32
    
    def is_point3d_frame(self):
        """Check if this frame contains point3d data."""
        return self.pixel_format == self.FORMAT_POINT3D_FLOAT32
    
    def to_numpy_depth_map(self):
        """Convert depth data to numpy array.
        
        Returns:
            numpy.ndarray: 2D array of float32 depth values, or None if not depth data
        """
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for depth map conversion")
        
        if not self.is_depth_frame() or not self.data:
            return None
            
        import numpy as np
        # Convert bytes to float32 array
        depth_array = np.frombuffer(self.data, dtype=np.float32)
        if len(depth_array) >= self.width * self.height:
            return depth_array[:self.width * self.height].reshape((self.height, self.width))
        return None
    
    def to_colorized_depth_map(self, colormap=None):
        """
        Convert depth map to colorized visualization.
        
        Args:
            colormap: OpenCV colormap (default: cv2.COLORMAP_JET)
            
        Returns:
            numpy.ndarray: Colorized depth map as BGR image
        """
        try:
            import numpy as np
            import cv2
        except ImportError as e:
            raise ImportError("OpenCV and NumPy are required for depth colorization: {}".format(e))
        
        depth_map = self.to_numpy_depth_map()
        if depth_map is None:
            return None
        
        if colormap is None:
            colormap = cv2.COLORMAP_JET
        
        # Normalize depth values to 0-255 range
        normalized_depth = np.zeros_like(depth_map, dtype=np.uint8)
        valid_mask = (depth_map > 0) & (depth_map < float('inf'))
        
        if np.any(valid_mask):
            valid_depths = depth_map[valid_mask]
            min_depth = np.min(valid_depths)
            max_depth = np.max(valid_depths)
            
            if max_depth > min_depth:
                # Normalize valid depths to 0-255
                normalized_valid = ((valid_depths - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)
                normalized_depth[valid_mask] = normalized_valid
        
        # Apply colormap
        return cv2.applyColorMap(normalized_depth, colormap)
    
    def to_point3d_array(self):
        """Convert point3d data to numpy array of 3D points.
        
        Returns:
            numpy.ndarray: Nx3 array of (x, y, z) points, or None if not point3d data
        """
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for point3d conversion")
        
        if not self.is_point3d_frame() or not self.data:
            return None
            
        import numpy as np
        # Convert bytes to float32 array
        float_array = np.frombuffer(self.data, dtype=np.float32)
        
        # Calculate expected number of points
        expected_floats = self.width * self.height * 3
        if len(float_array) >= expected_floats:
            # Reshape to Nx3 array of points
            points = float_array[:expected_floats].reshape((self.width * self.height, 3))
            return points
        return None
    
    def to_point_cloud_data(self):
        """Convert point3d data to point cloud format.
        
        Returns:
            tuple: (points_xyz, valid_mask) where points_xyz is shaped (height, width, 3)
                   and valid_mask indicates which points are valid (non-zero)
        """
        if not self.is_point3d_frame():
            return None, None
            
        points_flat = self.to_point3d_array()
        if points_flat is None:
            return None, None
            
        import numpy as np
        # Reshape to height x width x 3
        points_xyz = points_flat.reshape((self.height, self.width, 3))
        
        # Create mask for valid points (non-zero points)
        valid_mask = np.any(points_xyz != 0, axis=2)
        
        return points_xyz, valid_mask


class TrackingFrame:
    """Python wrapper for tracking frame data."""
    
    def __init__(self, left_image = None, right_image = None, 
                 left_keypoints = None, right_keypoints = None,
                 pose = None, timestamp_ns = 0, tracking_status = 0):
        self.left_image = left_image
        self.right_image = right_image
        self.left_keypoints = left_keypoints or []
        self.right_keypoints = right_keypoints or []
        self.pose = pose
        self.timestamp_ns = timestamp_ns
        self.tracking_status = tracking_status
    
    @classmethod
    def from_c_struct(cls, tracking_info, left_keypoints=None, right_keypoints=None, 
                      left_image_data=None, right_image_data=None):
        """Create TrackingFrame from C structures."""
        # Create image frames
        left_image = None
        right_image = None
        
        if tracking_info.left_image_desc.width > 0:
            left_image = ImageFrame.from_c_desc(tracking_info.left_image_desc, data=left_image_data)
            left_image.timestamp_ns = tracking_info.timestamp_ns
            
        if tracking_info.right_image_desc.width > 0:
            right_image = ImageFrame.from_c_desc(tracking_info.right_image_desc, data=right_image_data)
            right_image.timestamp_ns = tracking_info.timestamp_ns
        
        # Convert pose - handle case where pose might be invalid
        try:
            pose_position = tracking_info.pose.translation.to_tuple()
            pose_rotation = tracking_info.pose.quaternion.to_tuple()
        except AttributeError:
            # Fallback to default pose if conversion fails
            pose_position = (0.0, 0.0, 0.0)
            pose_rotation = (0.0, 0.0, 0.0, 1.0)
        
        
        return cls(
            left_image=left_image,
            right_image=right_image,
            left_keypoints=left_keypoints or [],
            right_keypoints=right_keypoints or [],
            pose=(pose_position, pose_rotation),
            timestamp_ns=tracking_info.timestamp_ns,
            tracking_status=tracking_info.tracking_status
        )
    
    def draw_keypoints_on_image(self, opencv_image, image_side='left', color=(0, 255, 0), radius=3):
        """
        Draw keypoints on a provided OpenCV image.
        
        Args:
            opencv_image (numpy.ndarray): OpenCV image to draw keypoints on
            image_side (str): 'left' or 'right' to specify which keypoints to use
            color (tuple): BGR color for keypoints (default: green)
            radius (int): Radius of keypoint circles
            
        Returns:
            numpy.ndarray: Image with keypoints drawn (modifies input image)
            
        Note:
            Requires opencv-python to be installed.
        """
        if opencv_image is None:
            return None
            
        # Select keypoints based on side
        if image_side == 'left':
            keypoints = self.left_keypoints
        elif image_side == 'right':
            keypoints = self.right_keypoints
        else:
            raise ValueError("image_side must be 'left' or 'right'")
        
        # Check if we have keypoints
        if not keypoints:
            return opencv_image
            
        try:
            import cv2
        except ImportError as e:
            raise ImportError("OpenCV is required for keypoint drawing: {}".format(e))
        
        # Get image dimensions
        height, width = opencv_image.shape[:2]
        
        # Draw keypoints
        for keypoint in keypoints:
            x, y = int(keypoint.x), int(keypoint.y)
            # Only draw if keypoint is within image bounds
            if 0 <= x < width and 0 <= y < height:
                cv2.circle(opencv_image, (x, y), radius, color, -1)
        
        return opencv_image
    
    def draw_keypoints(self, image_side='left', color=(0, 255, 0), radius=3):
        """
        Draw keypoints on the tracking frame's own image and return the result.
        
        Args:
            image_side (str): 'left' or 'right' to specify which image to use
            color (tuple): BGR color for keypoints (default: green)
            radius (int): Radius of keypoint circles
            
        Returns:
            numpy.ndarray: Image with keypoints drawn, or None if no image/keypoints
            
        Note:
            Requires opencv-python and numpy to be installed.
            This method only works if the tracking frame has image data.
        """
        # Select image and keypoints based on side
        if image_side == 'left':
            image = self.left_image
            keypoints = self.left_keypoints
        elif image_side == 'right':
            image = self.right_image
            keypoints = self.right_keypoints
        else:
            raise ValueError("image_side must be 'left' or 'right'")
        
        # Check if we have image and keypoints
        if not image or not keypoints:
            return None
            
        # Convert image to OpenCV format
        opencv_image = image.to_opencv_image()
        if opencv_image is None:
            return None
            
        return self.draw_keypoints_on_image(opencv_image, image_side, color, radius)


class ScanData:
    """Python wrapper for LiDAR scan data."""
    
    def __init__(self, timestamp_ns, points = None,
                 ranges = None, angles = None):
        self.timestamp_ns = timestamp_ns
        self.points = points or []
        self.ranges = ranges
        self.angles = angles
    
    @classmethod
    def from_c_data(cls, header, points):
        scan_points = [(point.x, point.y) for point in points]
        if NUMPY_AVAILABLE:
            ranges = np.array([point.distance for point in points])
            angles = np.array([point.angle for point in points])
        else:
            ranges = [point.distance for point in points]
            angles = [point.angle for point in points]
        
        return cls(
            timestamp_ns=header.timestamp_ns,
            points=scan_points,
            ranges=ranges,
            angles=angles
        )


class LidarScanData:
    """Python wrapper for 2D LiDAR scan data."""
    
    def __init__(self, timestamp_ns=0, layer_id=0, binded_kf_id=0, 
                 dyaw=0.0, points=None):
        self.timestamp_ns = timestamp_ns
        self.layer_id = layer_id
        self.binded_kf_id = binded_kf_id
        self.dyaw = dyaw
        self.points = points or []  # List of (dist, angle, quality) tuples
    
    @classmethod
    def from_c_data(cls, scan_info, scan_points):
        """Create LidarScanData from C structures."""
        points = []
        for i in range(scan_info.scan_count):
            point = scan_points[i]
            points.append((float(point.dist), float(point.angle), int(point.quality)))
        
        return cls(
            timestamp_ns=scan_info.timestamp_ns,
            layer_id=scan_info.layer_id,
            binded_kf_id=scan_info.binded_kf_id,
            dyaw=scan_info.dyaw,
            points=points
        )
    
    def to_cartesian(self):
        """Convert polar coordinates to cartesian (x, y) points."""
        if not NUMPY_AVAILABLE:
            cartesian_points = []
            for dist, angle, quality in self.points:
                if quality > 0:  # Valid point
                    x = dist * math.cos(angle)
                    y = dist * math.sin(angle)
                    cartesian_points.append((x, y, quality))
            return cartesian_points
        else:
            # Use numpy for faster computation
            import math
            valid_points = [(dist, angle, quality) for dist, angle, quality in self.points if quality > 0]
            if not valid_points:
                return []
            
            dists, angles, qualities = zip(*valid_points)
            dists = np.array(dists)
            angles = np.array(angles)
            qualities = np.array(qualities)
            
            x = dists * np.cos(angles)
            y = dists * np.sin(angles)
            
            return list(zip(x, y, qualities))
    
    def get_scan_count(self):
        """Get the number of scan points."""
        return len(self.points)
    
    def get_valid_points(self):
        """Get only valid scan points (quality > 0)."""
        return [(dist, angle, quality) for dist, angle, quality in self.points if quality > 0]


class GridMap2D:
    """Python wrapper for 2D grid map data."""
    
    def __init__(self, width=0, height=0, resolution=0.05, origin_x=0.0, origin_y=0.0, data=None):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.data = data or []  # Grid data as uint8 array
    
    def get_cell_value(self, x, y):
        """Get the value of a cell at grid coordinates (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y * self.width + x]
        return 0
    
    def world_to_grid(self, world_x, world_y):
        """Convert world coordinates to grid coordinates."""
        grid_x = int((world_x - self.origin_x) / self.resolution)
        grid_y = int((world_y - self.origin_y) / self.resolution)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x, grid_y):
        """Convert grid coordinates to world coordinates."""
        world_x = grid_x * self.resolution + self.origin_x
        world_y = grid_y * self.resolution + self.origin_y
        return world_x, world_y
    
    def to_numpy(self):
        """Convert grid data to numpy array (requires numpy)."""
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for to_numpy() method")
        return np.array(self.data, dtype=np.uint8).reshape((self.height, self.width))


class GridMapGenerationOptions(ctypes.Structure):
    """2D gridmap generation options structure (slamtec_aurora_sdk_2d_gridmap_generation_options_t)."""
    _fields_ = [
        ("resolution", ctypes.c_float),
        ("width", ctypes.c_float),
        ("height", ctypes.c_float),
        ("origin_x", ctypes.c_float),
        ("origin_y", ctypes.c_float),
        ("height_range_specified", ctypes.c_int),
        ("min_height", ctypes.c_float),
        ("max_height", ctypes.c_float)
    ]


class GlobalMapDesc(ctypes.Structure):
    """Global map description structure (slamtec_aurora_sdk_global_map_desc_t)."""
    _fields_ = [
        ("lastMPCountToFetch", ctypes.c_uint64),
        ("lastKFCountToFetch", ctypes.c_uint64),
        ("lastMapCountToFetch", ctypes.c_uint64),
        ("lastMPRetrieved", ctypes.c_uint64),
        ("lastKFRetrieved", ctypes.c_uint64),
        ("totalMPCount", ctypes.c_uint64),
        ("totalKFCount", ctypes.c_uint64),
        ("totalMapCount", ctypes.c_uint64),
        ("totalMPCountFetched", ctypes.c_uint64),
        ("totalKFCountFetched", ctypes.c_uint64),
        ("totalMapCountFetched", ctypes.c_uint64),
        ("currentActiveMPCount", ctypes.c_uint64),
        ("currentActiveKFCount", ctypes.c_uint64),
        ("activeMapID", ctypes.c_uint32),
        ("mappingFlags", ctypes.c_uint32),  # slamtec_aurora_sdk_mapping_flag_t
        ("slidingWindowStartKFId", ctypes.c_uint64)
    ]


class MapPointDesc(ctypes.Structure):
    """Map point description structure (slamtec_aurora_sdk_map_point_desc_t)."""
    _fields_ = [
        ("id", ctypes.c_uint64),
        ("map_id", ctypes.c_uint32),
        ("_padding1", ctypes.c_uint32),  # Padding to align timestamp on 8-byte boundary
        ("timestamp", ctypes.c_double),
        ("position", Vector3),
        ("flags", ctypes.c_uint32),
        ("_padding2", ctypes.c_uint32)   # Padding to align structure size
    ]


class KeyframeDesc(ctypes.Structure):
    """Keyframe description structure (slamtec_aurora_sdk_keyframe_desc_t)."""
    _fields_ = [
        ("id", ctypes.c_uint64),
        ("parent_id", ctypes.c_uint64),
        ("map_id", ctypes.c_uint32),
        ("_padding1", ctypes.c_uint32),  # Padding to align timestamp on 8-byte boundary
        ("timestamp", ctypes.c_double),
        ("pose_se3", PoseSE3),
        ("pose", Pose),
        ("looped_frame_count", ctypes.c_size_t),
        ("connected_frame_count", ctypes.c_size_t),
        ("flags", ctypes.c_uint32),
        ("_padding2", ctypes.c_uint32)   # Padding to align structure size
    ]


class MapDesc(ctypes.Structure):
    """Map description structure (slamtec_aurora_sdk_map_desc_t)."""
    _fields_ = [
        ("map_id", ctypes.c_uint32),               # Map ID
        ("map_flags", ctypes.c_uint32),            # Map flags
        ("keyframe_count", ctypes.c_uint64),       # Number of keyframes in the map
        ("map_point_count", ctypes.c_uint64),      # Number of map points in the map
        ("keyframe_id_start", ctypes.c_uint64),    # First keyframe ID
        ("keyframe_id_end", ctypes.c_uint64),      # Last keyframe ID
        ("map_point_id_start", ctypes.c_uint64),   # First map point ID
        ("map_point_id_end", ctypes.c_uint64)      # Last map point ID
    ]


# Callback function types for map data visitor
MapPointCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(MapPointDesc))
KeyframeCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(KeyframeDesc), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64))
MapDescCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(MapDesc))

# Callback function type for map storage session result
MapStorageSessionResultCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int)


class MapDataVisitor(ctypes.Structure):
    """Map data visitor structure (slamtec_aurora_sdk_map_data_visitor_t)."""
    _fields_ = [
        ("user_data", ctypes.c_void_p),
        ("on_keyframe", KeyframeCallback),
        ("on_map_point", MapPointCallback),
        ("on_map_desc", MapDescCallback)
    ]


# 2D Grid Map related structures
class GridMap2DDimension(ctypes.Structure):
    """2D gridmap dimension structure (slamtec_aurora_sdk_2dmap_dimension_t)."""
    _fields_ = [
        ("min_x", ctypes.c_float),    # minimum x coordinate in meters
        ("min_y", ctypes.c_float),    # minimum y coordinate in meters
        ("max_x", ctypes.c_float),    # maximum x coordinate in meters
        ("max_y", ctypes.c_float)     # maximum y coordinate in meters
    ]


class Rect(ctypes.Structure):
    """Rectangle structure (slamtec_aurora_sdk_rect_t)."""
    _fields_ = [
        ("x", ctypes.c_float),        # x coordinate
        ("y", ctypes.c_float),        # y coordinate
        ("width", ctypes.c_float),    # width
        ("height", ctypes.c_float)    # height
    ]


class GridMapGenerationOptions(ctypes.Structure):
    """2D gridmap generation options (slamtec_aurora_sdk_2d_gridmap_generation_options_t)."""
    _fields_ = [
        ("resolution", ctypes.c_float),           # resolution of the gridmap
        ("map_canvas_width", ctypes.c_float),     # width of the gridmap canvas
        ("map_canvas_height", ctypes.c_float),    # height of the gridmap canvas
        ("active_map_only", ctypes.c_int),        # whether to generate active map only
        ("height_range_specified", ctypes.c_int), # whether height range is specified
        ("min_height", ctypes.c_float),           # minimum height (valid when height_range_specified is true)
        ("max_height", ctypes.c_float)            # maximum height (valid when height_range_specified is true)
    ]


class GridMap2DFetchInfo(ctypes.Structure):
    """2D gridmap fetch info (slamtec_aurora_sdk_2d_gridmap_fetch_info_t)."""
    _fields_ = [
        ("real_x", ctypes.c_float),       # x coordinate of retrieved gridmap in meters
        ("real_y", ctypes.c_float),       # y coordinate of retrieved gridmap in meters
        ("cell_width", ctypes.c_int),     # width of retrieved gridmap cell
        ("cell_height", ctypes.c_int)     # height of retrieved gridmap cell
    ]


class FloorDetectionDesc(ctypes.Structure):
    """Floor detection description (slamtec_aurora_sdk_floor_detection_desc_t)."""
    _fields_ = [
        ("floorID", ctypes.c_int),            # floor ID
        ("typical_height", ctypes.c_float),   # typical height of the floor
        ("confidence", ctypes.c_float)        # confidence of detection
    ]


class FloorDetectionHistogramInfo(ctypes.Structure):
    """Floor detection histogram info (slamtec_aurora_sdk_floor_detection_histogram_info_t)."""
    _fields_ = [
        ("bin_width", ctypes.c_float),        # width of histogram bin in meters
        ("bin_height_start", ctypes.c_float), # start height of histogram bin in meters
        ("bin_total_count", ctypes.c_int)     # total count of histogram bins
    ]


# LiDAR scan data structures
class LidarScanPoint(ctypes.Structure):
    """LiDAR scan point structure (slamtec_aurora_sdk_lidar_scan_point_t)."""
    _fields_ = [
        ("dist", ctypes.c_float),     # distance in meters
        ("angle", ctypes.c_float),    # angle in radians (right-hand coordinate system)
        ("quality", ctypes.c_uint8)   # quality (RSSI)
    ]


class LidarSinglelayerScanDataInfo(ctypes.Structure):
    """LiDAR single layer scan data info (slamtec_aurora_sdk_lidar_singlelayer_scandata_info_t)."""
    _fields_ = [
        ("timestamp_ns", ctypes.c_uint64),    # nanoseconds timestamp
        ("layer_id", ctypes.c_int32),         # layer ID
        ("binded_kf_id", ctypes.c_uint64),    # binded Visual keyframe ID
        ("dyaw", ctypes.c_float),             # yaw rotation change during scan
        ("scan_count", ctypes.c_uint32)       # count of scan points
    ]


# 2D Grid Map structures
class GridMap2DDimension(ctypes.Structure):
    """2D grid map dimension structure (slamtec_aurora_sdk_2dmap_dimension_t)."""
    _fields_ = [
        ("min_x", ctypes.c_float),    # minimum x coordinate in meters
        ("min_y", ctypes.c_float),    # minimum y coordinate in meters
        ("max_x", ctypes.c_float),    # maximum x coordinate in meters
        ("max_y", ctypes.c_float)     # maximum y coordinate in meters
    ]


class GridMap2DGenerationOptions(ctypes.Structure):
    """2D grid map generation options (slamtec_aurora_sdk_2d_gridmap_generation_options_t)."""
    _fields_ = [
        ("resolution", ctypes.c_float),                # gridmap resolution
        ("map_canvas_width", ctypes.c_float),          # canvas width
        ("map_canvas_height", ctypes.c_float),         # canvas height
        ("active_map_only", ctypes.c_int),             # generate active map only
        ("height_range_specified", ctypes.c_int),      # height range specified flag
        ("min_height", ctypes.c_float),                # minimum height (when height_range_specified)
        ("max_height", ctypes.c_float)                 # maximum height (when height_range_specified)
    ]


# Callback function types for LiDAR scan
LidarScanCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, 
                                     ctypes.POINTER(LidarSinglelayerScanDataInfo), 
                                     ctypes.POINTER(LidarScanPoint))


# Enhanced Imaging data structures for SDK 2.0 - Matching C++ API exactly
class SingleCameraCalibration(ctypes.Structure):
    """Single camera calibration structure (slamtec_aurora_sdk_single_camera_calibration_t)."""
    _fields_ = [
        ("len_type", ctypes.c_uint32),           # lens type enum (0: PINHOLE, 1: RECTIFIED, 2: KANNALABRANDT)
        ("color_mode", ctypes.c_uint32),         # color mode enum (0: RGB, 1: MONO)
        ("width", ctypes.c_int),                 # image width
        ("height", ctypes.c_int),                # image height
        ("fps", ctypes.c_int),                   # frame rate (integer, not float)
        ("intrinsics", ctypes.c_float * 4),      # [fx, fy, cx, cy]
        ("distortion", ctypes.c_float * 5)       # distortion coefficients [k1, k2, k3, k4, unused] - 5 elements but only 4 used
    ]


class ExtCameraTransform(ctypes.Structure):
    """External camera transform structure (slamtec_aurora_sdk_ext_camera_transform_t)."""
    _fields_ = [
        ("t_c2_c1", ctypes.c_float * 16)         # 4x4 transformation matrix from camera 2 to camera 1
    ]


class CameraCalibrationInfo(ctypes.Structure):
    """Camera calibration info structure (slamtec_aurora_sdk_camera_calibration_t)."""
    _fields_ = [
        ("camera_type", ctypes.c_uint32),                     # camera type enum (0: MONO, 1: STEREO)
        ("camera_calibration", SingleCameraCalibration * 4),  # array of camera calibrations
        ("ext_camera_transform", ExtCameraTransform * 4)      # array of external camera transforms
    ]


class TransformCalibrationInfo(ctypes.Structure):
    """Transform calibration info structure (slamtec_aurora_sdk_transform_calibration_t)."""
    _fields_ = [
        ("t_base_cam", PoseSE3),          # base to camera transform
        ("t_camera_imu", PoseSE3)         # camera to IMU transform
    ]


class SemanticSegmentationConfig(ctypes.Structure):
    """Semantic segmentation configuration structure."""
    _fields_ = [
        ("model_type", ctypes.c_int),                    # 0: default model, 1: alternative model
        ("class_count", ctypes.c_int),                   # number of classes supported
        ("model_name", ctypes.c_char * 64),              # model name string
        ("version", ctypes.c_char * 32),                 # model version
        ("input_width", ctypes.c_int),                   # input image width
        ("input_height", ctypes.c_int),                  # input image height
        ("output_width", ctypes.c_int),                  # output segmentation map width
        ("output_height", ctypes.c_int)                  # output segmentation map height
    ]


class SemanticSegmentationLabelName(ctypes.Structure):
    """Semantic segmentation label name structure."""
    _fields_ = [
        ("name", ctypes.c_char * 64)                     # label name string
    ]

class SemanticSegmentationLabelInfo(ctypes.Structure):
    """Semantic segmentation label information structure."""
    _fields_ = [
        ("label_count", ctypes.c_size_t),                # number of labels
        ("label_names", SemanticSegmentationLabelName * 256)  # array of label name structures
    ]


# Enhanced Imaging Frame Structures (matching C API exactly)
class EnhancedImagingFrameDesc(ctypes.Structure):
    """Enhanced imaging frame descriptor (slamtec_aurora_sdk_enhanced_imaging_frame_desc_t)."""
    _fields_ = [
        ("timestamp_ns", ctypes.c_uint64),
        ("image_desc", ImageDesc)
    ]


class EnhancedImagingFrameBuffer(ctypes.Structure):
    """Enhanced imaging frame buffer (slamtec_aurora_sdk_enhanced_imaging_frame_buffer_t)."""
    _fields_ = [
        ("frame_data", ctypes.c_void_p),
        ("frame_data_size", ctypes.c_size_t)
    ]


# DepthCameraFrame is deprecated - use ImageFrame instead
# The ImageFrame class now supports depth data with is_depth_frame() and to_numpy_depth_map() methods

# Depth Camera Configuration
class DepthcamConfigInfo(ctypes.Structure):
    """Depth camera configuration info (slamtec_aurora_sdk_depthcam_config_info_t)."""
    _fields_ = [
        ("fps", ctypes.c_float),
        ("frame_skip", ctypes.c_int),
        ("image_width", ctypes.c_int),
        ("image_height", ctypes.c_int),
        ("binded_cam_id", ctypes.c_int)
    ]

class IMUInfo(ctypes.Structure):
    """IMU information structure (slamtec_aurora_sdk_imu_info_t)."""
    _fields_ = [
        ("valid", ctypes.c_int),                    # Whether IMU data is valid
        ("tcb", PoseSE3),                          # Transform from base to camera
        ("tc_imu", PoseSE3),                       # Transform from IMU to camera  
        ("cov_noise", ctypes.c_double * 6),        # Covariance of noise (gyro to accel)
        ("cov_random_walk", ctypes.c_double * 6)   # Covariance of random walk (gyro to accel)
    ]




