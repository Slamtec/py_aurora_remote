# SLAMTEC Aurora Remote SDK in Python

[English](README.md) | [中文](README.zh-CN.md) | [📖 API Documentation](docs/index.md) | [📓 Interactive Tutorials](notebooks/README.md)

This is a Python implementation of the SLAMTEC Aurora Remote SDK which is based on the Aurora SDK for C++. It provides comprehensive Python bindings for Aurora's 3D SLAM device including pose tracking, camera preview, LiDAR scanning, semantic segmentation, and advanced mapping capabilities.

## Features

### Core Capabilities
- **Real-time Pose Tracking**: 6DOF pose estimation with SE3 and Euler formats, including nanosecond timestamps
- **Camera Preview**: Stereo camera frames with calibration support
- **LiDAR Scanning**: Point cloud data acquisition and processing
- **Map Management**: VSLAM map creation, saving, and loading
- **2D Grid Mapping**: LIDAR-based occupancy grid mapping with real-time preview

### SDK 2.0 Enhanced Features
- **Semantic Segmentation**: Real-time scene understanding with multiple models and timestamp correlation
- **Unified ImageFrame Interface**: Single interface supporting regular images, depth maps, and point clouds
- **Depth Camera**: Dense depth maps with rectified image correlation and proper data conversion
- **Floor Detection**: Automatic multi-floor detection and management
- **Enhanced Imaging**: Advanced computer vision processing pipeline with cross-modal alignment
- **IMU Integration**: Inertial measurement unit data for robust tracking
- **Timestamp-based Data Retrieval**: Precise temporal correlation between sensor modalities

### Python Ecosystem Integration
- **NumPy/OpenCV**: Efficient image and point cloud processing
- **Open3D**: Advanced 3D visualization and point cloud operations
- **Scientific Computing**: Seamless integration with Python data science stack

## Requirements

The Aurora Python SDK has minimal core dependencies, with additional packages needed for demos and development:

### Core Requirements
- Python 3.7 or higher
- NumPy >= 1.19.0

### Requirements Files
- **requirements.txt** - Minimal dependencies for SDK core functionality
- **requirements-demo.txt** - Additional packages for running demos and Jupyter notebooks
- **requirements-dev.txt** - Development tools for building packages and documentation

```bash
# Basic SDK usage
pip install -r requirements.txt

# Running demos and notebooks
pip install -r requirements-demo.txt

# Development and package building
pip install -r requirements-dev.txt
```

## Installation

The SLAMTEC Aurora Python SDK supports three distinct usage models to accommodate different development workflows:

### Usage Model 1: Package Installation (Recommended for End Users)

Build and install the platform-specific wheel package for your system:

```bash
# Clone the repository with submodules (cpp_sdk is a git submodule)
git clone --recursive https://github.com/Slamtec/py_aurora_remote.git
cd py_aurora_remote

# Install build dependencies required for wheel generation
pip install -r requirements-dev.txt

# Build wheel packages for all platforms (wheels are not included in repo)
python tools/build_package.py --all-platforms --clean

# Install the appropriate wheel for your platform
# Linux x86_64:
pip install wheels/slamtec_aurora_python_sdk_linux_x86_64-2.0.0a0-py3-none-any.whl

# Linux ARM64:
pip install wheels/slamtec_aurora_python_sdk_linux_aarch64-2.0.0a0-py3-none-any.whl

# macOS ARM64 (Apple Silicon):
pip install wheels/slamtec_aurora_python_sdk_macos_arm64-2.0.0a0-py3-none-any.whl

# Windows x64:
pip install wheels/slamtec_aurora_python_sdk_win64-2.0.0a0-py3-none-any.whl
```

**Sample Commands:**
```bash
# Run examples using installed package (auto-discovery)
python examples/simple_pose.py
python examples/camera_preview.py
python examples/semantic_segmentation.py --device 192.168.1.212

# Verify installation
python -c "import slamtec_aurora_sdk; print('Aurora SDK installed successfully')"
```

### Usage Model 2: Source Development (Recommended for Developers)

Use the SDK directly from source code for development and customization:

```bash
# Clone the repository with submodules
git clone --recursive https://github.com/Slamtec/py_aurora_remote.git
cd py_aurora_remote

# Install minimal dependencies for SDK
pip install -r requirements.txt

# For running demos and notebooks, also install:
pip install -r requirements-demo.txt

# Run examples directly from source (auto-discovery)
python examples/simple_pose.py
python examples/device_info_monitor.py --device 192.168.1.212
```

**Sample Commands:**
```bash
# Development workflow
cd Aurora-Remote-Python-SDK

# Run any example (fallback to source automatically)
python examples/lidar_scan_plot.py 192.168.1.212
python examples/dense_point_cloud.py --device 192.168.1.212 --headless
python examples/semantic_segmentation.py --device auto

# Build your own wheels during development
python tools/build_package.py --platforms linux_x86_64
```

### Usage Model 3: Custom Build (Advanced Users)

Build platform-specific wheel packages from source:

```bash
# Clone and setup with submodules
git clone --recursive https://github.com/Slamtec/py_aurora_remote.git
cd py_aurora_remote

# Build wheels for specific platforms
python tools/build_package.py --platforms linux_x86_64 linux_aarch64 macos_arm64 macos_x86_64 win64

# Built wheels will be available in ./wheels/ directory
ls -la wheels/

# Install your custom-built wheel
pip install wheels/slamtec_aurora_python_sdk_linux_x86_64-2.0.0a0-py3-none-any.whl
```

**Sample Commands:**
```bash
# Build all supported platforms
python tools/build_package.py --all-platforms --clean

# Build and test specific platform
python tools/build_package.py --platforms linux_x86_64 --test

# Build current platform only
python tools/build_package.py --clean
```

### Dependencies

**Core Requirements (automatically installed with wheels):**
```bash
pip install numpy>=1.19.0
```

**For Advanced Demos and Visualization:**
```bash
pip install opencv-python open3d matplotlib plotly dash
```

**Development Requirements:**
```bash
pip install -r python_bindings/requirements-dev.txt
```

### Smart Import System

All examples automatically detect your usage model:

- **With installed package**: Direct import, no warnings
- **Source development**: Falls back to source with informative warning
- **No configuration needed**: Examples work in any scenario

```bash
# Example output with installed package
$ python examples/simple_pose.py --help
usage: simple_pose.py [-h] [connection_string]

# Example output using source fallback  
$ python examples/simple_pose.py --help
Warning: Aurora SDK package not found, using source code from parent directory
usage: simple_pose.py [-h] [connection_string]
```

## Recent Improvements (SDK 2.0)

### Enhanced ImageFrame Interface
- **Unified Data Handling**: Single `ImageFrame` class now supports regular images, depth maps, and point clouds
- **Depth Map Processing**: Direct conversion from depth data to numpy arrays and colorized visualizations
- **Point Cloud Support**: Built-in methods for point3d data handling and Open3D integration

### Timestamp-based Data Correlation
- **Camera Preview**: `get_camera_preview()` now accepts `timestamp_ns` and `allow_nearest_frame` parameters
- **Cross-modal Alignment**: Precise temporal correlation between depth, segmentation, and camera data
- **Enhanced Imaging**: All enhanced imaging operations support timestamp-based retrieval

### Improved Examples and Notebooks
- **Updated Interface**: All examples now use the unified ImageFrame interface
- **Better Error Handling**: Improved error reporting and graceful fallbacks
- **Depth Map Conversion**: Examples demonstrate proper depth-to-point-cloud conversion
- **Timestamp Correlation**: Semantic segmentation examples show proper camera preview correlation
- **Named Constants**: Eliminated magic numbers with proper depth camera frame type constants

## Quick Start

### Basic Device Connection

```python
from slamtec_aurora_sdk import AuroraSDK

# Create SDK instance and connect to device
sdk = AuroraSDK()  # Session created automatically

# Auto-discover and connect to first device
devices = sdk.discover_devices()
if devices:
    sdk.connect(device_info=devices[0])
    
    # Get current pose with timestamp
    position, rotation, timestamp = sdk.data_provider.get_current_pose()
    print(f"Position: {position}")
    print(f"Rotation: {rotation}")
    print(f"Timestamp: {timestamp} ns")
    
    sdk.disconnect()
    sdk.release()
```

### Context Manager (Recommended)

```python
from slamtec_aurora_sdk import AuroraSDK

# Automatic cleanup with context manager (recommended)
with AuroraSDK() as sdk:  # Session created automatically
    sdk.connect(connection_string="192.168.1.212")
    
    # Get current pose with timestamp
    position, rotation, timestamp = sdk.data_provider.get_current_pose()
    print(f"Position: {position}")
    print(f"Rotation: {rotation}")
    print(f"Timestamp: {timestamp} ns")
    
    # Automatic disconnect() and release() on exit
```

### Component-Based Architecture

```python
# Direct component access for advanced features
sdk = AuroraSDK()  # Session created automatically
sdk.connect(connection_string="192.168.1.212")

# VSLAM operations via MapManager
sdk.map_manager.save_vslam_map("my_map.vslam")
sdk.controller.require_relocalization()

# 2D LIDAR mapping via LIDAR2DMapBuilder
sdk.lidar_2d_map_builder.start_lidar_2d_map_preview()
preview_img = sdk.lidar_2d_map_builder.get_lidar_2d_map_preview()

# Enhanced imaging operations (unified ImageFrame interface)
depth_frame = sdk.enhanced_imaging.peek_depth_camera_frame(
    frame_type=DEPTHCAM_FRAME_TYPE_DEPTH_MAP
)  # Returns ImageFrame with depth map
point_cloud_frame = sdk.enhanced_imaging.peek_depth_camera_frame(
    frame_type=DEPTHCAM_FRAME_TYPE_POINT3D  
)  # Returns ImageFrame with point3d data
seg_frame = sdk.enhanced_imaging.peek_semantic_segmentation_frame()  # Returns ImageFrame

# Timestamp-correlated camera preview
if seg_frame:
    left_img, right_img = sdk.data_provider.get_camera_preview(
        seg_frame.timestamp_ns, allow_nearest_frame=False
    )
```

## Interactive Tutorials

The SDK includes comprehensive **Jupyter notebook tutorials** that provide step-by-step guidance through all Aurora features:

### 📓 [Interactive Tutorials](notebooks/README.md) | [中文教程](notebooks/README.zh-CN.md)

- **[Getting Started](notebooks/01_getting_started.ipynb)** - SDK basics and device connection
- **[Camera and Images](notebooks/02_camera_and_images.ipynb)** - Stereo camera operations and image processing
- **[VSLAM Mapping](notebooks/03_vslam_mapping_and_tracking.ipynb)** - 3D visual SLAM and map management
- **[Enhanced Imaging](notebooks/04_enhanced_imaging.ipynb)** - AI-powered depth sensing and semantic segmentation
- **[Advanced Enhanced Imaging](notebooks/05_advanced_enhanced_imaging.ipynb)** - Advanced computer vision workflows
- **[2D LiDAR Mapping](notebooks/06_lidar_2d_mapping.ipynb)** - 2D occupancy mapping and floor detection

**Quick Start with Tutorials:**
```bash
# Install demo and notebook requirements
pip install -r requirements-demo.txt

# Launch Jupyter in the notebooks directory
cd notebooks/
jupyter notebook

# Open any tutorial and follow along interactively!
```

## Examples and Demos

The SDK also includes standalone example scripts demonstrating all features:

**Note**: All demos support auto-discovery. The `[device_ip]` parameter is optional - if not provided, the demo will automatically discover and connect to the first available Aurora device.

### Core Functionality
1. **Simple Pose** - Basic pose data acquisition
   ```bash
   python examples/simple_pose.py [device_ip]
   ```

2. **Camera Preview** - Stereo camera display with calibration
   ```bash
   python examples/camera_preview.py [device_ip]
   ```

3. **Frame Preview** - Tracking frames with keypoints visualization
   ```bash
   python examples/frame_preview.py [device_ip]
   ```

4. **LiDAR Scan Plot** - Real-time LiDAR data visualization
   ```bash
   python examples/lidar_scan_plot.py [device_ip]
   ```

5. **LiDAR Scan Plot Vector** - Vector-based LiDAR visualization
   ```bash
   python examples/lidar_scan_plot_vector.py [device_ip]
   ```

### Advanced SDK 2.0 Features
6. **Semantic Segmentation** - Real-time scene understanding with timestamp correlation
   ```bash
   python examples/semantic_segmentation.py [--device device_ip] [--headless]
   ```

7. **Dense Point Cloud** - 3D visualization with unified ImageFrame interface
   ```bash
   python examples/dense_point_cloud.py [--device device_ip] [--headless] [options]
   ```

8. **Depth Camera Preview** - Enhanced imaging with proper depth map handling
   ```bash
   python examples/depthcam_preview.py [--device device_ip] [options]
   ```

9. **IMU Data Fetcher** - Inertial measurement unit data
   ```bash
   python examples/imu_fetcher.py [device_ip]
   ```

### Map and Calibration
10. **Map Render** - VSLAM map visualization
    ```bash
    python examples/map_render.py [device_ip]
    ```

11. **Simple Map Render** - Basic VSLAM map display
    ```bash
    python examples/simple_map_render.py [device_ip]
    ```

12. **Simple Map Snapshot** - Save map snapshot
    ```bash
    python examples/simple_map_snapshot.py [device_ip]
    ```

13. **Vector Map Render** - Vector-based map visualization
    ```bash
    python examples/vector_map_render.py [device_ip]
    ```

14. **VSLAM Map Save/Load** - Map persistence operations
    ```bash
    python examples/vslam_map_saveload.py [device_ip]
    ```

15. **Selective Map Data Fetch** - Optimized map data retrieval
    ```bash
    python examples/selective_map_data_fetch.py [device_ip] [--fetch-kf] [--fetch-mp] [--fetch-mapinfo]
    ```

16. **2D LIDAR Map Render** - Occupancy grid mapping
    ```bash
    python examples/lidar_2dmap_render.py [device_ip]
    ```

17. **2D LIDAR Map Save** - Save 2D map to file
    ```bash
    python examples/lidar_2dmap_save.py [device_ip]
    ```

18. **Relocalization** - Device relocalization demo
    ```bash
    python examples/relocalization.py [device_ip]
    ```

19. **Calibration Exporter** - Camera and transform calibration
    ```bash
    python examples/calibration_exporter.py [--device device_ip] [--output file] [options]
    ```

### Utility and Testing
20. **Device Info Monitor** - Device status and capabilities
    ```bash
    python examples/device_info_monitor.py [--device device_ip] [options]
    ```

21. **Context Manager Demo** - Automatic resource cleanup
    ```bash
    python examples/context_manager_demo.py [device_ip]
    ```

22. **IMU Fetcher** - IMU data acquisition
    ```bash
    python examples/imu_fetcher.py [device_ip]
    ```

23. **Depth Camera Preview** - Depth sensor visualization
    ```bash
    python examples/depthcam_preview.py [--device device_ip] [--headless]
    ```


## Architecture

### Component-Based Design

The Python SDK follows the same component-based architecture as the C++ SDK:

```
AuroraSDK
├── Controller          # Device connection and control
├── DataProvider        # Data acquisition (pose, images, scans)
├── MapManager          # VSLAM map operations
├── LIDAR2DMapBuilder   # 2D occupancy grid mapping
├── EnhancedImaging     # Depth camera and semantic segmentation
└── FloorDetector       # Multi-floor detection
```

## API Reference

### Core Classes

#### **AuroraSDK**
Main SDK interface providing component access and convenience methods.

```python
class AuroraSDK:
    # Session management (automatic)
    def release() -> None
    
    # Connection management
    def discover_devices(timeout: float = 10.0) -> List[Dict]
    def connect(device_info: Dict = None, connection_string: str = None) -> None
    def disconnect() -> None
    def is_connected() -> bool
    
    # Context manager support (automatic cleanup)
    def __enter__(self) -> AuroraSDK
    def __exit__(self, exc_type, exc_val, exc_tb) -> None
    def __del__(self) -> None  # Automatic cleanup on garbage collection
    
    # Component access
    @property
    def controller(self) -> Controller
    @property  
    def data_provider(self) -> DataProvider
    @property
    def map_manager(self) -> MapManager
    @property
    def lidar_2d_map_builder(self) -> LIDAR2DMapBuilder
    @property
    def enhanced_imaging(self) -> EnhancedImaging
    @property
    def floor_detector(self) -> FloorDetector
```

#### **Controller**
Device connection and control operations.

```python
class Controller:
    def require_relocalization(timeout_ms: int = 5000) -> None
    def cancel_relocalization() -> None
    def require_mapping_mode(timeout_ms: int = 10000) -> None
    def enable_raw_data_subscription(enable: bool) -> None
    def enable_map_data_syncing(enable: bool) -> None
```

#### **DataProvider**
Data acquisition and sensor access.

```python
class DataProvider:
    # Pose data (returns position, rotation, timestamp)
    def get_current_pose(use_se3: bool = True) -> Tuple[Tuple[float, float, float], Tuple[float, float, float, float], int]
    
    # Camera data with timestamp correlation support
    def get_camera_preview(timestamp_ns: int = 0, allow_nearest_frame: bool = True) -> Tuple[ImageFrame, ImageFrame]
    def get_tracking_frame() -> TrackingFrame
    
    # LiDAR data
    def get_recent_lidar_scan(max_points: int = 8192) -> Optional[LidarScanData]
    
    # IMU data
    def peek_imu_data(max_count: int = 100) -> List[IMUData]
    
    # Device info
    def get_last_device_basic_info() -> DeviceBasicInfoWrapper
    def get_camera_calibration() -> CameraCalibrationInfo
    def get_transform_calibration() -> TransformCalibrationInfo
    
    # Map data with enhanced metadata (SDK 2.0)
    def get_global_mapping_info() -> Dict
    def get_map_data(map_ids: Optional[List[int]] = None, 
                     fetch_kf: bool = True, 
                     fetch_mp: bool = True, 
                     fetch_mapinfo: bool = False,
                     kf_fetch_flags: Optional[int] = None,
                     mp_fetch_flags: Optional[int] = None) -> Dict
```

### Enhanced VSLAM Map Data (SDK 2.0)

The `get_map_data()` method returns comprehensive VSLAM mapping information including map points, keyframes, and loop closures with full metadata. **New in v2.0.0**: Selective data fetching for optimized performance.

```python
# Get map data from active map (default)
map_data = sdk.data_provider.get_map_data()

# Get map data from all maps
map_data = sdk.data_provider.get_map_data(map_ids=[])

# Get map data from specific maps
map_data = sdk.data_provider.get_map_data(map_ids=[1, 2, 3])

# Selective data fetching (new in v2.0.0) - fetch only what you need
# Fetch only keyframes (trajectory data)
map_data = sdk.data_provider.get_map_data(fetch_kf=True, fetch_mp=False, fetch_mapinfo=False)

# Fetch only map points (3D point cloud)
map_data = sdk.data_provider.get_map_data(fetch_kf=False, fetch_mp=True, fetch_mapinfo=False)

# Fetch only map metadata (no actual data, very fast)
map_data = sdk.data_provider.get_map_data(fetch_kf=False, fetch_mp=False, fetch_mapinfo=True)

# Map data structure
{
    'map_points': [
        {
            'position': (x, y, z),      # 3D position coordinates
            'id': int,                  # Unique map point ID
            'map_id': int,             # Map ID this point belongs to
            'timestamp': float         # Creation timestamp
        },
        # ... more map points
    ],
    'keyframes': [
        {
            'position': (x, y, z),      # 3D position coordinates  
            'rotation': (qx, qy, qz, qw), # Quaternion rotation
            'id': int,                  # Unique keyframe ID
            'map_id': int,             # Map ID this keyframe belongs to
            'timestamp': float,        # Creation timestamp
            'fixed': bool              # True if keyframe is fixed (not optimizable)
        },
        # ... more keyframes
    ],
    'loop_closures': [
        (from_keyframe_id, to_keyframe_id),  # Loop closure connections
        # ... more loop closures
    ],
    'map_info': {               # Available when fetch_mapinfo=True
        0: {                    # Map ID as key
            'id': 0,
            'point_count': 17028,
            'keyframe_count': 459,
            'map_flags': 0,
            'keyframe_id_start': 0,
            'keyframe_id_end': 701,
            'map_point_id_start': 0,
            'map_point_id_end': 102789
        },
        # ... more maps
    }
}
```

#### **EnhancedImaging**
SDK 2.0 advanced imaging capabilities with unified ImageFrame interface.

```python
class EnhancedImaging:
    # Depth camera (returns unified ImageFrame)
    def peek_depth_camera_frame(frame_type: int = DEPTHCAM_FRAME_TYPE_DEPTH_MAP, 
                                timestamp_ns: int = 0, 
                                allow_nearest_frame: bool = True) -> ImageFrame
    def peek_depth_camera_related_rectified_image(timestamp_ns: int) -> ImageFrame
    def is_depth_camera_ready() -> bool
    def wait_depth_camera_next_frame(timeout_ms: int) -> bool
    
    # Semantic segmentation (returns unified ImageFrame)
    def peek_semantic_segmentation_frame(timestamp_ns: int = 0, 
                                        allow_nearest_frame: bool = True) -> ImageFrame
    def get_semantic_segmentation_config() -> SemanticSegmentationConfig
    def get_semantic_segmentation_labels() -> SemanticSegmentationLabelInfo
    def get_semantic_segmentation_label_set_name() -> str
    def is_semantic_segmentation_ready() -> bool
    def wait_semantic_segmentation_next_frame(timeout_ms: int) -> bool
    
    # Cross-modal alignment operations
    def calc_depth_camera_aligned_segmentation_map(seg_frame: ImageFrame) -> Tuple[bytes, int, int]
```

### Data Types

#### **ImageFrame**
Unified image data container supporting regular images, depth maps, and enhanced imaging data.

```python
class ImageFrame:
    @property
    def width(self) -> int
    def height(self) -> int  
    def format(self) -> int
    def data(self) -> bytes
    def timestamp_ns(self) -> int
    
    # Image conversion methods
    def to_opencv_image(self) -> numpy.ndarray
    def has_image_data(self) -> bool
    
    # Depth data support (SDK 2.0)
    def is_depth_frame(self) -> bool
    def to_numpy_depth_map(self) -> numpy.ndarray
    def to_colorized_depth_map(self, colormap=None) -> numpy.ndarray
    
    # Point cloud support (SDK 2.0)
    def is_point3d_frame(self) -> bool
    def to_point3d_array(self) -> numpy.ndarray
    def to_point_cloud_data(self) -> Tuple[numpy.ndarray, numpy.ndarray]
```

#### **Depth Camera Frame Type Constants**
Constants for specifying depth camera frame format.

```python
# Available frame types for peek_depth_camera_frame()
DEPTHCAM_FRAME_TYPE_DEPTH_MAP = 0    # Float32 depth map data
DEPTHCAM_FRAME_TYPE_POINT3D = 1      # 3D point cloud data (x,y,z)

# Usage example
from slamtec_aurora_sdk import DEPTHCAM_FRAME_TYPE_DEPTH_MAP, DEPTHCAM_FRAME_TYPE_POINT3D

# Get depth map
depth_frame = sdk.enhanced_imaging.peek_depth_camera_frame(DEPTHCAM_FRAME_TYPE_DEPTH_MAP)
depth_map = depth_frame.to_numpy_depth_map()

# Get point cloud
point_frame = sdk.enhanced_imaging.peek_depth_camera_frame(DEPTHCAM_FRAME_TYPE_POINT3D)
points_xyz = point_frame.to_point3d_array()
```

#### **IMUData**
Inertial measurement unit data.

```python
class IMUData:
    @property
    def timestamp_ns(self) -> int
    def imu_id(self) -> int
    def acc(self) -> ctypes.Array[ctypes.c_double]  # [x, y, z] acceleration
    def gyro(self) -> ctypes.Array[ctypes.c_double]  # [x, y, z] gyroscope
    
    def get_acceleration(self) -> Tuple[float, float, float]
    def get_gyroscope(self) -> Tuple[float, float, float]
    def get_timestamp_seconds(self) -> float
```

#### **LidarScanData**
LiDAR point cloud data.

```python
class LidarScanData:
    @property
    def scan_count(self) -> int
    def timestamp_ns(self) -> int
    def points(self) -> List[Tuple[float, float, float]]
    
    def to_numpy(self) -> numpy.ndarray
    def to_open3d(self) -> open3d.geometry.PointCloud
```

### Error Handling

The SDK uses specific exception hierarchy for different error conditions:

```python
# Base exceptions
class AuroraSDKError(Exception): pass
class ConnectionError(AuroraSDKError): pass
class DataNotReadyError(AuroraSDKError): pass

# Usage example
try:
    pose = sdk.data_provider.get_current_pose()
except ConnectionError:
    print("Device not connected")
except DataNotReadyError:
    print("Pose data not ready yet")
except AuroraSDKError as e:
    print(f"SDK error: {e}")
```

## Advanced Usage

### Real-time Data Processing

```python
import time
from slamtec_aurora_sdk import AuroraSDK, DataNotReadyError

# Real-time pose tracking with automatic cleanup
with AuroraSDK() as sdk:  # Session created automatically
    sdk.connect(connection_string="192.168.1.212")
    
    while True:
        try:
            position, rotation, timestamp = sdk.data_provider.get_current_pose()
            print(f"Position: {position} (timestamp: {timestamp} ns)")
            
            # IMU data
            imu_samples = sdk.data_provider.peek_imu_data(max_count=10)
            if imu_samples:
                latest_imu = imu_samples[-1]
                accel = latest_imu.get_acceleration()
                print(f"Acceleration: {accel}")
                
        except DataNotReadyError:
            pass  # Data not available yet
        except KeyboardInterrupt:
            break
            
        time.sleep(0.1)  # 10 Hz loop
        
# Automatic cleanup happens here
```

### Enhanced Imaging Pipeline

```python
# Semantic segmentation with depth alignment using unified ImageFrame interface
from slamtec_aurora_sdk import (
    ENHANCED_IMAGE_TYPE_DEPTH, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION,
    DEPTHCAM_FRAME_TYPE_DEPTH_MAP, DEPTHCAM_FRAME_TYPE_POINT3D
)

sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_DEPTH, True)
sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, True)

while True:
    try:
        # Wait for semantic segmentation frame
        if sdk.enhanced_imaging.wait_semantic_segmentation_next_frame(1000):
            # Get semantic segmentation frame (unified ImageFrame)
            seg_frame = sdk.enhanced_imaging.peek_semantic_segmentation_frame()
            
            if seg_frame:
                # Get timestamp-correlated camera preview for overlay
                left_img, right_img = sdk.data_provider.get_camera_preview(
                    seg_frame.timestamp_ns, allow_nearest_frame=False
                )
                
                # Get depth frame using proper constants
                depth_frame = sdk.enhanced_imaging.peek_depth_camera_frame(
                    frame_type=DEPTHCAM_FRAME_TYPE_DEPTH_MAP,
                    timestamp_ns=seg_frame.timestamp_ns
                )
                
                # Get depth-aligned version
                aligned_data, width, height = sdk.enhanced_imaging.calc_depth_camera_aligned_segmentation_map(seg_frame)
                
                # Process aligned segmentation data
                seg_image = np.frombuffer(aligned_data, dtype=np.uint8).reshape((height, width))
        
    except DataNotReadyError:
        time.sleep(0.01)
```

### 2D LIDAR Mapping

```python
from slamtec_aurora_sdk.data_types import GridMapGenerationOptions

# Configure 2D map generation
options = GridMapGenerationOptions()
options.resolution = 0.05  # 5cm resolution
options.width = 100.0  # 100m x 100m map
options.height = 100.0

# Start background map generation
sdk.lidar_2d_map_builder.start_lidar_2d_map_preview(options)

try:
    while True:
        # Check if map data is available
        if sdk.lidar_2d_map_builder.is_background_updating():
            # Get map preview
            gridmap_handle = sdk.lidar_2d_map_builder.get_lidar_2d_map_preview_handle()
            
            if gridmap_handle:
                dimension = sdk.lidar_2d_map_builder.get_gridmap_dimension(gridmap_handle)
                print(f"Map size: {dimension.width}x{dimension.height} cells")
                
        time.sleep(1.0)
        
finally:
    sdk.lidar_2d_map_builder.stop_lidar_2d_map_preview()
```

## Folder Structure

```bash
Aurora-Remote-Python-SDK/
├── cpp_sdk/                    # C++ SDK and demos
│   ├── aurora_remote_public/   # C++ SDK library and headers
│   └── demo/                   # C++ demo applications
├── python_bindings/            # Python SDK implementation
│   ├── slamtec_aurora_sdk/     # Core Python package
│   │   ├── __init__.py         # Package initialization
│   │   ├── aurora_sdk.py       # Main SDK class
│   │   ├── controller.py       # Controller component
│   │   ├── data_provider.py    # DataProvider component
│   │   ├── data_types.py       # Data structures and types
│   │   ├── c_bindings.py       # Low-level C API bindings
│   │   └── exceptions.py       # Exception definitions
│   └── examples/               # Python demo applications
├── README.md                   # This documentation
└── setup.py                   # Package installation script
```

## Platform Support

### Supported Platforms

- **Linux**: x86_64, ARM64 (aarch64)
- **macOS**: ARM64 (Apple Silicon), x86_64 (Intel)
- **Windows**: x64
- **Python**: 3.6+ (tested with 3.8, 3.9, 3.10, 3.11, 3.12)

### Platform-Specific Notes

#### **macOS**
- **Native Backend Support**: Uses native macOS backends for matplotlib visualization
- **Library Loading**: Automatic detection and loading of `.dylib` files
- **Consistent Naming**: Both `--all-platforms` and single-platform builds use consistent `macos_*` wheel naming

#### **Windows** 
- **Backend Compatibility**: Automatic fallback to compatible matplotlib backends
- **Library Loading**: Automatic detection and loading of `.dll` files  
- **Build System**: Consistent `win64` platform naming across build tools

#### **Linux**
- **Multi-Architecture**: Full support for both x86_64 and ARM64 architectures
- **Library Loading**: Automatic detection and loading of `.so` files
- **Packaging**: Separate wheels for each architecture for optimal compatibility

## Troubleshooting

### Common Issues

1. **"Aurora SDK library not found"**
   - Ensure the correct platform-specific wheel is installed (check wheel naming: `macos_*`, `win64`, `linux_*`)
   - Verify C++ SDK library is in the correct location for your platform
   - Check platform-specific library paths in installation

2. **Connection timeout**
   - Verify device IP address and network connectivity
   - Check that Aurora device is powered on and in correct mode

3. **Data not ready errors**
   - These are normal during device startup
   - Implement retry logic with appropriate delays

4. **Memory errors with large point clouds**
   - Reduce max_points parameter in LiDAR functions
   - Process data in smaller batches

5. **Matplotlib backend issues on macOS**
   - Modern versions automatically select compatible backends
   - Install GUI backend if needed: `pip install PyQt5` or `pip install tkinter`

6. **Inconsistent wheel naming**
   - Fixed in SDK 2.0: All builds now use consistent platform naming
   - `macos_arm64`/`macos_x86_64` (not `darwin_*`)
   - `win64` (consistent across all build modes)

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

sdk = AuroraSDK()
# Debug output will show detailed SDK operations
```

## Contributing

For bug reports, feature requests, or contributions, please contact SLAMTEC support or refer to the official documentation.

## License

Copyright (c) SLAMTEC Co., Ltd. All rights reserved.

