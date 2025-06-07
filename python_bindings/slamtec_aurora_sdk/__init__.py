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

# Data types and exceptions
from .data_types import *
from .exceptions import *

__version__ = "2.0.0"
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
    
    # Exceptions
    'AuroraSDKError',
    'ConnectionError',
    'DataNotReadyError',
    
    # Data types
    'Pose',
    'PoseSE3', 
    'DeviceInfo',
    'ImageFrame',
    'TrackingFrame',
    'ScanData',
    
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
    'DeviceBasicInfo'
]