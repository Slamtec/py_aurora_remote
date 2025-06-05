"""
Low-level C bindings for Aurora SDK using ctypes.
"""

import ctypes
import os
import platform
# typing module not available in Python 2.7
from .data_types import *
from .exceptions import AuroraSDKError


def load_aurora_sdk_library():
    """Load the Aurora SDK dynamic library based on platform."""
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Determine library path based on platform
    if system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            lib_path = "cpp_sdk/aurora_remote_public/lib/linux_aarch64/libslamtec_aurora_remote_sdk.so"
        else:
            lib_path = "cpp_sdk/aurora_remote_public/lib/linux_x86_64/libslamtec_aurora_remote_sdk.so"
    elif system == "windows":
        lib_path = "cpp_sdk/aurora_remote_public/lib/win64/slamtec_aurora_remote_sdk.dll"
    elif system == "darwin":
        if "aarch64" in machine or "arm64" in machine:
            lib_path = "cpp_sdk/aurora_remote_public/lib/macos_arm64/libslamtec_aurora_remote_sdk.dylib"
        else:
            lib_path = "cpp_sdk/aurora_remote_public/lib/macos_x86_64/libslamtec_aurora_remote_sdk.dylib"
    else:
        raise AuroraSDKError("Unsupported platform: {}".format(system))
    
    # Find the library relative to the package installation
    # When installed via pip/setup.py, the library should be in the package data
    package_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for the library
    possible_paths = [
        # Development setup - library in sibling cpp_sdk directory
        os.path.join(os.path.dirname(os.path.dirname(package_dir)), lib_path),
        # Installed package - platform-specific library bundled with package (current platform only build)
        os.path.join(package_dir, "lib", os.path.basename(lib_path)),
        # Installed package - universal library bundled with package (all platforms build)
        os.path.join(package_dir, "lib", lib_path.replace("cpp_sdk/aurora_remote_public/lib/", "")),
        # Alternative package layout
        os.path.join(os.path.dirname(package_dir), lib_path),
        # Windows-specific fallback paths
        os.path.join(package_dir, "lib", "slamtec_aurora_remote_sdk.dll") if system == "windows" else None,
        # Linux-specific fallback paths  
        os.path.join(package_dir, "lib", "libslamtec_aurora_remote_sdk.so") if system == "linux" else None,
        # macOS-specific fallback paths
        os.path.join(package_dir, "lib", "libslamtec_aurora_remote_sdk.dylib") if system == "darwin" else None,
    ]
    
    # Remove None entries
    possible_paths = [p for p in possible_paths if p is not None]
    
    full_lib_path = None
    for path in possible_paths:
        if os.path.exists(path):
            full_lib_path = path
            break
    
    if full_lib_path is None:
        searched_paths = "\n".join("  - {}".format(path) for path in possible_paths)
        raise AuroraSDKError("Aurora SDK library not found. Searched paths:\n{}".format(searched_paths))
    
    try:
        # Aurora SDK DLL uses __cdecl calling convention on all platforms
        # Use CDLL for consistent __cdecl convention across Windows and Linux
        return ctypes.CDLL(full_lib_path)
    except OSError as e:
        raise AuroraSDKError("Failed to load Aurora SDK library: {}".format(e))


class CBindings:
    """Low-level C bindings for Aurora SDK."""
    
    def __init__(self):
        self.lib = load_aurora_sdk_library()
        self._setup_function_signatures()
    
    def _setup_function_signatures(self):
        """Setup function signatures for all C API functions."""
        
        # Session management
        self.lib.slamtec_aurora_sdk_get_version_info.argtypes = [ctypes.POINTER(VersionInfo)]
        self.lib.slamtec_aurora_sdk_get_version_info.restype = ctypes.c_int
        
        from .data_types import Quaternion, EulerAngle
        
        self.lib.slamtec_aurora_sdk_convert_quaternion_to_euler.argtypes = [
            ctypes.POINTER(Quaternion),    # const quaternion*
            ctypes.POINTER(EulerAngle)     # euler_out*
        ]
        self.lib.slamtec_aurora_sdk_convert_quaternion_to_euler.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_create_session.argtypes = [
            ctypes.c_void_p,  # config
            ctypes.c_size_t,  # config_size
            ctypes.c_void_p,  # listener
            ctypes.POINTER(ctypes.c_int)  # error_code
        ]
        self.lib.slamtec_aurora_sdk_create_session.restype = ctypes.c_void_p
        
        self.lib.slamtec_aurora_sdk_release_session.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_release_session.restype = None
        
        # Controller operations
        self.lib.slamtec_aurora_sdk_controller_get_discovered_servers.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ServerConnectionInfo),  # servers
            ctypes.c_size_t  # max_server_count
        ]
        self.lib.slamtec_aurora_sdk_controller_get_discovered_servers.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_connect.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ServerConnectionInfo)  # server_conn_info
        ]
        self.lib.slamtec_aurora_sdk_controller_connect.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_disconnect.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_controller_disconnect.restype = None
        
        self.lib.slamtec_aurora_sdk_controller_is_connected.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_controller_is_connected.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_set_map_data_syncing.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int  # enable
        ]
        self.lib.slamtec_aurora_sdk_controller_set_map_data_syncing.restype = None
        
        self.lib.slamtec_aurora_sdk_controller_set_raw_data_subscription.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int  # enable
        ]
        self.lib.slamtec_aurora_sdk_controller_set_raw_data_subscription.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_resync_map_data.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int  # invalidate_cache
        ]
        self.lib.slamtec_aurora_sdk_controller_resync_map_data.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_require_mapping_mode.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64  # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_controller_require_mapping_mode.restype = ctypes.c_int
        
        # Data provider operations (using new timestamp-enabled functions)
        self.lib.slamtec_aurora_sdk_dataprovider_get_current_pose_se3_with_timestamp.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(PoseSE3),  # pose_out
            ctypes.POINTER(ctypes.c_uint64)  # timestamp_ns_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_current_pose_se3_with_timestamp.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_current_pose_with_timestamp.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(Pose),  # pose_out
            ctypes.POINTER(ctypes.c_uint64)  # timestamp_ns_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_current_pose_with_timestamp.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_last_device_basic_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(DeviceBasicInfo),  # info_out
            ctypes.POINTER(ctypes.c_uint64)  # timestamp_ns_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_last_device_basic_info.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_peek_camera_preview_image.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64,  # timestamp_ns
            ctypes.POINTER(StereoImagePairDesc),  # desc_out
            ctypes.c_void_p,  # provided_buffer_info
            ctypes.c_int  # allow_nearest_frame
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_peek_camera_preview_image.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_peek_recent_lidar_scan_singlelayer.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(LidarSinglelayerScanDataInfo),  # header_out
            ctypes.POINTER(LidarScanPoint),  # scan_points_out
            ctypes.c_size_t,  # buffer_count
            ctypes.POINTER(PoseSE3),  # scanpose
            ctypes.c_int  # forceLatest
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_peek_recent_lidar_scan_singlelayer.restype = ctypes.c_int
        
        # Camera/tracking data operations
        self.lib.slamtec_aurora_sdk_dataprovider_peek_tracking_data.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_void_p,  # tracking_data_out
            ctypes.c_void_p   # provided_buffer_info
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_peek_tracking_data.restype = ctypes.c_int
        
        # Map data access operations
        from .data_types import MapDataVisitor, GlobalMapDesc
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_global_mapping_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(GlobalMapDesc)  # global_desc_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_global_mapping_info.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_access_map_data.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(MapDataVisitor),  # visitor
            ctypes.POINTER(ctypes.c_uint32),  # map_ids
            ctypes.c_size_t  # map_id_count
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_access_map_data.restype = ctypes.c_int
        
        from .data_types import DeviceStatus, RelocalizationStatus
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_last_device_status.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(DeviceStatus),  # status_out
            ctypes.POINTER(ctypes.c_uint64)  # timestamp_ns_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_last_device_status.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_relocalization_status.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(RelocalizationStatus)  # status_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_relocalization_status.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_mapping_flags.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ctypes.c_uint32)  # flags_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_mapping_flags.restype = ctypes.c_int
        
        # CRITICAL MISSING FUNCTIONS that supervisor overlooked
        from .data_types import IMUInfo, IMUData, MapDesc
        
        # slamtec_aurora_sdk_dataprovider_get_imu_info (Line 620 in C API)
        self.lib.slamtec_aurora_sdk_dataprovider_get_imu_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(IMUInfo)  # info_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_imu_info.restype = ctypes.c_int
        
        # slamtec_aurora_sdk_dataprovider_get_all_map_info (Line 645 in C API)
        self.lib.slamtec_aurora_sdk_dataprovider_get_all_map_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(MapDesc),  # desc_buffer
            ctypes.c_size_t,  # buffer_count
            ctypes.POINTER(ctypes.c_size_t)  # actual_count_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_all_map_info.restype = ctypes.c_int
        
        # slamtec_aurora_sdk_dataprovider_peek_history_pose (Line 492 in C API)
        self.lib.slamtec_aurora_sdk_dataprovider_peek_history_pose.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(PoseSE3),  # pose_out
            ctypes.c_uint64,  # timestamp_ns
            ctypes.c_int,     # allow_interpolation
            ctypes.c_uint64   # max_time_diff_ns
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_peek_history_pose.restype = ctypes.c_int
        
        # slamtec_aurora_sdk_dataprovider_peek_imu_data (Line 608 in C API)
        self.lib.slamtec_aurora_sdk_dataprovider_peek_imu_data.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(IMUData),  # imu_data_out
            ctypes.c_size_t,  # buffer_count
            ctypes.POINTER(ctypes.c_size_t)  # actual_count_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_peek_imu_data.restype = ctypes.c_int
        
        # 2D Grid Map operations
        from .data_types import GridMapGenerationOptions, GridMap2DDimension, Rect, GridMap2DFetchInfo
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_start_background_update.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(GridMapGenerationOptions)  # build_options
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_start_background_update.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_stop_background_update.argtypes = [
            ctypes.c_void_p  # handle
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_stop_background_update.restype = None
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_is_background_updating.argtypes = [
            ctypes.c_void_p  # handle
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_is_background_updating.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_require_redraw.argtypes = [
            ctypes.c_void_p  # handle
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_require_redraw.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_and_reset_update_dirty_rect.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(Rect),  # dirty_rect_out
            ctypes.POINTER(ctypes.c_int)  # map_big_change
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_and_reset_update_dirty_rect.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_set_auto_floor_detection.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int  # enable
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_set_auto_floor_detection.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_is_auto_floor_detection.argtypes = [
            ctypes.c_void_p  # handle
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_is_auto_floor_detection.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_gridmap_handle.argtypes = [
            ctypes.c_void_p  # handle
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_gridmap_handle.restype = ctypes.c_void_p
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_get_dimension.argtypes = [
            ctypes.c_void_p,  # gridmap_handle
            ctypes.POINTER(GridMap2DDimension),  # dimension_out
            ctypes.c_int  # get_max_capacity
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_get_dimension.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_read_cell_data.argtypes = [
            ctypes.c_void_p,  # gridmap_handle
            ctypes.POINTER(Rect),  # fetch_rect
            ctypes.POINTER(GridMap2DFetchInfo),  # info_out
            ctypes.POINTER(ctypes.c_uint8),  # cell_buffer
            ctypes.c_size_t,  # cell_buffer_size
            ctypes.c_int  # l2p_mapping
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_read_cell_data.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_release.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_release.restype = None
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_get_resolution.argtypes = [
            ctypes.c_void_p,  # gridmap_handle
            ctypes.POINTER(ctypes.c_float)  # resolution_out
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_get_resolution.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_get_supported_grid_resultion_range.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ctypes.c_float),  # min_resolution_out
            ctypes.POINTER(ctypes.c_float)   # max_resolution_out
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_get_supported_grid_resultion_range.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_lidar2dmap_get_supported_max_grid_cell_count.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ctypes.c_size_t)  # max_cell_count_out
        ]
        self.lib.slamtec_aurora_sdk_lidar2dmap_get_supported_max_grid_cell_count.restype = ctypes.c_int
        
        # Auto floor detection operations
        from .data_types import FloorDetectionDesc, FloorDetectionHistogramInfo
        
        self.lib.slamtec_aurora_sdk_autofloordetection_get_detection_histogram.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(FloorDetectionHistogramInfo),  # header_out
            ctypes.POINTER(ctypes.c_float),  # histogram_buffer
            ctypes.c_size_t   # buffer_count
        ]
        self.lib.slamtec_aurora_sdk_autofloordetection_get_detection_histogram.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_autofloordetection_get_all_detection_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(FloorDetectionDesc),  # desc_buffer
            ctypes.c_size_t,  # buffer_count
            ctypes.POINTER(ctypes.c_size_t),  # actual_count_out
            ctypes.POINTER(ctypes.c_int)  # current_floor_id
        ]
        self.lib.slamtec_aurora_sdk_autofloordetection_get_all_detection_info.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_autofloordetection_get_current_detection_desc.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(FloorDetectionDesc)  # desc_out
        ]
        self.lib.slamtec_aurora_sdk_autofloordetection_get_current_detection_desc.restype = ctypes.c_int
        
        # Enhanced Imaging API operations (SDK 2.0)
        from .data_types import (CameraCalibrationInfo, TransformCalibrationInfo, 
                                SemanticSegmentationConfig, SemanticSegmentationLabelInfo,
                                EnhancedImagingFrameDesc, DepthCameraFrameInfo)
        
        # Camera calibration operations
        self.lib.slamtec_aurora_sdk_dataprovider_get_camera_calibration.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(CameraCalibrationInfo)  # calibration_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_camera_calibration.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_get_transform_calibration.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(TransformCalibrationInfo)  # transform_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_get_transform_calibration.restype = ctypes.c_int
        
        # SUPERVISOR FIX: Missing Enhanced Imaging readiness functions
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_is_ready.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_is_ready.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_get_config_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(DepthCameraFrameInfo)  # config_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_get_config_info.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_wait_next_frame.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_wait_next_frame.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_is_ready.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_is_ready.restype = ctypes.c_int
        
        # Enhanced imaging depth camera operations (correct C API signature)
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_frame.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int,     # frame_type
            ctypes.POINTER(EnhancedImagingFrameDesc),  # frame_desc_out
            ctypes.POINTER(EnhancedImagingFrameBuffer)  # frame_buffer
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_frame.restype = ctypes.c_int
        
        # Depth camera related rectified image operations
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_related_rectified_image.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64,  # timestamp
            ctypes.POINTER(EnhancedImagingFrameDesc),  # frame_desc_out
            ctypes.POINTER(EnhancedImagingFrameBuffer)  # frame_buffer
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_related_rectified_image.restype = ctypes.c_int
        
        # Enhanced imaging semantic segmentation operations
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_config_info.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(SemanticSegmentationConfig)  # config_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_config_info.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_labels.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(SemanticSegmentationLabelInfo)  # label_info_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_labels.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_label_set_name.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_char_p,  # label_set_name_buffer
            ctypes.c_size_t   # buffer_size
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_label_set_name.restype = ctypes.c_size_t
        
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_peek_frame.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(EnhancedImagingFrameDesc),  # frame_desc_out
            ctypes.POINTER(EnhancedImagingFrameBuffer)  # frame_buffer
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_peek_frame.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_wait_next_frame.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_wait_next_frame.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_is_using_alternative_model.argtypes = [
            ctypes.c_void_p   # handle
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_is_using_alternative_model.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_calc_aligned_segmentation_map.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ImageDesc),  # desc_in (input image descriptor)
            ctypes.c_void_p,  # raw_segment_data
            ctypes.POINTER(ImageDesc),  # desc_out (output image descriptor)
            ctypes.c_void_p   # aligned_segment_data (enhanced imaging frame buffer)
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_depthcam_calc_aligned_segmentation_map.restype = ctypes.c_int
        
        # Controller Enhanced Imaging subscription operations
        self.lib.slamtec_aurora_sdk_controller_set_enhanced_imaging_subscription.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int,     # enhanced_image_type
            ctypes.c_int      # enable
        ]
        self.lib.slamtec_aurora_sdk_controller_set_enhanced_imaging_subscription.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_is_enhanced_imaging_subscribed.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int      # enhanced_image_type
        ]
        self.lib.slamtec_aurora_sdk_controller_is_enhanced_imaging_subscribed.restype = ctypes.c_int
        
        # Controller semantic segmentation model operations
        self.lib.slamtec_aurora_sdk_controller_require_semantic_segmentation_alternative_model.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int,     # use_alternative_model
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_controller_require_semantic_segmentation_alternative_model.restype = ctypes.c_int
        
        # Map manager operations
        from .data_types import MapStorageSessionResultCallback, MapStorageSessionStatus
        
        self.lib.slamtec_aurora_sdk_mapmanager_start_storage_session.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_char_p,  # map_file_name
            ctypes.c_int,     # session_type
            MapStorageSessionResultCallback,  # callback
            ctypes.c_void_p   # user_data
        ]
        self.lib.slamtec_aurora_sdk_mapmanager_start_storage_session.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_mapmanager_abort_session.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_mapmanager_abort_session.restype = None
        
        self.lib.slamtec_aurora_sdk_mapmanager_is_storage_session_active.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_mapmanager_is_storage_session_active.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_mapmanager_query_storage_status.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(MapStorageSessionStatus)  # progress_out
        ]
        self.lib.slamtec_aurora_sdk_mapmanager_query_storage_status.restype = ctypes.c_int
        
        # IMU data operations
        from .data_types import IMUData
        
        self.lib.slamtec_aurora_sdk_dataprovider_peek_imu_data.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(IMUData),  # imu_data_out
            ctypes.c_size_t,  # max_count
            ctypes.POINTER(ctypes.c_size_t)  # actual_count_out
        ]
        self.lib.slamtec_aurora_sdk_dataprovider_peek_imu_data.restype = ctypes.c_int
        
        # Relocalization operations
        self.lib.slamtec_aurora_sdk_controller_require_relocalization.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_controller_require_relocalization.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_cancel_relocalization.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_controller_cancel_relocalization.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_require_map_reset.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_controller_require_map_reset.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_require_pure_localization_mode.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_controller_require_pure_localization_mode.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_is_device_connection_alive.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_controller_is_device_connection_alive.restype = ctypes.c_int
        
        self.lib.slamtec_aurora_sdk_controller_is_raw_data_subscribed.argtypes = [ctypes.c_void_p]
        self.lib.slamtec_aurora_sdk_controller_is_raw_data_subscribed.restype = ctypes.c_int
        
        # CORRECTED: Fixed function signatures to match C API exactly
        # void slamtec_aurora_sdk_controller_set_low_rate_mode(handle, int enable)
        self.lib.slamtec_aurora_sdk_controller_set_low_rate_mode.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int      # enable
        ]
        self.lib.slamtec_aurora_sdk_controller_set_low_rate_mode.restype = None  # FIXED: void return
        
        # slamtec_aurora_sdk_errorcode_t slamtec_aurora_sdk_controller_set_loop_closure(handle, int enable, uint64_t timeout_ms)
        self.lib.slamtec_aurora_sdk_controller_set_loop_closure.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_int,     # enable
            ctypes.c_uint64   # timeout_ms - FIXED: Added missing parameter
        ]
        self.lib.slamtec_aurora_sdk_controller_set_loop_closure.restype = ctypes.c_int
        
        # slamtec_aurora_sdk_errorcode_t slamtec_aurora_sdk_controller_force_map_global_optimization(handle, uint64_t timeout_ms)
        self.lib.slamtec_aurora_sdk_controller_force_map_global_optimization.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64   # timeout_ms
        ]
        self.lib.slamtec_aurora_sdk_controller_force_map_global_optimization.restype = ctypes.c_int
        
        # slamtec_aurora_sdk_errorcode_t slamtec_aurora_sdk_controller_send_custom_command(
        #   handle, uint64_t timeout_ms, uint64_t cmd, const void* data, size_t data_size, 
        #   void* response, size_t response_buffer_size, size_t* response_retrieved_size)
        self.lib.slamtec_aurora_sdk_controller_send_custom_command.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint64,  # timeout_ms - FIXED: Added missing parameter
            ctypes.c_uint64,  # cmd - FIXED: Changed from char_p to uint64
            ctypes.c_void_p,  # data
            ctypes.c_size_t,  # data_size
            ctypes.c_void_p,  # response
            ctypes.c_size_t,  # response_buffer_size
            ctypes.POINTER(ctypes.c_size_t)  # response_retrieved_size
        ]
        self.lib.slamtec_aurora_sdk_controller_send_custom_command.restype = ctypes.c_int
    
    def get_version_info(self):
        """Get SDK version information."""
        version_info = VersionInfo()
        error_code = self.lib.slamtec_aurora_sdk_get_version_info(ctypes.byref(version_info))
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get version info, error code: {}".format(error_code))
        return version_info
    
    def create_session(self):
        """Create a new SDK session."""
        error_code = ctypes.c_int()
        handle = self.lib.slamtec_aurora_sdk_create_session(
            None, 0, None, ctypes.byref(error_code)
        )
        if error_code.value != ERRORCODE_OK or not handle:
            raise AuroraSDKError("Failed to create session, error code: {}".format(error_code.value))
        return handle
    
    def release_session(self, handle):
        """Release SDK session."""
        self.lib.slamtec_aurora_sdk_release_session(handle)
    
    def get_discovered_servers(self, handle, max_count = 32):
        """Get list of discovered Aurora servers."""
        servers = (ServerConnectionInfo * max_count)()
        count = self.lib.slamtec_aurora_sdk_controller_get_discovered_servers(
            handle, servers, max_count
        )
        if count < 0:
            raise AuroraSDKError("Failed to get discovered servers, error code: {}".format(count))
        return list(servers[:count])
    
    def discover_devices(self, handle, timeout=10.0):
        """Discover Aurora devices on the network."""
        import time
        
        # The C SDK performs passive discovery - we need to wait for it to discover devices
        # Based on the pure C demo, we wait for the discovery timeout period
        time.sleep(min(timeout, 10.0))  # Cap at 10 seconds max
        
        # Now get the discovered servers and convert to Python-friendly format
        servers = self.get_discovered_servers(handle)
        return self._convert_servers_to_dict(servers)
    
    def _convert_servers_to_dict(self, servers):
        """Convert ServerConnectionInfo structures to dictionaries."""
        result = []
        for i, server in enumerate(servers):
            # Extract connection options
            options = []
            for j in range(server.connection_count):
                conn_info = server.connection_info[j]
                options.append({
                    'protocol': conn_info.protocol_type.decode('utf-8', errors='ignore').rstrip('\x00'),
                    'address': conn_info.address.decode('utf-8', errors='ignore').rstrip('\x00'),
                    'port': conn_info.port
                })
            
            # Create device info dictionary
            device_dict = {
                'device_name': "Aurora Device {}".format(i),  # We don't have device name in ServerConnectionInfo
                'options': options,
                '_raw_server_info': server  # Keep raw info for connection
            }
            result.append(device_dict)
        
        return result
    
    def connect_device(self, handle, device_info):
        """Connect to Aurora device using device info dictionary from discovery."""
        if isinstance(device_info, dict):
            # Use the raw server info stored during discovery
            if '_raw_server_info' in device_info:
                server_info = device_info['_raw_server_info']
            else:
                raise AuroraSDKError("Invalid device info - missing raw server info")
        else:
            # Assume it's already a ServerConnectionInfo structure
            server_info = device_info
            
        error_code = self.lib.slamtec_aurora_sdk_controller_connect(
            handle, ctypes.byref(server_info)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to connect to server, error code: {} (INVALID_ARGUMENT)".format(error_code))
        return server_info
    
    def connect_string(self, handle, connection_string):
        """Connect to Aurora device using connection string."""
        from .data_types import ServerConnectionInfo, ConnectionInfo
        
        # Create ServerConnectionInfo from connection string
        server_info = ServerConnectionInfo()
        server_info.connection_count = 1
        
        # Parse connection string (assume IP address for now)
        conn_info = server_info.connection_info[0]
        conn_info.protocol_type = b"tcp"  # Default protocol
        conn_info.address = connection_string.encode('utf-8')
        conn_info.port = 7447  # SLAMTEC_AURORA_SDK_REMOTE_SERVER_DEFAULT_PORT
        
        error_code = self.lib.slamtec_aurora_sdk_controller_connect(
            handle, ctypes.byref(server_info)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to connect to server, error code: {} (INVALID_ARGUMENT)".format(error_code))
        return server_info
    
    def connect(self, handle, server_info):
        """Connect to Aurora server (legacy method)."""
        error_code = self.lib.slamtec_aurora_sdk_controller_connect(
            handle, ctypes.byref(server_info)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to connect to server, error code: {} (INVALID_ARGUMENT)".format(error_code))
    
    def disconnect(self, handle):
        """Disconnect from Aurora server."""
        self.lib.slamtec_aurora_sdk_controller_disconnect(handle)
    
    def is_connected(self, handle):
        """Check if connected to Aurora server."""
        return bool(self.lib.slamtec_aurora_sdk_controller_is_connected(handle))
    
    def set_map_data_syncing(self, handle, enable):
        """Enable/disable map data syncing."""
        self.lib.slamtec_aurora_sdk_controller_set_map_data_syncing(handle, int(enable))
    
    def set_raw_data_subscription(self, handle, enable):
        """Enable/disable raw data subscription."""
        error_code = self.lib.slamtec_aurora_sdk_controller_set_raw_data_subscription(
            handle, int(enable)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set raw data subscription, error code: {}".format(error_code))
    
    def get_current_pose_se3(self, handle):
        """Get current pose in SE3 format with timestamp."""
        pose = PoseSE3()
        timestamp_ns = ctypes.c_uint64()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_current_pose_se3_with_timestamp(
            handle, ctypes.byref(pose), ctypes.byref(timestamp_ns)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get current pose SE3, error code: {}".format(error_code))
        return pose, timestamp_ns.value
    
    def get_current_pose(self, handle):
        """Get current pose in Euler angle format with timestamp."""
        pose = Pose()
        timestamp_ns = ctypes.c_uint64()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_current_pose_with_timestamp(
            handle, ctypes.byref(pose), ctypes.byref(timestamp_ns)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get current pose, error code: {}".format(error_code))
        return pose, timestamp_ns.value
    
    def get_device_basic_info(self, handle):
        """Get device basic information."""
        info = DeviceBasicInfo()
        timestamp = ctypes.c_uint64()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_last_device_basic_info(
            handle, ctypes.byref(info), ctypes.byref(timestamp)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get device basic info, error code: {}".format(error_code))
        return info, timestamp.value
    
    
    def peek_camera_preview_image(self, handle, timestamp_ns = 0):
        """Get camera preview image with actual pixel data."""
        desc = StereoImagePairDesc()
        
        # First call to get image dimensions
        buffer_info = StereoImagePairBuffer()
        buffer_info.imgdata_left = None
        buffer_info.imgdata_right = None
        buffer_info.imgdata_left_size = 0
        buffer_info.imgdata_right_size = 0
        
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_peek_camera_preview_image(
            handle, timestamp_ns, ctypes.byref(desc), ctypes.byref(buffer_info), 1
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get camera preview image, error code: {}".format(error_code))
        
        # Now allocate buffers and get actual image data
        left_data = None
        right_data = None
        
        if desc.left_image_desc.width > 0 and desc.left_image_desc.data_size > 0:
            # Allocate buffer for left image
            left_buffer = (ctypes.c_uint8 * desc.left_image_desc.data_size)()
            buffer_info.imgdata_left = ctypes.cast(left_buffer, ctypes.c_void_p)
            buffer_info.imgdata_left_size = desc.left_image_desc.data_size
        
        if desc.right_image_desc.width > 0 and desc.right_image_desc.data_size > 0:
            # Allocate buffer for right image
            right_buffer = (ctypes.c_uint8 * desc.right_image_desc.data_size)()
            buffer_info.imgdata_right = ctypes.cast(right_buffer, ctypes.c_void_p)
            buffer_info.imgdata_right_size = desc.right_image_desc.data_size
        
        # Second call to actually get the image data
        if buffer_info.imgdata_left or buffer_info.imgdata_right:
            error_code = self.lib.slamtec_aurora_sdk_dataprovider_peek_camera_preview_image(
                handle, timestamp_ns, ctypes.byref(desc), ctypes.byref(buffer_info), 1
            )
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to get camera preview image data, error code: {}".format(error_code))
            
            # Extract image data from buffers
            if buffer_info.imgdata_left and desc.left_image_desc.data_size > 0:
                left_data = bytes(left_buffer)
                
            if buffer_info.imgdata_right and desc.right_image_desc.data_size > 0:
                right_data = bytes(right_buffer)
        
        return desc, left_data, right_data
    
    def peek_tracking_data(self, handle):
        """Get tracking frame data with keypoints."""
        tracking_info = TrackingInfo()
        
        # Allocate reasonable buffer sizes upfront (typical approach for tracking data)
        max_keypoints = 1000  # Should be enough for most cases
        max_image_size = 1920 * 1080 * 4  # Assume max 1920x1080 RGBA
        
        # Allocate image buffers
        left_image_buffer = (ctypes.c_uint8 * max_image_size)()
        right_image_buffer = (ctypes.c_uint8 * max_image_size)()
        
        # Allocate keypoint buffers
        left_keypoints_buffer = (Keypoint * max_keypoints)()
        right_keypoints_buffer = (Keypoint * max_keypoints)()
        
        # Create tracking data buffer with allocated buffers
        tracking_buffer = TrackingDataBuffer()
        tracking_buffer.imgdata_left = ctypes.cast(left_image_buffer, ctypes.c_void_p)
        tracking_buffer.imgdata_left_size = max_image_size
        tracking_buffer.imgdata_right = ctypes.cast(right_image_buffer, ctypes.c_void_p)
        tracking_buffer.imgdata_right_size = max_image_size
        tracking_buffer.keypoints_left = ctypes.cast(left_keypoints_buffer, ctypes.POINTER(Keypoint))
        tracking_buffer.keypoints_left_buffer_count = max_keypoints
        tracking_buffer.keypoints_right = ctypes.cast(right_keypoints_buffer, ctypes.POINTER(Keypoint))
        tracking_buffer.keypoints_right_buffer_count = max_keypoints
        
        # Call the tracking data function
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_peek_tracking_data(
            handle, ctypes.byref(tracking_info), ctypes.byref(tracking_buffer)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get tracking data, error code: {}".format(error_code))
        
        # Extract keypoints - return actual Keypoint objects
        left_keypoints = []
        if tracking_info.keypoints_left_count > 0:
            for i in range(min(tracking_info.keypoints_left_count, max_keypoints)):
                kp = left_keypoints_buffer[i]
                left_keypoints.append(kp)  # Keep as Keypoint object with .x, .y, .flags attributes
        
        right_keypoints = []
        if tracking_info.keypoints_right_count > 0:
            for i in range(min(tracking_info.keypoints_right_count, max_keypoints)):
                kp = right_keypoints_buffer[i]
                right_keypoints.append(kp)  # Keep as Keypoint object with .x, .y, .flags attributes
        # Extract image data if available
        left_image_data = None
        right_image_data = None
        
        if tracking_info.left_image_desc.width > 0 and tracking_info.left_image_desc.height > 0:
            # Calculate expected image size
            expected_size = tracking_info.left_image_desc.width * tracking_info.left_image_desc.height
            if tracking_info.left_image_desc.format == 1:  # RGB
                expected_size *= 3
            elif tracking_info.left_image_desc.format == 2:  # RGBA
                expected_size *= 4
            
            # Extract image data from buffer
            if expected_size <= max_image_size:
                left_image_data = bytes(left_image_buffer[:expected_size])
        
        if tracking_info.right_image_desc.width > 0 and tracking_info.right_image_desc.height > 0:
            # Calculate expected image size
            expected_size = tracking_info.right_image_desc.width * tracking_info.right_image_desc.height
            if tracking_info.right_image_desc.format == 1:  # RGB
                expected_size *= 3
            elif tracking_info.right_image_desc.format == 2:  # RGBA
                expected_size *= 4
            
            # Extract image data from buffer
            if expected_size <= max_image_size:
                right_image_data = bytes(right_image_buffer[:expected_size])
        
        return tracking_info, left_keypoints, right_keypoints, left_image_data, right_image_data
    
    
    def require_mapping_mode(self, handle, timeout_ms=10000):
        """Require the device to enter mapping mode."""
        error_code = self.lib.slamtec_aurora_sdk_controller_require_mapping_mode(handle, timeout_ms)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to enter mapping mode, error code: {}".format(error_code))
    
    def resync_map_data(self, handle, invalidate_cache=True):
        """Force resync of map data."""
        error_code = self.lib.slamtec_aurora_sdk_controller_resync_map_data(handle, int(invalidate_cache))
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to resync map data, error code: {}".format(error_code))
    
    def get_global_mapping_info_legacy(self, handle):
        """Get global mapping information (legacy)."""
        # This is a simplified implementation used by map_manager
        # Use the real implementation but format for legacy compatibility
        try:
            real_info = self.get_global_mapping_info(handle)
            return {
                'active_map_id': real_info['active_map_id'],
                'map_count': real_info['total_map_count'],
                'status': 'mapping'
            }
        except:
            return {
                'active_map_id': 0,
                'map_count': 1,
                'status': 'mapping'
            }
    
    def start_lidar2d_preview_map(self, handle, resolution=0.05):
        """Start LIDAR 2D map preview generation."""
        from .data_types import GridMapGenerationOptions
        
        # Create generation options
        options = GridMapGenerationOptions()
        options.resolution = resolution
        options.width = 100.0  # Default 100m x 100m map
        options.height = 100.0
        options.origin_x = 0.0
        options.origin_y = 0.0
        options.height_range_specified = 0  # Don't filter by height
        options.min_height = 0.0
        options.max_height = 0.0
        
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_start_background_update(
            handle, ctypes.byref(options)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to start LIDAR 2D map preview, error code: {}".format(error_code))
    
    def stop_lidar2d_preview_map(self, handle):
        """Stop LIDAR 2D map preview generation."""
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_stop_background_update(handle)
    
    def get_lidar2d_preview_map(self, handle):
        """Get current LIDAR 2D map preview."""
        # Get the gridmap handle
        gridmap_handle = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_gridmap_handle(handle)
        if not gridmap_handle:
            return None
        
        # For now, return a placeholder. Full implementation would read grid data.
        return {
            'gridmap_handle': gridmap_handle,
            'status': 'preview_available'
        }
    
    def get_global_mapping_info(self, handle):
        """Get global mapping information."""
        from .data_types import GlobalMapDesc
        
        global_desc = GlobalMapDesc()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_global_mapping_info(
            handle, ctypes.byref(global_desc)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get global mapping info, error code: {}".format(error_code))
        
        # Return complete GlobalMapDesc structure with all fields accessible
        return {
            # Fetching/retrieval counts
            'lastMPCountToFetch': global_desc.lastMPCountToFetch,
            'lastKFCountToFetch': global_desc.lastKFCountToFetch,
            'lastMapCountToFetch': global_desc.lastMapCountToFetch,
            'lastMPRetrieved': global_desc.lastMPRetrieved,
            'lastKFRetrieved': global_desc.lastKFRetrieved,
            
            # Total counts
            'totalMPCount': global_desc.totalMPCount,
            'total_kf_count': global_desc.totalKFCount,  # Key field for sync status
            'totalMapCount': global_desc.totalMapCount,
            
            # Fetched counts (for sync status calculation)
            'totalMPCountFetched': global_desc.totalMPCountFetched,
            'total_kf_count_fetched': global_desc.totalKFCountFetched,  # Key field for sync status
            'totalMapCountFetched': global_desc.totalMapCountFetched,
            
            # Current active counts
            'currentActiveMPCount': global_desc.currentActiveMPCount,
            'currentActiveKFCount': global_desc.currentActiveKFCount,
            
            # Map and state information
            'active_map_id': global_desc.activeMapID,
            'mappingFlags': global_desc.mappingFlags,
            'slidingWindowStartKFId': global_desc.slidingWindowStartKFId
        }
    
    def access_map_data(self, handle):
        """Access visual map data (map points and keyframes)."""
        from .data_types import MapDataVisitor, MapPointCallback, KeyframeCallback, MapDescCallback
        
        # Storage for collected data - use lists that persist outside callback scope
        collected_data = {'map_points': [], 'keyframes': [], 'loop_closures': []}
        
        # Callback to collect map points - make more robust
        def map_point_callback(user_data, map_point_ptr):
            try:
                if map_point_ptr:
                    mp = map_point_ptr.contents
                    collected_data['map_points'].append((float(mp.position.x), float(mp.position.y), float(mp.position.z)))
            except Exception:
                pass  # Ignore errors in callback to prevent crashes
        
        # Callback to collect keyframes - make more robust
        def keyframe_callback(user_data, keyframe_ptr, looped_ids, connected_ids):
            try:
                if keyframe_ptr:
                    kf = keyframe_ptr.contents
                    # Use SE3 pose for position and rotation
                    pos = kf.pose_se3.translation
                    rot = kf.pose_se3.quaternion
                    keyframe_id = kf.id
                    
                    # Store keyframe with ID
                    keyframe_tuple = (
                        float(pos.x), float(pos.y), float(pos.z), 
                        float(rot.x), float(rot.y), float(rot.z), float(rot.w),
                        int(keyframe_id)
                    )
                    collected_data['keyframes'].append(keyframe_tuple)
                    
                    # Process loop closure connections
                    if looped_ids:
                        # Count how many looped frame IDs are provided
                        # The array is null-terminated, so count until we hit 0
                        loop_count = 0
                        try:
                            while looped_ids[loop_count] != 0:
                                looped_frame_id = looped_ids[loop_count]
                                # Store loop closure connection: (from_keyframe_id, to_keyframe_id)
                                loop_closure = (int(keyframe_id), int(looped_frame_id))
                                collected_data['loop_closures'].append(loop_closure)
                                loop_count += 1
                                if loop_count > 100:  # Safety limit to prevent infinite loop
                                    break
                        except Exception:
                            pass  # Ignore errors in loop processing
                            
            except Exception:
                pass  # Ignore errors in callback to prevent crashes
        
        # Dummy callback for map description - make more robust
        def map_desc_callback(user_data, map_desc_ptr):
            try:
                pass  # Not needed for visualization
            except Exception:
                pass
        
        # Keep references to prevent garbage collection
        map_point_cb = MapPointCallback(map_point_callback)
        keyframe_cb = KeyframeCallback(keyframe_callback)
        map_desc_cb = MapDescCallback(map_desc_callback)
        
        # Create visitor with callbacks
        visitor = MapDataVisitor()
        visitor.user_data = None
        visitor.on_map_point = map_point_cb
        visitor.on_keyframe = keyframe_cb
        visitor.on_map_desc = map_desc_cb
        
        try:
            # Get active map ID
            global_info = self.get_global_mapping_info(handle)
            active_map_id = global_info['active_map_id']
            
            # Call access_map_data for the active map
            map_ids = (ctypes.c_uint32 * 1)(active_map_id)
            error_code = self.lib.slamtec_aurora_sdk_dataprovider_access_map_data(
                handle, ctypes.byref(visitor), map_ids, 1
            )
            
            if error_code != ERRORCODE_OK:
                # Don't raise exception, just return empty data
                return {'map_points': [], 'keyframes': [], 'loop_closures': []}
                
        except Exception as e:
            # If there's an error, return empty data but don't fail completely
            return {'map_points': [], 'keyframes': [], 'loop_closures': []}
        
        return collected_data
    
    # LiDAR scan data functions
    def peek_recent_lidar_scan(self, handle, max_points=8192, force_latest=0):
        """Get the most recent LiDAR scan data."""
        from .data_types import LidarSinglelayerScanDataInfo, LidarScanPoint, PoseSE3
        
        # Create scan info structure
        scan_info = LidarSinglelayerScanDataInfo()
        
        # Create scan points buffer
        scan_points = (LidarScanPoint * max_points)()
        
        # Create pose structure for scan pose
        scan_pose = PoseSE3()
        
        # Call the C function with all 6 required arguments
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_peek_recent_lidar_scan_singlelayer(
            handle, 
            ctypes.byref(scan_info), 
            scan_points, 
            max_points,
            ctypes.byref(scan_pose),
            force_latest
        )
        
        if error_code != ERRORCODE_OK:
            if error_code == ERRORCODE_NOT_READY:
                return None  # No scan data available yet
            else:
                raise AuroraSDKError("Failed to get LiDAR scan data, error code: {}".format(error_code))
        
        return scan_info, scan_points[:scan_info.scan_count], scan_pose
    
    # 2D Grid Map functions
    def start_lidar2dmap_preview(self, handle, options):
        """Start LIDAR 2D grid map preview generation."""
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_start_background_update(
            handle, ctypes.byref(options)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to start LIDAR 2D map preview, error code: {}".format(error_code))
    
    def stop_lidar2dmap_preview(self, handle):
        """Stop LIDAR 2D grid map preview generation."""
        self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_stop_background_update(handle)
    
    
    
    
    def get_lidar2dmap_preview_handle(self, handle):
        """Get the handle of the preview 2D grid map."""
        gridmap_handle = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_gridmap_handle(handle)
        return gridmap_handle
    
    
    def is_lidar2dmap_preview_updating(self, handle):
        """Check if LIDAR 2D grid map preview is updating."""
        return bool(self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_is_background_updating(handle))
    
    def require_lidar2dmap_redraw(self, handle):
        """Require redraw of the 2D map preview."""
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_require_redraw(handle)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to require map redraw, error code: {}".format(error_code))
    
    def get_lidar2dmap_dirty_rect(self, handle):
        """Get and reset the dirty rectangle of the 2D map preview."""
        from .data_types import Rect
        
        dirty_rect = Rect()
        map_changed = ctypes.c_int()
        
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_get_and_reset_update_dirty_rect(
            handle, ctypes.byref(dirty_rect), ctypes.byref(map_changed)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get dirty rect, error code: {}".format(error_code))
        
        return dirty_rect, bool(map_changed.value)
    
    def set_lidar2dmap_auto_floor_detection(self, handle, enable):
        """Enable/disable auto floor detection for 2D map."""
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_set_auto_floor_detection(
            handle, int(enable)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set auto floor detection, error code: {}".format(error_code))
    
    def is_lidar2dmap_auto_floor_detection(self, handle):
        """Check if auto floor detection is enabled."""
        return bool(self.lib.slamtec_aurora_sdk_lidar2dmap_previewmap_is_auto_floor_detection(handle))
    
    def get_gridmap_dimension(self, gridmap_handle, get_max_capacity=False):
        """Get the dimension of a 2D grid map."""
        from .data_types import GridMap2DDimension
        
        dimension = GridMap2DDimension()
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_get_dimension(
            gridmap_handle, ctypes.byref(dimension), int(get_max_capacity)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get grid map dimension, error code: {}".format(error_code))
        
        return dimension
    
    def read_gridmap_cell_data(self, gridmap_handle, fetch_rect, resolution=0.05, l2p_mapping=True):
        """
        Read cell data from a 2D grid map.
        
        Args:
            gridmap_handle: Handle to the grid map
            fetch_rect: Rectangle area to fetch (in meters)
            resolution: Map resolution in meters per cell (default: 0.05m = 5cm)
            l2p_mapping: If True, perform log-odd to linear (0-255) mapping for visualization.
                        If False, return raw data for navigation (default: True)
        
        Returns:
            tuple: (cell_data_list, fetch_info)
        """
        from .data_types import GridMap2DFetchInfo
        
        # Validate input rectangle
        if fetch_rect.width <= 0 or fetch_rect.height <= 0:
            # Return empty data for invalid rectangle
            fetch_info = GridMap2DFetchInfo()
            fetch_info.real_x = fetch_rect.x
            fetch_info.real_y = fetch_rect.y
            fetch_info.cell_width = 0
            fetch_info.cell_height = 0
            return [], fetch_info
        
        # Calculate buffer size based on fetch rectangle and resolution
        # This is the correct way to calculate expected cell count
        expected_width_cells = int(abs(fetch_rect.width) / resolution) + 1
        expected_height_cells = int(abs(fetch_rect.height) / resolution) + 1
        buffer_size = expected_width_cells * expected_height_cells
        
        # Add some safety margin but cap at reasonable size
        buffer_size = min(buffer_size * 2, 50000000)  # Cap at 50M cells for safety
        
        # Allocate buffer
        cell_buffer = (ctypes.c_uint8 * buffer_size)()
        fetch_info = GridMap2DFetchInfo()
        
        # Initialize fetch_info
        fetch_info.real_x = 0.0
        fetch_info.real_y = 0.0
        fetch_info.cell_width = 0
        fetch_info.cell_height = 0
        
        # Call C function with correct parameter order and l2p_mapping
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_read_cell_data(
            gridmap_handle,
            ctypes.byref(fetch_rect),
            ctypes.byref(fetch_info),  # info_out comes before cell_buffer
            cell_buffer,
            buffer_size,  # explicit buffer size
            int(l2p_mapping)  # l2p_mapping parameter
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to read grid map cell data, error code: {}".format(error_code))
        
        # Get actual data size from fetch_info
        actual_data_size = fetch_info.cell_width * fetch_info.cell_height
        
        # Validate fetch_info values
        if (fetch_info.cell_width < 0 or fetch_info.cell_height < 0 or 
            actual_data_size > buffer_size):
            # Return empty data if fetch_info contains invalid values
            fetch_info.cell_width = 0
            fetch_info.cell_height = 0
            return [], fetch_info
        
        # Return actual data based on fetch_info
        if actual_data_size > 0:
            return list(cell_buffer[:actual_data_size]), fetch_info
        else:
            return [], fetch_info
    
    # Auto floor detection operations
    def get_floor_detection_histogram(self, handle):
        """Get floor detection histogram data."""
        from .data_types import FloorDetectionHistogramInfo
        
        # Get histogram info first
        histogram_info = FloorDetectionHistogramInfo()
        
        # Allocate buffer for histogram data (reasonable maximum)
        max_bins = 1000  # Should be enough for most cases
        histogram_buffer = (ctypes.c_float * max_bins)()
        
        error_code = self.lib.slamtec_aurora_sdk_autofloordetection_get_detection_histogram(
            handle,
            ctypes.byref(histogram_info),
            histogram_buffer,
            max_bins
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get floor detection histogram, error code: {}".format(error_code))
        
        # Extract actual histogram data based on bin_total_count
        actual_count = min(histogram_info.bin_total_count, max_bins)
        histogram_data = [histogram_buffer[i] for i in range(actual_count)]
        
        return histogram_info, histogram_data
    
    def get_all_floor_detection_info(self, handle):
        """Get all floor detection descriptions and current floor ID."""
        from .data_types import FloorDetectionDesc
        
        # Allocate buffer for floor descriptions
        max_floors = 20  # Should be enough for most scenarios
        desc_buffer = (FloorDetectionDesc * max_floors)()
        actual_count = ctypes.c_size_t()
        current_floor_id = ctypes.c_int()
        
        error_code = self.lib.slamtec_aurora_sdk_autofloordetection_get_all_detection_info(
            handle,
            desc_buffer,
            max_floors,
            ctypes.byref(actual_count),
            ctypes.byref(current_floor_id)
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get all floor detection info, error code: {}".format(error_code))
        
        # Extract floor descriptions
        floor_descriptions = []
        for i in range(min(actual_count.value, max_floors)):
            floor_descriptions.append(desc_buffer[i])
        
        return floor_descriptions, current_floor_id.value
    
    def get_current_floor_detection_desc(self, handle):
        """Get current floor detection description."""
        from .data_types import FloorDetectionDesc
        
        desc = FloorDetectionDesc()
        
        error_code = self.lib.slamtec_aurora_sdk_autofloordetection_get_current_detection_desc(
            handle,
            ctypes.byref(desc)
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get current floor detection desc, error code: {}".format(error_code))
        
        return desc
    
    def generate_lidar_2d_fullmap(self, handle, build_options, wait_for_data_sync=True, timeout_ms=60000):
        """
        Generate full 2D LiDAR map on-demand.
        
        Args:
            handle: Session handle
            build_options: GridMapGenerationOptions for the map generation
            wait_for_data_sync: Whether to wait for map data sync (default: True)
            timeout_ms: Timeout in milliseconds (default: 60000)
            
        Returns:
            Handle to the generated 2D grid map
        """
        from .data_types import GridMapGenerationOptions
        
        # Output handle for the generated map
        generated_handle = ctypes.c_void_p()
        
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_generate_fullmap(
            handle,
            ctypes.byref(generated_handle),
            ctypes.byref(build_options),
            int(wait_for_data_sync),
            ctypes.c_uint64(timeout_ms)
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to generate full 2D LiDAR map, error code: {}".format(error_code))
        
        return generated_handle
    
    # Controller Enhanced Imaging operations (SDK 2.0)
    def set_enhanced_imaging_subscription(self, handle, enhanced_image_type, enable):
        """Set enhanced imaging subscription for specific image type."""
        error_code = self.lib.slamtec_aurora_sdk_controller_set_enhanced_imaging_subscription(
            handle, enhanced_image_type, int(enable)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set enhanced imaging subscription, error code: {}".format(error_code))
    
    def is_enhanced_imaging_subscribed(self, handle, enhanced_image_type):
        """Check if enhanced imaging is subscribed for specific image type."""
        return bool(self.lib.slamtec_aurora_sdk_controller_is_enhanced_imaging_subscribed(
            handle, enhanced_image_type
        ))
    
    def require_semantic_segmentation_alternative_model(self, handle, use_alternative_model, timeout_ms=5000):
        """Require semantic segmentation to use alternative model."""
        error_code = self.lib.slamtec_aurora_sdk_controller_require_semantic_segmentation_alternative_model(
            handle, int(use_alternative_model), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set semantic segmentation model, error code: {}".format(error_code))
    
    # Enhanced Imaging API methods (SDK 2.0)
    def get_camera_calibration(self, handle):
        """Get camera calibration parameters."""
        from .data_types import CameraCalibrationInfo
        
        calibration_info = CameraCalibrationInfo()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_camera_calibration(
            handle, ctypes.byref(calibration_info)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get camera calibration, error code: {}".format(error_code))
        
        return calibration_info
    
    def get_transform_calibration(self, handle):
        """Get transform calibration parameters."""
        from .data_types import TransformCalibrationInfo
        
        transform_info = TransformCalibrationInfo()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_transform_calibration(
            handle, ctypes.byref(transform_info)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get transform calibration, error code: {}".format(error_code))
        
        return transform_info
    
    def peek_depth_camera_frame(self, handle, frame_type=0):
        """Get depth camera frame data using correct C API (two-step process like C++)."""
        from .data_types import EnhancedImagingFrameDesc, EnhancedImagingFrameBuffer
        
        frame_desc = EnhancedImagingFrameDesc()
        frame_buffer = EnhancedImagingFrameBuffer()
        
        # First call: Get frame descriptor and data size (with empty buffer)
        frame_buffer.frame_data = None
        frame_buffer.frame_data_size = 0
        
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_frame(
            handle, frame_type, ctypes.byref(frame_desc), ctypes.byref(frame_buffer)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get depth camera frame info, error code: {}".format(error_code))
        
        # Allocate buffer for frame data based on the returned size
        frame_data = None
        if frame_desc.image_desc.data_size > 0:
            data_buffer = (ctypes.c_uint8 * frame_desc.image_desc.data_size)()
            frame_buffer.frame_data = ctypes.cast(data_buffer, ctypes.c_void_p)
            frame_buffer.frame_data_size = frame_desc.image_desc.data_size
            
            # Second call: Get actual frame data
            error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_frame(
                handle, frame_type, ctypes.byref(frame_desc), ctypes.byref(frame_buffer)
            )
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to get depth camera frame data, error code: {}".format(error_code))
            
            # Extract the frame data
            frame_data = bytes(data_buffer)
        
        return frame_desc, frame_data
    
    def peek_depth_camera_related_rectified_image(self, handle, timestamp):
        """Get depth camera related rectified image using correct C API."""
        from .data_types import EnhancedImagingFrameDesc, EnhancedImagingFrameBuffer
        
        frame_desc = EnhancedImagingFrameDesc()
        frame_buffer = EnhancedImagingFrameBuffer()
        
        # First call: Get frame descriptor and data size (with empty buffer)
        frame_buffer.frame_data = None
        frame_buffer.frame_data_size = 0
        
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_related_rectified_image(
            handle, timestamp, ctypes.byref(frame_desc), ctypes.byref(frame_buffer)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get rectified image info, error code: {}".format(error_code))
        
        # Allocate buffer for frame data based on the returned size
        frame_data = None
        if frame_desc.image_desc.data_size > 0:
            data_buffer = (ctypes.c_uint8 * frame_desc.image_desc.data_size)()
            frame_buffer.frame_data = ctypes.cast(data_buffer, ctypes.c_void_p)
            frame_buffer.frame_data_size = frame_desc.image_desc.data_size
            
            # Second call: Get actual frame data
            error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_peek_related_rectified_image(
                handle, timestamp, ctypes.byref(frame_desc), ctypes.byref(frame_buffer)
            )
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to get rectified image data, error code: {}".format(error_code))
            
            # Extract the frame data
            frame_data = bytes(data_buffer)
        
        return frame_desc, frame_data
    
    def get_semantic_segmentation_config(self, handle):
        """Get semantic segmentation configuration."""
        from .data_types import SemanticSegmentationConfig
        
        config = SemanticSegmentationConfig()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_config_info(
            handle, ctypes.byref(config)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get semantic segmentation config, error code: {}".format(error_code))
        
        return config
    
    def get_semantic_segmentation_labels(self, handle):
        """Get semantic segmentation label information."""
        from .data_types import SemanticSegmentationLabelInfo
        
        label_info = SemanticSegmentationLabelInfo()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_labels(
            handle, ctypes.byref(label_info)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get semantic segmentation labels, error code: {}".format(error_code))
        
        return label_info
    
    def get_semantic_segmentation_label_set_name(self, handle):
        """Get semantic segmentation label set name."""
        buffer_size = 256  # Should be enough for label set name
        buffer = ctypes.create_string_buffer(buffer_size)
        
        actual_size = self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_get_label_set_name(
            handle, buffer, buffer_size
        )
        
        if actual_size == 0:
            raise AuroraSDKError("Failed to get semantic segmentation label set name")
        
        return buffer.value.decode('utf-8').rstrip('\0')
    
    def peek_semantic_segmentation_frame(self, handle, timestamp_ns=0, allow_nearest=True):
        """Get semantic segmentation frame data using two-step buffer allocation."""
        from .data_types import EnhancedImagingFrameDesc, EnhancedImagingFrameBuffer
        
        frame_desc = EnhancedImagingFrameDesc()
        frame_buffer = EnhancedImagingFrameBuffer()
        
        # First call: Get frame descriptor and data size (with empty buffer)
        frame_buffer.frame_data = None
        frame_buffer.frame_data_size = 0
        
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_peek_frame(
            handle, ctypes.byref(frame_desc), ctypes.byref(frame_buffer)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get semantic segmentation frame info, error code: {}".format(error_code))
        
        # Allocate buffer for frame data based on the returned size
        segmentation_data = None
        if frame_desc.image_desc.data_size > 0:
            data_buffer = (ctypes.c_uint8 * frame_desc.image_desc.data_size)()
            frame_buffer.frame_data = ctypes.cast(data_buffer, ctypes.c_void_p)
            frame_buffer.frame_data_size = frame_desc.image_desc.data_size
            
            # Second call: Get actual frame data
            error_code = self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_peek_frame(
                handle, ctypes.byref(frame_desc), ctypes.byref(frame_buffer)
            )
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to get semantic segmentation frame data, error code: {}".format(error_code))
            
            # Extract the frame data
            segmentation_data = bytes(data_buffer)
        
        return frame_desc, segmentation_data
    
    def wait_semantic_segmentation_next_frame(self, handle, timeout_ms=1000):
        """Wait for the next semantic segmentation frame to be available."""
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_wait_next_frame(
            handle, timeout_ms
        )
        return error_code == ERRORCODE_OK
    
    def is_semantic_segmentation_using_alternative_model(self, handle):
        """Check if semantic segmentation is using alternative model."""
        return bool(self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_is_using_alternative_model(handle))
    
    def set_semantic_segmentation_model(self, handle, model_type):
        """Set semantic segmentation model type."""
        # This function doesn't exist in the actual library - removing for now
        raise AuroraSDKError("set_semantic_segmentation_model function not available in this SDK version")
    
    def calc_depth_aligned_segmentation_map(self, handle, segmentation_data, seg_width, seg_height):
        """Calculate depth camera aligned segmentation map (matching C++ implementation)."""
        # Create input image descriptor
        desc_in = ImageDesc()
        desc_in.width = seg_width
        desc_in.height = seg_height
        desc_in.stride = seg_width  # Assuming 1 byte per pixel
        desc_in.format = 0  # Assuming grayscale format for segmentation
        desc_in.data_size = len(segmentation_data)
        
        # Create output image descriptor
        desc_out = ImageDesc()
        
        # Create input buffer from segmentation data
        if isinstance(segmentation_data, bytes):
            input_buffer = (ctypes.c_uint8 * len(segmentation_data)).from_buffer_copy(segmentation_data)
        else:
            input_buffer = segmentation_data
        
        # Create enhanced imaging frame buffer for output (matching C++ logic)
        max_aligned_size = seg_width * seg_height * 2  # Conservative estimate
        aligned_buffer = (ctypes.c_uint8 * max_aligned_size)()
        
        # Create enhanced imaging frame buffer structure
        from .data_types import EnhancedImagingFrameBuffer
        frame_buffer = EnhancedImagingFrameBuffer()
        frame_buffer.frame_data = ctypes.cast(aligned_buffer, ctypes.c_void_p)
        frame_buffer.frame_data_size = max_aligned_size
        
        # Call the C API with proper parameters (like C++)
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_calc_aligned_segmentation_map(
            handle,
            ctypes.byref(desc_in),
            ctypes.cast(input_buffer, ctypes.c_void_p),
            ctypes.byref(desc_out),
            ctypes.byref(frame_buffer)
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to calculate depth aligned segmentation map, error code: {}".format(error_code))
        
        # Extract the actual aligned data using output descriptor
        actual_size = desc_out.width * desc_out.height
        if actual_size > 0 and desc_out.width > 0 and desc_out.height > 0:
            aligned_data = bytes(aligned_buffer[:actual_size])
            return aligned_data, desc_out.width, desc_out.height
        else:
            return None, 0, 0
    
    def require_map_reset(self, handle, timeout_ms=10000):
        """Require the device to reset its map."""
        error_code = self.lib.slamtec_aurora_sdk_controller_require_map_reset(handle, timeout_ms)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to reset map, error code: {}".format(error_code))
    
    def require_pure_localization_mode(self, handle, timeout_ms=10000):
        """Require the device to enter pure localization mode (no mapping)."""
        error_code = self.lib.slamtec_aurora_sdk_controller_require_pure_localization_mode(handle, timeout_ms)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to enter pure localization mode, error code: {}".format(error_code))
    
    def is_device_connection_alive(self, handle):
        """Check if the device connection is alive and healthy."""
        return bool(self.lib.slamtec_aurora_sdk_controller_is_device_connection_alive(handle))
    
    def is_raw_data_subscribed(self, handle):
        """Check if raw data subscription is active."""
        return bool(self.lib.slamtec_aurora_sdk_controller_is_raw_data_subscribed(handle))
    
    # Missing high-priority DataProvider operations - IMPLEMENTATION ADDED
    def get_last_device_status(self, handle):
        """Get the last device status information."""
        from .data_types import DeviceStatus
        
        status = DeviceStatus()
        timestamp = ctypes.c_uint64()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_last_device_status(
            handle, ctypes.byref(status), ctypes.byref(timestamp)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get device status, error code: {}".format(error_code))
        
        return status, timestamp.value
    
    def get_relocalization_status(self, handle):
        """Get relocalization status information."""
        from .data_types import RelocalizationStatus
        
        status = RelocalizationStatus()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_relocalization_status(
            handle, ctypes.byref(status)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get relocalization status, error code: {}".format(error_code))
        
        return status
    
    def get_mapping_flags(self, handle):
        """Get current mapping flags."""
        flags = ctypes.c_uint32()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_mapping_flags(
            handle, ctypes.byref(flags)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get mapping flags, error code: {}".format(error_code))
        
        return flags.value
    def convert_quaternion_to_euler(self, qx, qy, qz, qw):
        """Convert quaternion to Euler angles."""
        from .data_types import Quaternion, EulerAngle
        
        # Create quaternion structure
        quat = Quaternion()
        quat.x = qx
        quat.y = qy
        quat.z = qz
        quat.w = qw
        
        # Create euler angle output structure
        euler = EulerAngle()
        
        error_code = self.lib.slamtec_aurora_sdk_convert_quaternion_to_euler(
            ctypes.byref(quat), ctypes.byref(euler)
        )
        
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to convert quaternion to euler, error code: {}".format(error_code))
        
        return euler.roll, euler.pitch, euler.yaw
    
    # Enhanced Imaging readiness functions
    def depthcam_is_ready(self, handle):
        """Check if depth camera is ready."""
        return bool(self.lib.slamtec_aurora_sdk_dataprovider_depthcam_is_ready(handle))
    
    def depthcam_get_config_info(self, handle):
        """Get depth camera configuration."""
        from .data_types import DepthCameraFrameInfo
        
        config = DepthCameraFrameInfo()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_get_config_info(
            handle, ctypes.byref(config)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get depth camera config, error code: {}".format(error_code))
        
        return config
    
    def depthcam_wait_next_frame(self, handle, timeout_ms=1000):
        """Wait for next depth camera frame."""
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_depthcam_wait_next_frame(handle, timeout_ms)
        return error_code == ERRORCODE_OK
    
    def semantic_segmentation_is_ready(self, handle):
        """Check if semantic segmentation is ready."""
        return bool(self.lib.slamtec_aurora_sdk_dataprovider_semantic_segmentation_is_ready(handle))
    
    # LIDAR 2D Map critical functions
    def gridmap_release(self, gridmap_handle):
        """Release gridmap handle to prevent memory leaks."""
        self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_release(gridmap_handle)
    
    def gridmap_get_resolution(self, gridmap_handle):
        """Get gridmap resolution."""
        resolution = ctypes.c_float()
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_gridmap_get_resolution(
            gridmap_handle, ctypes.byref(resolution)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get gridmap resolution, error code: {}".format(error_code))
        
        return resolution.value
    
    def get_supported_grid_resolution_range(self, handle):
        """Get supported grid resolution range."""
        min_res = ctypes.c_float()
        max_res = ctypes.c_float()
        
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_get_supported_grid_resultion_range(
            handle, ctypes.byref(min_res), ctypes.byref(max_res)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get resolution range, error code: {}".format(error_code))
        
        return min_res.value, max_res.value
    
    def get_supported_max_grid_cell_count(self, handle):
        """Get maximum supported grid cell count."""
        max_count = ctypes.c_size_t()
        
        error_code = self.lib.slamtec_aurora_sdk_lidar2dmap_get_supported_max_grid_cell_count(
            handle, ctypes.byref(max_count)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get max cell count, error code: {}".format(error_code))
        
        return max_count.value

    def get_imu_info(self, handle):
        """Get IMU information."""
        from .data_types import IMUInfo
        info = IMUInfo()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_imu_info(handle, ctypes.byref(info))
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get IMU info, error code: {}".format(error_code))
        return info
    
    def get_all_map_info(self, handle, max_count=32):
        """Get information about all maps."""
        from .data_types import MapDesc
        desc_buffer = (MapDesc * max_count)()
        actual_count = ctypes.c_size_t()
        
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_get_all_map_info(
            handle, desc_buffer, max_count, ctypes.byref(actual_count)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get all map info, error code: {}".format(error_code))
        
        return list(desc_buffer[:actual_count.value])
    
    def peek_history_pose(self, handle, timestamp_ns=0, allow_interpolation=True, max_time_diff_ns=1000000000):
        """Peek historical pose at specific timestamp."""
        pose = PoseSE3()
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_peek_history_pose(
            handle, ctypes.byref(pose), timestamp_ns, int(allow_interpolation), max_time_diff_ns
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to peek history pose, error code: {}".format(error_code))
        return pose
    
    def peek_imu_data(self, handle, max_count=100):
        """Peek recent IMU data."""
        from .data_types import IMUData
        imu_buffer = (IMUData * max_count)()
        actual_count = ctypes.c_size_t()
        
        error_code = self.lib.slamtec_aurora_sdk_dataprovider_peek_imu_data(
            handle, imu_buffer, max_count, ctypes.byref(actual_count)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to peek IMU data, error code: {}".format(error_code))
        
        return list(imu_buffer[:actual_count.value])
    
    # CORRECTED CONTROLLER METHOD IMPLEMENTATIONS
    def set_low_rate_mode(self, handle, enable):
        """Enable/disable low rate mode - CORRECTED: no return value."""
        self.lib.slamtec_aurora_sdk_controller_set_low_rate_mode(handle, int(enable))
    
    def set_loop_closure(self, handle, enable, timeout_ms=5000):
        """Enable/disable loop closure - CORRECTED: added missing timeout_ms parameter."""
        error_code = self.lib.slamtec_aurora_sdk_controller_set_loop_closure(handle, int(enable), timeout_ms)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set loop closure, error code: {}".format(error_code))
    
    def force_map_global_optimization(self, handle, timeout_ms=30000):
        """Force global map optimization."""
        error_code = self.lib.slamtec_aurora_sdk_controller_force_map_global_optimization(handle, timeout_ms)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to force global optimization, error code: {}".format(error_code))
    
    def send_custom_command(self, handle, command_id, data=None, timeout_ms=5000):
        """Send custom command - CORRECTED: proper parameter order and types."""
        if data is None:
            data_ptr = None
            data_size = 0
        else:
            if isinstance(data, str):
                data = data.encode('utf-8')
            data_ptr = ctypes.cast(data, ctypes.c_void_p)
            data_size = len(data)
        
        # Response buffer
        response_buffer_size = 4096
        response_buffer = ctypes.create_string_buffer(response_buffer_size)
        actual_response_size = ctypes.c_size_t()
        
        error_code = self.lib.slamtec_aurora_sdk_controller_send_custom_command(
            handle, timeout_ms, command_id, data_ptr, data_size,
            ctypes.cast(response_buffer, ctypes.c_void_p), response_buffer_size,
            ctypes.byref(actual_response_size)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to send custom command, error code: {}".format(error_code))
        
        return response_buffer.raw[:actual_response_size.value]


# Global instance
_c_bindings = None

def get_c_bindings():
    """Get global C bindings instance."""
    global _c_bindings
    if _c_bindings is None:
        _c_bindings = CBindings()
    return _c_bindings