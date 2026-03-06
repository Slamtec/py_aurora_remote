# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/__init__.py
#  *
#  */
"""
SLAMTEC Aurora Remote SDK Python Bindings

This package provides Python bindings for the SLAMTEC Aurora Remote SDK,
enabling Python applications to communicate with Aurora devices and
retrieve pose, image, and map data.

Architecture:
- Component-based design following C++ SDK patterns
- Controller: Device connection and control
- DataProvider: Data retrieval operations  
- MapManager: VSLAM (3D mapping) operations
- LIDAR2DMapBuilder: CoMap (2D LIDAR mapping) operations
"""

# Component-based SDK with convenience methods
from .aurora_sdk import AuroraSDK

# Components (for advanced users who want direct access)
from .controller import Controller
from .data_provider import DataProvider
from .map_manager import MapManager
from .lidar_2d_map_builder import LIDAR2DMapBuilder
from .enhanced_imaging import EnhancedImaging
from .data_recorder import DataRecorder
from .persistent_config import ConfigData, PersistentConfigManager
from .transform_manager import TransformManager
from .camera_mask import CameraMaskManager
from .dashcam_recorder import DashcamRecorderManager, DashcamStorageInfo
from .listener import SDKListener
from .timesync import TimeSyncClient

# Data types and exceptions
from .data_types import *
from .exceptions import *

__version__ = "2.1.1"
__author__ = "SLAMTEC Co., Ltd."

__all__ = [
    # Main SDK class
    'AuroraSDK',           # Component-based SDK with convenience methods

    # Components (for advanced usage)
    'Controller',
    'DataProvider',
    'MapManager',
    'LIDAR2DMapBuilder',
    'EnhancedImaging',
    'DataRecorder',
    'PersistentConfigManager',
    'TransformManager',
    'CameraMaskManager',
    'DashcamRecorderManager',
    'TimeSyncClient',
    'SDKListener',
    'ConfigData',
    'DashcamStorageInfo',

    # Exceptions
    'AuroraSDKError',
    'ConnectionError',
    'DataNotReadyError',
    
    # Data types
    'Pose',
    'PoseSE3',
    'PoseCovariance',
    'PoseCovarianceReadable',
    'PoseAugmentationConfig',
    'DeviceInfo',
    'ImageFrame',
    'TrackingFrame',
    'ScanData',
    'DashcamStatus',
    'DashcamStorageStatus',
    'DashcamSessionInfo',
    'TimeSyncOptions',
    'TimeSyncQuality',
    'WallclockOffsetResult',
    'WallclockSyncResult',
    'WallclockAccuracyResult',
    
    # Enhanced Imaging data types (SDK 2.0)
    'SemanticSegmentationFrame',
    'CameraCalibrationInfo',
    'TransformCalibrationInfo',
    
    # Enhanced Image Type Constants
    'ENHANCED_IMAGE_TYPE_DEPTH',
    'ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION',
    
    # Depth Camera Frame Type Constants
    'DEPTHCAM_FRAME_TYPE_DEPTH_MAP',
    'DEPTHCAM_FRAME_TYPE_POINT3D',
    
    # Device capability checking (SDK 2.0)
    'DeviceBasicInfo',

    # Session configuration
    'SESSION_FLAG_DEFAULT',
    'SESSION_FLAG_NO_PREVIEW_IMAGE_SUBSCRIPTION',

    # Pose augmentation
    'POSE_AUGMENTATION_MODE_VISUAL_ONLY',
    'POSE_AUGMENTATION_MODE_IMU_VISION_MIXED',
    'POSE_OUTPUT_FREQ_HIGHEST_POSSIBLE',
    'POSE_OUTPUT_FREQ_50HZ',
    'POSE_OUTPUT_FREQ_100HZ',
    'POSE_OUTPUT_FREQ_200HZ',

    # Power operations
    'POWER_OP_REBOOT',
    'POWER_OP_SHUTDOWN',

    # Time synchronization
    'TIMESYNC_DEFAULT_PORT',
    'TIMESYNC_DOMAIN_STEADY_CLOCK',
    'TIMESYNC_DOMAIN_WALL_CLOCK',
]
