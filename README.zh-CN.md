# SLAMTEC Aurora Remote SDK Python版

[English](README.md) | [中文](README.zh-CN.md) | [📖 API文档](docs/index.md) | [📓 教程](notebooks/README.zh-CN.md)

这是基于Aurora C++ SDK的SLAMTEC Aurora Remote SDK Python实现。它为Aurora 3D SLAM设备提供了全面的Python绑定，包括位姿跟踪、相机预览、激光雷达扫描、语义分割和高级建图功能。

## 功能特性

### 核心功能
- **实时位姿跟踪**：支持SE3和欧拉角格式的6DOF位姿估计
- **相机预览**：支持校准的双目相机帧显示
- **激光雷达扫描**：点云数据采集和处理
- **地图管理**：VSLAM地图创建、保存和加载
- **2D网格建图**：基于激光雷达的占用网格建图和实时预览

### SDK 2.0增强功能
- **语义分割**：基于多种模型的实时场景理解
- **深度相机**：支持校正图像关联的密集深度图
- **楼层检测**：自动多楼层检测和管理
- **增强成像**：先进的计算机视觉处理管道
- **IMU集成**：惯性测量单元数据用于鲁棒跟踪

### Python生态系统集成
- **NumPy/OpenCV**：高效的图像和点云处理
- **Open3D**：先进的3D可视化和点云操作
- **科学计算**：与Python数据科学栈无缝集成

## 安装

SLAMTEC Aurora Python SDK支持三种不同的使用模式，以适应不同的开发工作流程：

### 使用模式1：包安装（推荐给最终用户）

构建并安装适合您系统的平台特定wheel包：

```bash
# 克隆包含子模块的仓库（cpp_sdk是git子模块）
git clone --recursive https://github.com/Slamtec/py_aurora_remote.git
cd py_aurora_remote

# 安装wheel生成所需的构建依赖
pip install -r requirements-dev.txt

# 构建所有平台的wheel包（wheel不包含在仓库中）
python tools/build_package.py --all-platforms --clean

# 安装适合您平台的wheel包
# Linux x86_64:
pip install wheels/slamtec_aurora_python_sdk_linux_x86_64-2.0.0a0-py3-none-any.whl

# Linux ARM64:
pip install wheels/slamtec_aurora_python_sdk_linux_aarch64-2.0.0a0-py3-none-any.whl

# macOS ARM64 (Apple Silicon):
pip install wheels/slamtec_aurora_python_sdk_macos_arm64-2.0.0a0-py3-none-any.whl

# Windows x64:
pip install wheels/slamtec_aurora_python_sdk_win64-2.0.0a0-py3-none-any.whl
```

**示例命令：**
```bash
# 使用已安装的包运行示例（自动发现）
python examples/simple_pose.py
python examples/camera_preview.py
python examples/semantic_segmentation.py --device 192.168.1.212

# 验证安装
python -c "import slamtec_aurora_sdk; print('Aurora SDK安装成功')"
```

### 使用模式2：源码开发（推荐给开发者）

直接从源码使用SDK进行开发和定制：

```bash
# 克隆包含子模块的仓库
git clone --recursive https://github.com/Slamtec/py_aurora_remote.git
cd py_aurora_remote

# 安装依赖
pip install -r python_bindings/requirements.txt

# 直接从源码运行示例（自动发现）
python examples/simple_pose.py
python examples/device_info_monitor.py --device 192.168.1.212
```

**示例命令：**
```bash
# 开发工作流程
cd Aurora-Remote-Python-SDK

# 运行任何示例（自动回退到源码）
python examples/lidar_scan_plot.py 192.168.1.212
python examples/dense_point_cloud.py --device 192.168.1.212 --headless
python examples/semantic_segmentation.py --device auto

# 在开发过程中构建自己的wheel包
python tools/build_package.py --platforms linux_x86_64
```

### 使用模式3：自定义构建（高级用户）

从源码构建平台特定的wheel包：

```bash
# 克隆和设置包含子模块
git clone --recursive https://github.com/Slamtec/py_aurora_remote.git
cd py_aurora_remote

# 为特定平台构建wheel包
python tools/build_package.py --platforms linux_x86_64 linux_aarch64 macos_arm64 macos_x86_64 win64

# 构建的wheel包将在./wheels/目录中可用
ls -la wheels/

# 安装您自定义构建的wheel包
pip install wheels/slamtec_aurora_python_sdk_linux_x86_64-2.0.0a0-py3-none-any.whl
```

**示例命令：**
```bash
# 构建所有支持的平台
python tools/build_package.py --all-platforms --clean

# 构建并测试特定平台
python tools/build_package.py --platforms linux_x86_64 --test

# 仅构建当前平台
python tools/build_package.py --clean
```

### 依赖项

**核心要求（wheel包会自动安装）：**
```bash
pip install numpy>=1.19.0
```

**高级演示和可视化：**
```bash
pip install opencv-python open3d matplotlib plotly dash
```

**开发要求：**
```bash
pip install -r python_bindings/requirements-dev.txt
```

### 智能导入系统

所有示例都会自动检测您的使用模式：

- **已安装包**：直接导入，无警告
- **源码开发**：回退到源码并显示信息提示
- **无需配置**：示例在任何场景下都能工作

```bash
# 使用已安装包的示例输出
$ python examples/simple_pose.py --help
usage: simple_pose.py [-h] [connection_string]

# 使用源码回退的示例输出
$ python examples/simple_pose.py --help
Warning: Aurora SDK package not found, using source code from parent directory
usage: simple_pose.py [-h] [connection_string]
```

## 快速开始

### 基本设备连接

```python
from slamtec_aurora_sdk import AuroraSDK

# 创建SDK实例并连接到设备
sdk = AuroraSDK()  # 会话自动创建

# 自动发现并连接到第一个设备
devices = sdk.discover_devices()
if devices:
    sdk.connect(device_info=devices[0])
    
    # 获取当前位姿和时间戳
    position, rotation, timestamp = sdk.data_provider.get_current_pose()
    print(f"位置: {position}")
    print(f"旋转: {rotation}")
    print(f"时间戳: {timestamp} ns")
    
    sdk.disconnect()
    sdk.release()
```

### 上下文管理器（推荐）

```python
from slamtec_aurora_sdk import AuroraSDK

# 使用上下文管理器自动清理（推荐）
with AuroraSDK() as sdk:  # 会话自动创建
    sdk.connect(connection_string="192.168.1.212")
    
    # 获取当前位姿和时间戳
    position, rotation, timestamp = sdk.data_provider.get_current_pose()
    print(f"位置: {position}")
    print(f"旋转: {rotation}")
    print(f"时间戳: {timestamp} ns")
    
    # 退出时自动调用disconnect()和release()
```

### 基于组件的架构

```python
# 直接访问组件以使用高级功能
sdk = AuroraSDK()  # 会话自动创建
sdk.connect(connection_string="192.168.1.212")

# 通过MapManager进行VSLAM操作
sdk.map_manager.save_vslam_map("my_map.vslam")
sdk.controller.require_relocalization()

# 通过LIDAR2DMapBuilder进行2D激光雷达建图
sdk.lidar_2d_map_builder.start_lidar_2d_map_preview()
preview_img = sdk.lidar_2d_map_builder.get_lidar_2d_map_preview()

# 增强成像操作
sdk.enhanced_imaging.peek_depth_camera_frame()
seg_frame = sdk.enhanced_imaging.peek_semantic_segmentation_frame()
```

## 交互式教程

SDK包含全面的**Jupyter笔记本教程**，提供所有Aurora功能的分步指导：

### 📓 [交互式教程](notebooks/README.md) | [中文教程](notebooks/README.zh-CN.md)

- **[入门指南](notebooks/01_getting_started.ipynb)** - SDK基础知识和设备连接
- **[相机和图像](notebooks/02_camera_and_images.ipynb)** - 双目相机操作和图像处理
- **[VSLAM建图](notebooks/03_vslam_mapping_and_tracking.ipynb)** - 3D视觉SLAM和地图管理
- **[增强成像](notebooks/04_enhanced_imaging.ipynb)** - AI驱动的深度感知和语义分割
- **[高级增强成像](notebooks/05_advanced_enhanced_imaging.ipynb)** - 高级计算机视觉工作流程
- **[2D激光雷达建图](notebooks/06_lidar_2d_mapping.ipynb)** - 2D占用建图和楼层检测

**教程快速开始：**
```bash
# 安装Jupyter和所需包
pip install jupyter matplotlib numpy open3d

# 在notebooks目录中启动Jupyter
cd notebooks/
jupyter notebook

# 打开任何教程并交互式跟随！
```

## 示例和演示

SDK包含展示所有功能的全面示例：

**注意**：所有演示都支持自动发现。`[device_ip]`参数是可选的 - 如果不提供，演示将自动发现并连接到第一个可用的Aurora设备。

### 核心功能
1. **简单位姿** - 基本位姿数据获取
   ```bash
   python examples/simple_pose.py [device_ip]
   ```

2. **相机预览** - 带校准的双目相机显示
   ```bash
   python examples/camera_preview.py [device_ip]
   ```

3. **帧预览** - 带关键点可视化的跟踪帧
   ```bash
   python examples/frame_preview.py [device_ip]
   ```

4. **激光雷达扫描绘图** - 实时激光雷达数据可视化
   ```bash
   python examples/lidar_scan_plot.py [device_ip]
   ```

5. **激光雷达扫描矢量绘图** - 基于矢量的激光雷达可视化
   ```bash
   python examples/lidar_scan_plot_vector.py [device_ip]
   ```

### 高级SDK 2.0功能
6. **语义分割** - 实时场景理解
   ```bash
   python examples/semantic_segmentation.py [--device device_ip] [--headless]
   ```

7. **密集点云** - 使用Open3D的3D可视化
   ```bash
   python examples/dense_point_cloud.py [--device device_ip] [--headless] [options]
   ```

8. **深度相机预览** - 增强成像深度图
   ```bash
   python examples/depthcam_preview.py [--device device_ip] [options]
   ```

9. **IMU数据获取器** - 惯性测量单元数据
   ```bash
   python examples/imu_fetcher.py [device_ip]
   ```

### 地图和校准
10. **地图渲染** - VSLAM地图可视化
    ```bash
    python examples/map_render.py [device_ip]
    ```

11. **简单地图渲染** - 基本VSLAM地图显示
    ```bash
    python examples/simple_map_render.py [device_ip]
    ```

12. **简单地图快照** - 保存地图快照
    ```bash
    python examples/simple_map_snapshot.py [device_ip]
    ```

13. **矢量地图渲染** - 基于矢量的地图可视化
    ```bash
    python examples/vector_map_render.py [device_ip]
    ```

14. **VSLAM地图保存/加载** - 地图持久化操作
    ```bash
    python examples/vslam_map_saveload.py [device_ip]
    ```

15. **2D激光雷达地图渲染** - 占用网格建图
    ```bash
    python examples/lidar_2dmap_render.py [device_ip]
    ```

16. **2D激光雷达地图保存** - 将2D地图保存到文件
    ```bash
    python examples/lidar_2dmap_save.py [device_ip]
    ```

17. **重定位** - 设备重定位演示
    ```bash
    python examples/relocalization.py [device_ip]
    ```

18. **校准导出器** - 相机和变换校准
    ```bash
    python examples/calibration_exporter.py [--device device_ip] [--output file] [options]
    ```

### 实用工具和测试
19. **设备信息监视器** - 设备状态和功能
    ```bash
    python examples/device_info_monitor.py [--device device_ip] [options]
    ```

20. **上下文管理器演示** - 自动资源清理
    ```bash
    python examples/context_manager_demo.py [device_ip]
    ```

## 架构

### 基于组件的设计

Python SDK遵循与C++ SDK相同的基于组件的架构：

```
AuroraSDK
├── Controller          # 设备连接和控制
├── DataProvider        # 数据获取（位姿、图像、扫描）
├── MapManager          # VSLAM地图操作
├── LIDAR2DMapBuilder   # 2D占用网格建图
├── EnhancedImaging     # 深度相机和语义分割
└── FloorDetector       # 多楼层检测
```

## API参考

### 核心类

#### **AuroraSDK**
提供组件访问和便利方法的主要SDK接口。

```python
class AuroraSDK:
    # 会话管理（自动）
    def release() -> None
    
    # 连接管理
    def discover_devices(timeout: float = 10.0) -> List[Dict]
    def connect(device_info: Dict = None, connection_string: str = None) -> None
    def disconnect() -> None
    def is_connected() -> bool
    
    # 上下文管理器支持（自动清理）
    def __enter__(self) -> AuroraSDK
    def __exit__(self, exc_type, exc_val, exc_tb) -> None
    def __del__(self) -> None  # 垃圾回收时自动清理
    
    # 组件访问
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
设备连接和控制操作。

```python
class Controller:
    def require_relocalization(timeout_ms: int = 5000) -> None
    def cancel_relocalization() -> None
    def require_mapping_mode(timeout_ms: int = 10000) -> None
    def enable_raw_data_subscription(enable: bool) -> None
    def enable_map_data_syncing(enable: bool) -> None
```

#### **DataProvider**
数据获取和传感器访问。

```python
class DataProvider:
    # 位姿数据（返回位置、旋转、时间戳）
    def get_current_pose(use_se3: bool = True) -> Tuple[Tuple[float, float, float], Tuple[float, float, float, float], int]
    
    # 相机数据
    def get_camera_preview() -> Tuple[ImageFrame, ImageFrame]
    def get_tracking_frame() -> TrackingFrame
    
    # 激光雷达数据
    def get_recent_lidar_scan(max_points: int = 8192) -> Optional[LidarScanData]
    
    # IMU数据
    def peek_imu_data(max_count: int = 100) -> List[IMUData]
    
    # 设备信息
    def get_last_device_basic_info() -> DeviceBasicInfoWrapper
    def get_camera_calibration() -> CameraCalibrationInfo
    def get_transform_calibration() -> TransformCalibrationInfo
    
    # 地图数据
    def get_global_mapping_info() -> Dict
    def get_map_data() -> Dict
```

#### **EnhancedImaging**
SDK 2.0高级成像功能。

```python
class EnhancedImaging:
    # 深度相机
    def peek_depth_camera_frame() -> DepthCameraFrame
    def peek_depth_camera_related_rectified_image(timestamp: int) -> ImageFrame
    def is_depth_camera_ready() -> bool
    def wait_depth_camera_next_frame(timeout_ms: int) -> bool
    
    # 语义分割
    def peek_semantic_segmentation_frame() -> ImageFrame
    def get_semantic_segmentation_config() -> SemanticSegmentationConfig
    def get_semantic_segmentation_labels() -> SemanticSegmentationLabelInfo
    def get_semantic_segmentation_label_set_name() -> str
    def is_semantic_segmentation_ready() -> bool
    def wait_semantic_segmentation_next_frame(timeout_ms: int) -> bool
    
    # 对齐操作
    def calc_depth_camera_aligned_segmentation_map(seg_frame: ImageFrame) -> Tuple[bytes, int, int]
```

### 数据类型

#### **ImageFrame**
带元数据的相机图像数据容器。

```python
class ImageFrame:
    @property
    def width(self) -> int
    def height(self) -> int  
    def format(self) -> int
    def data(self) -> bytes
    def timestamp_ns(self) -> int
    
    def to_opencv(self) -> numpy.ndarray
    def to_pil(self) -> PIL.Image.Image
```

#### **IMUData**
惯性测量单元数据。

```python
class IMUData:
    @property
    def timestamp_ns(self) -> int
    def imu_id(self) -> int
    def acc(self) -> ctypes.Array[ctypes.c_double]  # [x, y, z] 加速度
    def gyro(self) -> ctypes.Array[ctypes.c_double]  # [x, y, z] 陀螺仪
    
    def get_acceleration(self) -> Tuple[float, float, float]
    def get_gyroscope(self) -> Tuple[float, float, float]
    def get_timestamp_seconds(self) -> float
```

#### **LidarScanData**
激光雷达点云数据。

```python
class LidarScanData:
    @property
    def scan_count(self) -> int
    def timestamp_ns(self) -> int
    def points(self) -> List[Tuple[float, float, float]]
    
    def to_numpy(self) -> numpy.ndarray
    def to_open3d(self) -> open3d.geometry.PointCloud
```

### 错误处理

SDK针对不同错误条件使用特定的异常层次结构：

```python
# 基础异常
class AuroraSDKError(Exception): pass
class ConnectionError(AuroraSDKError): pass
class DataNotReadyError(AuroraSDKError): pass

# 使用示例
try:
    pose = sdk.data_provider.get_current_pose()
except ConnectionError:
    print("设备未连接")
except DataNotReadyError:
    print("位姿数据尚未准备好")
except AuroraSDKError as e:
    print(f"SDK错误: {e}")
```

## 高级用法

### 实时数据处理

```python
import time
from slamtec_aurora_sdk import AuroraSDK, DataNotReadyError

# 带自动清理的实时位姿跟踪
with AuroraSDK() as sdk:  # 会话自动创建
    sdk.connect(connection_string="192.168.1.212")
    
    while True:
        try:
            position, rotation, timestamp = sdk.data_provider.get_current_pose()
            print(f"位置: {position} (时间戳: {timestamp} ns)")
            
            # IMU数据
            imu_samples = sdk.data_provider.peek_imu_data(max_count=10)
            if imu_samples:
                latest_imu = imu_samples[-1]
                accel = latest_imu.get_acceleration()
                print(f"加速度: {accel}")
                
        except DataNotReadyError:
            pass  # 数据尚未可用
        except KeyboardInterrupt:
            break
            
        time.sleep(0.1)  # 10 Hz循环
        
# 自动清理在这里发生
```

### 增强成像管道

```python
# 带深度对齐的语义分割
from slamtec_aurora_sdk import ENHANCED_IMAGE_TYPE_DEPTH, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION

sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_DEPTH, True)
sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, True)

while True:
    try:
        # 等待语义分割帧
        if sdk.enhanced_imaging.wait_semantic_segmentation_next_frame(1000):
            # 获取语义分割
            seg_frame = sdk.enhanced_imaging.peek_semantic_segmentation_frame()
            
            if seg_frame:
                # 获取深度对齐版本
                aligned_data, width, height = sdk.enhanced_imaging.calc_depth_camera_aligned_segmentation_map(seg_frame)
                
                # 处理对齐的分割数据
                seg_image = np.frombuffer(aligned_data, dtype=np.uint8).reshape((height, width))
        
    except DataNotReadyError:
        time.sleep(0.01)
```

### 2D激光雷达建图

```python
from slamtec_aurora_sdk.data_types import GridMapGenerationOptions

# 配置2D地图生成
options = GridMapGenerationOptions()
options.resolution = 0.05  # 5cm分辨率
options.width = 100.0  # 100m x 100m地图
options.height = 100.0

# 启动后台地图生成
sdk.lidar_2d_map_builder.start_lidar_2d_map_preview(options)

try:
    while True:
        # 检查地图数据是否可用
        if sdk.lidar_2d_map_builder.is_background_updating():
            # 获取地图预览
            gridmap_handle = sdk.lidar_2d_map_builder.get_lidar_2d_map_preview_handle()
            
            if gridmap_handle:
                dimension = sdk.lidar_2d_map_builder.get_gridmap_dimension(gridmap_handle)
                print(f"地图大小: {dimension.width}x{dimension.height} 个单元格")
                
        time.sleep(1.0)
        
finally:
    sdk.lidar_2d_map_builder.stop_lidar_2d_map_preview()
```

## 文件夹结构

```bash
Aurora-Remote-Python-SDK/
├── cpp_sdk/                    # C++ SDK和演示
│   ├── aurora_remote_public/   # C++ SDK库和头文件
│   └── demo/                   # C++演示应用程序
├── python_bindings/            # Python SDK实现
│   ├── slamtec_aurora_sdk/     # 核心Python包
│   │   ├── __init__.py         # 包初始化
│   │   ├── aurora_sdk.py       # 主SDK类
│   │   ├── controller.py       # Controller组件
│   │   ├── data_provider.py    # DataProvider组件
│   │   ├── data_types.py       # 数据结构和类型
│   │   ├── c_bindings.py       # 低级C API绑定
│   │   └── exceptions.py       # 异常定义
│   └── examples/               # Python演示应用程序
├── README.md                   # 本文档
└── setup.py                   # 包安装脚本
```

## 平台支持

### 支持的平台

- **Linux**: x86_64, ARM64 (aarch64)
- **macOS**: ARM64 (Apple Silicon), x86_64 (Intel)
- **Windows**: x64
- **Python**: 3.6+ (已在3.8、3.9、3.10、3.11、3.12上测试)

### 平台特定说明

#### **macOS**
- **原生后端支持**：使用原生macOS后端进行matplotlib可视化
- **库加载**：自动检测和加载`.dylib`文件
- **一致命名**：`--all-platforms`和单平台构建都使用一致的`macos_*`wheel命名

#### **Windows** 
- **后端兼容性**：自动回退到兼容的matplotlib后端
- **库加载**：自动检测和加载`.dll`文件  
- **构建系统**：在构建工具中使用一致的`win64`平台命名

#### **Linux**
- **多架构**：完全支持x86_64和ARM64架构
- **库加载**：自动检测和加载`.so`文件
- **包装**：为每个架构提供单独的wheel包以获得最佳兼容性

## 故障排除

### 常见问题

1. **"Aurora SDK library not found"**
   - 确保安装了正确的平台特定wheel包（检查wheel命名：`macos_*`、`win64`、`linux_*`）
   - 验证C++ SDK库在您平台的正确位置
   - 检查安装中的平台特定库路径

2. **连接超时**
   - 验证设备IP地址和网络连接
   - 检查Aurora设备是否已开机且处于正确模式

3. **数据未准备好错误**
   - 这在设备启动期间是正常的
   - 实现带适当延迟的重试逻辑

4. **大点云的内存错误**
   - 减少激光雷达函数中的max_points参数
   - 以更小的批次处理数据

5. **macOS上的Matplotlib后端问题**
   - 现代版本会自动选择兼容的后端
   - 如需要，安装GUI后端：`pip install PyQt5`或`pip install tkinter`

6. **不一致的wheel命名**
   - 在SDK 2.0中已修复：所有构建现在使用一致的平台命名
   - `macos_arm64`/`macos_x86_64`（不是`darwin_*`）
   - `win64`（在所有构建模式中保持一致）

### 调试模式

启用调试日志记录进行故障排除：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

sdk = AuroraSDK()
# 调试输出将显示详细的SDK操作
```

## 贡献

如需错误报告、功能请求或贡献，请联系SLAMTEC支持或参考官方文档。

## 许可证

版权所有 (c) SLAMTEC Co., Ltd. 保留所有权利。