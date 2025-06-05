# Aurora Python SDK 教程

该文件夹包含全面的 Jupyter 笔记本教程，提供使用 SLAMTEC Aurora Python SDK 的分步指导。这些交互式教程旨在帮助您有效地理解和使用 Aurora SDK 的所有方面。

## 📚 教程系列

### 入门指南
- **[01_getting_started.ipynb](01_getting_started.ipynb)** - 基础必备知识
  - SDK 安装和导入
  - 设备发现和连接
  - 基本姿态数据获取
  - 正确的资源管理
  - 上下文管理器使用

### 核心功能
- **[02_camera_and_images.ipynb](02_camera_and_images.ipynb)** - 相机和图像处理
  - 双目相机预览
  - 带关键点的跟踪帧
  - 图像格式转换
  - 相机标定数据
  - 实时图像捕获

- **[03_vslam_mapping_and_tracking.ipynb](03_vslam_mapping_and_tracking.ipynb)** - VSLAM 和 3D 建图
  - 视觉 SLAM 操作
  - 3D 地图点可视化
  - 关键帧轨迹跟踪
  - 实时姿态估计
  - 地图数据管理

### 高级功能
- **[04_enhanced_imaging.ipynb](04_enhanced_imaging.ipynb)** - AI 驱动的成像
  - 深度相机操作
  - 语义分割
  - 从深度生成点云
  - 多模态传感器融合
  - 高级计算机视觉

- **[05_advanced_enhanced_imaging.ipynb](05_advanced_enhanced_imaging.ipynb)** - 高级成像技术
  - 密集点云处理
  - 语义分析和可视化
  - 3D 重建工作流
  - 跨模态数据关联
  - 性能优化

- **[06_lidar_2d_mapping.ipynb](06_lidar_2d_mapping.ipynb)** - 2D LiDAR 建图和楼层检测
  - 实时 LiDAR 扫描可视化
  - 2D 占用栅格建图
  - 自动楼层检测系统
  - 多楼层环境分析
  - 导航就绪地图生成

## 🚀 快速开始

### 先决条件

1. **Aurora 设备**：连接到您的网络
2. **Python 环境**：已安装 Aurora SDK 的 Python 3.6+
3. **依赖项**：安装可视化所需的包

```bash
# 必要依赖项
pip install numpy matplotlib

# 可选但推荐用于 3D 可视化
pip install open3d

# 可选用于高级分析
pip install scipy scikit-learn
```

### 运行教程

1. **启动 Jupyter**：
   ```bash
   jupyter notebook
   # 或
   jupyter lab
   ```

2. **导航** 到 notebooks 文件夹

3. **打开教程** 并按步骤进行

4. **修改设备 IP** 在连接单元格中匹配您的 Aurora 设备

### 设备配置

运行教程前，确保您的 Aurora 设备：

- **已开机** 并完全初始化
- **连接到同一网络** 与您的计算机
- **未被其他应用程序使用**
- **处于正确模式** 用于您要测试的功能

## 📖 教程学习路径

### 初学者路径
1. 从 **入门指南** 开始了解基础知识
2. 尝试 **相机和图像** 查看视觉数据
3. 探索 **VSLAM 建图** 进行 3D 理解

### 高级路径
1. 首先完成初学者路径
2. 深入 **增强成像** 进行 AI 驱动的计算机视觉
3. 掌握 **高级增强成像** 进行复杂工作流
4. 探索 **2D LiDAR 建图** 进行导航应用

## 🔧 自定义

每个笔记本都设计为：

- **自包含**：可以独立运行
- **可修改**：易于适应您的特定需求
- **充分文档化**：广泛的注释和解释
- **交互式**：鼓励实验

### 适应您的用例

```python
# 示例：修改连接参数
device_ip = "YOUR_DEVICE_IP_HERE"  # 更改此项

# 示例：调整处理参数
max_points = 4096  # 减少以加快处理速度
update_rate = 10   # Hz，根据您的需要调整

# 示例：启用/禁用可视化
SHOW_PLOTS = True  # 设置为 False 进行无头操作
```

## 🎯 学习目标

完成这些教程后，您将能够：

### 基本技能
- ✅ 可靠地连接到 Aurora 设备
- ✅ 获取姿态、相机和 LiDAR 数据
- ✅ 处理常见错误和边缘情况
- ✅ 正确管理资源

### 中级技能
- ✅ 处理和可视化传感器数据
- ✅ 实现实时监控
- ✅ 执行基本计算机视觉任务
- ✅ 处理 3D 点云

### 高级技能
- ✅ 构建 SLAM 应用程序
- ✅ 集成多种传感器模态
- ✅ 优化生产性能
- ✅ 创建自定义处理管道

## 🛠️ 开发环境

### 推荐设置

```bash
# 创建虚拟环境
python -m venv aurora_tutorials
source aurora_tutorials/bin/activate  # Linux/Mac
# 或
aurora_tutorials\Scripts\activate     # Windows

# 安装依赖项
pip install numpy matplotlib open3d scipy jupyter

# 安装 Aurora SDK（根据需要调整路径）
pip install path/to/aurora_sdk_wheel.whl
```

### VS Code 集成

如果您偏好 VS Code：

1. 安装 **Jupyter 扩展**
2. 在 VS Code 中打开 notebooks 文件夹
3. 选择带有 Aurora SDK 的 Python 解释器
4. 交互式运行单元格

## 📊 故障排除

### 常见问题

**连接问题：**
```python
# 检查设备 IP 和网络
ping 192.168.1.212

# 验证 Aurora SDK 安装
import slamtec_aurora_sdk
print("SDK 导入成功")
```

**可视化问题：**
```python
# 针对 Jupyter 显示问题
%matplotlib inline

# 针对远程环境中的 Open3D
# 使用无头模式并将点云保存到文件
```

**性能问题：**
```python
# 减少点云大小
scan_data = sdk.get_recent_lidar_scan(max_points=2048)

# 降低更新率
time.sleep(0.2)  # 5Hz 而不是 10Hz
```

### 调试模式

启用详细日志记录进行故障排除：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 您的 Aurora SDK 代码在此
```

## 🤝 贡献

发现问题或想改进教程？

1. **通过 GitHub issues 报告错误**
2. **建议改进** 以提高清晰度或内容
3. **分享您的用例** 以启发新教程
4. **贡献示例** 用于特定应用

### 教程指南

创建新教程时：

- **从简单开始** 逐步构建复杂性
- **包含错误处理** 示例
- **为每个步骤提供清晰解释**
- **在有帮助的地方添加可视化**
- **使用不同设备彻底测试**

## 📚 其他资源

- **[API 文档](../docs/index.md)** - 完整的 SDK 参考
- **[示例](../examples/)** - 独立示例脚本
- **[主 README](../README.md)** - 项目概述和安装
- **SLAMTEC 文档** - 官方设备手册

## 💡 成功提示

1. **如果您还没有设备，请从仿真开始**
2. **仔细阅读错误消息** - 它们通常包含有用的提示
3. **尝试参数** 以了解它们的效果
4. **使用版本控制** 跟踪您的修改
5. **与社区分享您的发现**

---

*愉快学习！这些教程将帮助您掌握 Aurora Python SDK 并构建令人惊叹的机器人应用程序。* 🚀