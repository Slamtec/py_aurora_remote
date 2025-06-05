# Aurora Python SDK Tutorials

This folder contains comprehensive Jupyter notebooks that provide step-by-step tutorials for using the SLAMTEC Aurora Python SDK. These interactive tutorials are designed to help you understand and use all aspects of the Aurora SDK effectively.

## 📚 Tutorial Series

### Getting Started
- **[01_getting_started.ipynb](01_getting_started.ipynb)** - Essential basics
  - SDK installation and imports
  - Device discovery and connection
  - Basic pose data retrieval
  - Proper resource management
  - Context manager usage

### Core Features
- **[02_camera_and_images.ipynb](02_camera_and_images.ipynb)** - Camera and image processing
  - Stereo camera preview
  - Tracking frames with keypoints
  - Image format conversion
  - Camera calibration data
  - Real-time image capture

- **[03_vslam_mapping_and_tracking.ipynb](03_vslam_mapping_and_tracking.ipynb)** - VSLAM and 3D mapping
  - Visual SLAM operations
  - 3D map point visualization
  - Keyframe trajectory tracking
  - Real-time pose estimation
  - Map data management

### Advanced Features
- **[04_enhanced_imaging.ipynb](04_enhanced_imaging.ipynb)** - AI-powered imaging
  - Depth camera operations
  - Semantic segmentation
  - Point cloud generation from depth
  - Multi-modal sensor fusion
  - Advanced computer vision

- **[05_advanced_enhanced_imaging.ipynb](05_advanced_enhanced_imaging.ipynb)** - Advanced imaging techniques
  - Dense point cloud processing
  - Semantic analysis and visualization
  - 3D reconstruction workflows
  - Cross-modal data correlation
  - Performance optimization

- **[06_lidar_2d_mapping.ipynb](06_lidar_2d_mapping.ipynb)** - 2D LiDAR mapping and floor detection
  - Real-time LiDAR scan visualization
  - 2D occupancy grid mapping
  - Automatic floor detection system
  - Multi-floor environment analysis
  - Navigation-ready map generation

## 🚀 Quick Start

### Prerequisites

1. **Aurora Device**: Connected to your network
2. **Python Environment**: Python 3.6+ with Aurora SDK installed
3. **Dependencies**: Install required packages for visualization

```bash
# Essential dependencies
pip install numpy matplotlib

# Optional but recommended for 3D visualization
pip install open3d

# Optional for advanced analysis
pip install scipy scikit-learn
```

### Running the Tutorials

1. **Start Jupyter**:
   ```bash
   jupyter notebook
   # or
   jupyter lab
   ```

2. **Navigate** to the notebooks folder

3. **Open a tutorial** and follow along step-by-step

4. **Modify the device IP** in the connection cells to match your Aurora device

### Device Configuration

Before running the tutorials, ensure your Aurora device is:

- **Powered on** and fully initialized
- **Connected to the same network** as your computer
- **Not being used** by other applications
- **In the correct mode** for the features you want to test

## 📖 Tutorial Learning Path

### Beginner Path
1. Start with **Getting Started** to understand the basics
2. Try **Camera and Images** to see visual data
3. Explore **VSLAM Mapping** for 3D understanding

### Advanced Path
1. Complete the beginner path first
2. Dive into **Enhanced Imaging** for AI-powered computer vision
3. Master **Advanced Enhanced Imaging** for complex workflows
4. Explore **2D LiDAR Mapping** for navigation applications

## 🔧 Customization

Each notebook is designed to be:

- **Self-contained**: Can be run independently
- **Modifiable**: Easy to adapt for your specific needs
- **Well-documented**: Extensive comments and explanations
- **Interactive**: Encourages experimentation

### Adapting for Your Use Case

```python
# Example: Modify connection parameters
device_ip = "YOUR_DEVICE_IP_HERE"  # Change this

# Example: Adjust processing parameters
max_points = 4096  # Reduce for faster processing
update_rate = 10   # Hz, adjust based on your needs

# Example: Enable/disable visualizations
SHOW_PLOTS = True  # Set to False for headless operation
```

## 🎯 Learning Objectives

After completing these tutorials, you will be able to:

### Basic Skills
- ✅ Connect to Aurora devices reliably
- ✅ Retrieve pose, camera, and LiDAR data
- ✅ Handle common errors and edge cases
- ✅ Manage resources properly

### Intermediate Skills
- ✅ Process and visualize sensor data
- ✅ Implement real-time monitoring
- ✅ Perform basic computer vision tasks
- ✅ Work with 3D point clouds

### Advanced Skills
- ✅ Build SLAM applications
- ✅ Integrate multiple sensor modalities
- ✅ Optimize performance for production
- ✅ Create custom processing pipelines

## 🛠️ Development Environment

### Recommended Setup

```bash
# Create a virtual environment
python -m venv aurora_tutorials
source aurora_tutorials/bin/activate  # Linux/Mac
# or
aurora_tutorials\Scripts\activate     # Windows

# Install dependencies
pip install numpy matplotlib open3d scipy jupyter

# Install Aurora SDK (adjust path as needed)
pip install path/to/aurora_sdk_wheel.whl
```

### VS Code Integration

If you prefer VS Code:

1. Install the **Jupyter extension**
2. Open the notebooks folder in VS Code
3. Select your Python interpreter with Aurora SDK
4. Run cells interactively

## 📊 Troubleshooting

### Common Issues

**Connection Problems:**
```python
# Check device IP and network
ping 192.168.1.212

# Verify Aurora SDK installation
import slamtec_aurora_sdk
print("SDK imported successfully")
```

**Visualization Issues:**
```python
# For Jupyter display problems
%matplotlib inline

# For Open3D in remote environments
# Use headless mode and save point clouds to files
```

**Performance Issues:**
```python
# Reduce point cloud size
scan_data = sdk.get_recent_lidar_scan(max_points=2048)

# Lower update rates
time.sleep(0.2)  # 5Hz instead of 10Hz
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your Aurora SDK code here
```

## 🤝 Contributing

Found an issue or want to improve the tutorials?

1. **Report bugs** via GitHub issues
2. **Suggest improvements** for clarity or content
3. **Share your use cases** to inspire new tutorials
4. **Contribute examples** for specific applications

### Tutorial Guidelines

When creating new tutorials:

- **Start simple** and build complexity gradually
- **Include error handling** examples
- **Provide clear explanations** for each step
- **Add visualizations** where helpful
- **Test thoroughly** with different devices

## 📚 Additional Resources

- **[API Documentation](../docs/index.md)** - Complete SDK reference
- **[Examples](../examples/)** - Standalone example scripts
- **[Main README](../README.md)** - Project overview and installation
- **SLAMTEC Documentation** - Official device manuals

## 💡 Tips for Success

1. **Start with simulation** if you don't have a device yet
2. **Read error messages carefully** - they often contain helpful hints
3. **Experiment with parameters** to understand their effects
4. **Use version control** to track your modifications
5. **Share your findings** with the community

---

*Happy learning! These tutorials will help you master the Aurora Python SDK and build amazing robotic applications.* 🚀