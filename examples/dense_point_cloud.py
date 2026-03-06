#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/dense_point_cloud.py
#  *
#  */
"""
SLAMTEC Aurora Python SDK Demo - Dense Point Cloud Visualization

This demo shows how to visualize a dense 3D point cloud from the Aurora device
in real-time using Open3D.
"""

import sys
import os
import time
import signal
import argparse
import threading

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, ENHANCED_IMAGE_TYPE_DEPTH, DEPTHCAM_FRAME_TYPE_POINT3D, DEPTHCAM_FRAME_TYPE_DEPTH_MAP, AuroraSDKError)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import (
            AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, ENHANCED_IMAGE_TYPE_DEPTH,
            DEPTHCAM_FRAME_TYPE_POINT3D, DEPTHCAM_FRAME_TYPE_DEPTH_MAP
        )
        from slamtec_aurora_sdk.exceptions import AuroraSDKError
        return AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, ENHANCED_IMAGE_TYPE_DEPTH, DEPTHCAM_FRAME_TYPE_POINT3D, DEPTHCAM_FRAME_TYPE_DEPTH_MAP, AuroraSDKError
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import (
            AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, ENHANCED_IMAGE_TYPE_DEPTH,
            DEPTHCAM_FRAME_TYPE_POINT3D, DEPTHCAM_FRAME_TYPE_DEPTH_MAP
        )
        from slamtec_aurora_sdk.exceptions import AuroraSDKError
        return AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, ENHANCED_IMAGE_TYPE_DEPTH, DEPTHCAM_FRAME_TYPE_POINT3D, DEPTHCAM_FRAME_TYPE_DEPTH_MAP, AuroraSDKError

# Setup SDK import
AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, ENHANCED_IMAGE_TYPE_DEPTH, DEPTHCAM_FRAME_TYPE_POINT3D, DEPTHCAM_FRAME_TYPE_DEPTH_MAP, AuroraSDKError = setup_sdk_import()

try:
    import numpy as np
except ImportError as e:
    print("Error: NumPy not found.")
    print("Please install: pip install numpy")
    sys.exit(1)

try:
    import open3d as o3d
except ImportError as e:
    print("Error: Open3D not found.")
    print("Please install: pip install open3d")
    sys.exit(1)

# Global variables for point cloud data and visualization
is_ctrl_c = False
point_cloud_data = None
color_data = None
point_cloud_lock = threading.Lock()
debug_mode = False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    global is_ctrl_c
    print("\nCtrl-C pressed, exiting...")
    is_ctrl_c = True


def _build_strided_uint8_image(data, width, height, channels, stride=0):
    """Create a NumPy image view while honoring optional row stride."""
    if data is None:
        return None

    packed_row_bytes = width * channels
    row_stride = stride or packed_row_bytes
    required_size = packed_row_bytes + row_stride * (height - 1 if height > 1 else 0)
    if len(data) < required_size or row_stride < packed_row_bytes:
        return None

    shape = (height, width) if channels == 1 else (height, width, channels)
    strides = (row_stride, 1) if channels == 1 else (row_stride, channels, 1)
    try:
        return np.ndarray(shape=shape, dtype=np.uint8, buffer=data, strides=strides)
    except (TypeError, ValueError, BufferError):
        return None


def extract_camera_rgb_image(camera_image):
    """Convert a related rectified image into normalized RGB colors for Open3D."""
    if camera_image is None or not getattr(camera_image, 'data', None):
        return None

    if hasattr(camera_image, 'to_numpy_image'):
        img_rgb = camera_image.to_numpy_image(color_order="rgb")
        if img_rgb is not None:
            return img_rgb.astype(np.float32) / 255.0

    img_height = camera_image.height
    img_width = camera_image.width
    pixel_format = camera_image.pixel_format
    img_stride = getattr(camera_image, 'stride', 0)
    img_data = camera_image.data

    if pixel_format == 0:
        gray = _build_strided_uint8_image(img_data, img_width, img_height, 1, img_stride)
        if gray is None:
            return None
        normalized_gray = gray.astype(np.float32) / 255.0
        return np.repeat(normalized_gray[:, :, np.newaxis], 3, axis=2)

    if pixel_format == 1:
        bgr = _build_strided_uint8_image(img_data, img_width, img_height, 3, img_stride)
        if bgr is None:
            return None
        return bgr[:, :, ::-1].astype(np.float32) / 255.0

    if pixel_format == 2:
        rgba = _build_strided_uint8_image(img_data, img_width, img_height, 4, img_stride)
        if rgba is None:
            return None
        return rgba[:, :, :3].astype(np.float32) / 255.0

    return None

def parse_point_cloud_data(frame, camera_image=None, max_points=100000):
    """
    Parse 3D point cloud data from depth camera frame.
    
    Args:
        frame: ImageFrame with point3d data
        camera_image: Optional camera image for colorization
        max_points: Maximum number of points to process
        
    Returns:
        tuple: (points_xyz, colors_rgb, timestamp) or (None, None, None) if failed
    """
    if frame is None or not frame.is_point3d_frame():
        if debug_mode:
            print("No frame or not point3d data")
        return None, None, None
    
    # Get frame dimensions
    width = frame.width
    height = frame.height
    
    if debug_mode:
        print(f"Frame: {width}x{height}, data size: {len(frame.data)} bytes")
    
    # Use the new to_point3d_array method
    points_xyz = frame.to_point3d_array()
    
    if points_xyz is None:
        if debug_mode:
            print("Failed to extract point3d data")
        return None, None, None
    
    # Store original shape for organized point cloud
    original_shape = points_xyz.shape
    is_organized = (len(points_xyz) == width * height)
    
    if debug_mode:
        print(f"Point cloud organized: {is_organized} (shape: {original_shape})")
    
    # Filter out invalid points FIRST, before any sampling
    valid_mask = np.ones(len(points_xyz), dtype=bool)
    
    # Remove zero points
    zero_mask = np.all(points_xyz == 0, axis=1)
    valid_mask &= ~zero_mask
    
    # Remove points with NaN or inf
    finite_mask = np.all(np.isfinite(points_xyz), axis=1)
    valid_mask &= finite_mask
    
    # Remove points too far away (adjust threshold as needed)
    distance_mask = np.linalg.norm(points_xyz, axis=1) < 50.0  # 50 meters max
    valid_mask &= distance_mask
    
    # Remove points too close (noise near camera)
    close_mask = np.linalg.norm(points_xyz, axis=1) > 0.1  # 10cm minimum
    valid_mask &= close_mask
    
    # Store original indices for organized point cloud mapping
    original_indices = np.arange(len(points_xyz))
    valid_original_indices = original_indices[valid_mask]
    points_xyz = points_xyz[valid_mask]
    
    # NOW do sampling if needed, but preserve the original indices for color mapping
    if len(points_xyz) > max_points:
        # Random sampling to maintain spatial distribution
        sampling_indices = np.random.choice(len(points_xyz), max_points, replace=False)
        # Keep track of which original indices these correspond to
        sampled_original_indices = valid_original_indices[sampling_indices]
        points_xyz = points_xyz[sampling_indices]
        valid_original_indices = sampled_original_indices
    
    if len(points_xyz) == 0:
        if debug_mode:
            print("No valid points after filtering")
        return None, None, None
    
    if debug_mode:
        print(f"Valid points: {len(points_xyz)}")
        print(f"Point cloud bounds: X=[{points_xyz[:, 0].min():.2f}, {points_xyz[:, 0].max():.2f}], "
              f"Y=[{points_xyz[:, 1].min():.2f}, {points_xyz[:, 1].max():.2f}], "
              f"Z=[{points_xyz[:, 2].min():.2f}, {points_xyz[:, 2].max():.2f}]")
    
    # Get timestamp for camera image sync
    timestamp = frame.timestamp_ns if hasattr(frame, 'timestamp_ns') else 0
    
    # Colorization using the unified ImageFrame interface
    if camera_image is not None and hasattr(camera_image, 'data'):
        # Use camera image for colors (ImageFrame with proper data field)
        try:
            img_height = camera_image.height
            img_width = camera_image.width
            img_rgb = extract_camera_rgb_image(camera_image)
            
            if debug_mode:
                data_size = len(camera_image.data)
                pixel_format = camera_image.pixel_format
                stride = getattr(camera_image, 'stride', 0)
                print(f"Camera image: {img_width}x{img_height}, format: {pixel_format}, stride: {stride}, data size: {data_size} bytes")
            
            if img_rgb is not None:
                colors_rgb = np.zeros((len(points_xyz), 3))  # Start with black, not gray
                
                # For organized point cloud - direct 1:1 correspondence between depth and camera
                if is_organized and width == img_width and height == img_height:
                    # Direct mapping: depth point at (row,col) corresponds to camera pixel at (row,col)
                    if debug_mode:
                        print(f"Using direct 1:1 mapping: {width}x{height} depth <-> {img_width}x{img_height} camera")
                        print(f"Applying colors to {len(valid_original_indices)} valid points")
                    
                    for i, original_idx in enumerate(valid_original_indices):
                        # Convert linear index to 2D coordinates
                        row = original_idx // width
                        col = original_idx % width
                        
                        # Direct correspondence: same row, col in camera image
                        colors_rgb[i] = img_rgb[row, col]
                        
                        # Debug first few mappings
                        if debug_mode and i < 5:
                            pixel_val = img_rgb[row, col]
                            print(f"  Point {i}: depth({col},{row}) -> camera({col},{row}) = {pixel_val}")
                
                elif is_organized:
                    # Dimensions don't match exactly - use scaling
                    if debug_mode:
                        print(f"Using scaled mapping: {width}x{height} depth -> {img_width}x{img_height} camera")
                        print(f"Applying colors to {len(valid_original_indices)} valid points")
                    
                    for i, original_idx in enumerate(valid_original_indices):
                        # Convert linear index to 2D coordinates in depth frame
                        row = original_idx // width
                        col = original_idx % width
                        
                        # Scale to camera image coordinates
                        img_col = int(col * img_width / width)
                        img_row = int(row * img_height / height)
                        
                        # Ensure we're within image bounds
                        img_col = max(0, min(img_col, img_width - 1))
                        img_row = max(0, min(img_row, img_height - 1))
                        
                        colors_rgb[i] = img_rgb[img_row, img_col]
                        
                        # Debug first few mappings
                        if debug_mode and i < 5:
                            pixel_val = img_rgb[img_row, img_col]
                            print(f"  Point {i}: depth({col},{row}) -> camera({img_col},{img_row}) = {pixel_val}")
                    
                    if debug_mode:
                        print(f"Applied camera colors to {len(valid_original_indices)} valid points")
                        print(f"Color statistics after mapping:")
                        print(f"  R: [{colors_rgb[:, 0].min():.3f}, {colors_rgb[:, 0].max():.3f}], mean: {colors_rgb[:, 0].mean():.3f}")
                        print(f"  G: [{colors_rgb[:, 1].min():.3f}, {colors_rgb[:, 1].max():.3f}], mean: {colors_rgb[:, 1].mean():.3f}")
                        print(f"  B: [{colors_rgb[:, 2].min():.3f}, {colors_rgb[:, 2].max():.3f}], mean: {colors_rgb[:, 2].mean():.3f}")
                        # Check if colors are too bright (white)
                        avg_brightness = colors_rgb.mean()
                        if avg_brightness > 0.8:
                            print(f"WARNING: Colors are very bright (avg={avg_brightness:.3f}), might appear white!")
                        elif avg_brightness < 0.2:
                            print(f"WARNING: Colors are very dark (avg={avg_brightness:.3f}), might appear black!")
                else:
                    # For unorganized point cloud, use nearest neighbor or projection
                    # This is a simplified approach
                    if debug_mode:
                        print("Using height-based coloring for unorganized point cloud")
                    heights = points_xyz[:, 1]
                    height_normalized = (heights - heights.min()) / (heights.max() - heights.min() + 1e-8)
                    colors_rgb[:, 0] = height_normalized
                    colors_rgb[:, 1] = 1 - height_normalized
                    colors_rgb[:, 2] = 0.5
                
                if debug_mode:
                    print(f"Applied camera colors from {img_width}x{img_height} image")
                    
                # Ensure we have valid colors - if everything is near white/black, fall back to height coloring
                avg_brightness = colors_rgb.mean()
                if avg_brightness > 0.9 or avg_brightness < 0.1:
                    if debug_mode:
                        print(f"Colors too extreme (avg={avg_brightness:.3f}), falling back to height-based coloring")
                    # Fall back to height-based coloring
                    heights = points_xyz[:, 1]
                    height_normalized = (heights - heights.min()) / (heights.max() - heights.min() + 1e-8)
                    colors_rgb = np.zeros((len(points_xyz), 3))
                    colors_rgb[:, 0] = height_normalized * 0.8 + 0.1  # Red varies with height
                    colors_rgb[:, 1] = (1 - height_normalized) * 0.8 + 0.1  # Green inverse
                    colors_rgb[:, 2] = 0.5  # Blue constant
            else:
                if debug_mode:
                    print("Failed to convert camera image, falling back to height-based coloring")
                # Fall back to height-based coloring
                heights = points_xyz[:, 1]
                height_normalized = (heights - heights.min()) / (heights.max() - heights.min() + 1e-8)
                colors_rgb = np.zeros((len(points_xyz), 3))
                colors_rgb[:, 0] = height_normalized
                colors_rgb[:, 1] = 1 - height_normalized
                colors_rgb[:, 2] = 0.5
                if debug_mode:
                    print("Using height-based coloring (unexpected camera format)")
        except Exception as e:
            if debug_mode:
                print(f"Error applying camera colors: {e}")
            # Fall back to height-based coloring
            heights = points_xyz[:, 1]
            height_normalized = (heights - heights.min()) / (heights.max() - heights.min() + 1e-8)
            colors_rgb = np.zeros((len(points_xyz), 3))
            colors_rgb[:, 0] = height_normalized * 0.8 + 0.1  # Red varies with height (avoid pure black/white)
            colors_rgb[:, 1] = (1 - height_normalized) * 0.8 + 0.1  # Green inverse
            colors_rgb[:, 2] = 0.5  # Blue constant
    else:
        # No camera image - use height-based coloring
        if len(points_xyz) > 0:
            heights = points_xyz[:, 1]
            height_normalized = (heights - heights.min()) / (heights.max() - heights.min() + 1e-8)
            colors_rgb = np.zeros((len(points_xyz), 3))
            colors_rgb[:, 0] = height_normalized * 0.8 + 0.1  # Red varies with height (avoid pure black/white)
            colors_rgb[:, 1] = (1 - height_normalized) * 0.8 + 0.1  # Green inverse
            colors_rgb[:, 2] = 0.5  # Blue constant
        else:
            colors_rgb = np.ones((len(points_xyz), 3)) * 0.5  # Medium gray, not white
    
    return points_xyz, colors_rgb, timestamp

def point_cloud_acquisition_thread(sdk, max_points, update_rate_hz):
    """
    Background thread for acquiring point cloud data with camera image colorization.
    """
    global point_cloud_data, color_data, is_ctrl_c
    
    frame_interval = 1.0 / update_rate_hz
    last_update = 0
    frame_count = 0
    error_count = 0
    
    print(f"Point cloud acquisition started (max_points={max_points}, rate={update_rate_hz}Hz)")
    print("Attempting to use camera images for colorization...")
    
    # Wait for depth camera to be ready
    print("Waiting for depth camera to be ready...")
    ready_timeout = 50  # 5 seconds
    while not is_ctrl_c and ready_timeout > 0:
        if sdk.enhanced_imaging.is_depth_camera_ready():
            print("Depth camera is ready!")
            break
        time.sleep(0.1)
        ready_timeout -= 1
    
    if ready_timeout <= 0:
        print("Warning: Depth camera not ready after 5 seconds, continuing anyway...")

    while not is_ctrl_c:
        try:
            current_time = time.time()
            if current_time - last_update < frame_interval:
                time.sleep(0.01)
                continue
            
            # Wait for next frame to be available (following C++ demo pattern)
            if not sdk.enhanced_imaging.wait_depth_camera_next_frame(100):  # 100ms timeout
                continue
            
            # Get depth frame
            frame = sdk.enhanced_imaging.peek_depth_camera_frame(DEPTHCAM_FRAME_TYPE_POINT3D)
            
            if frame and frame.data:
                # Try to get the related camera image
                camera_image = None
                if hasattr(frame, 'timestamp_ns') and frame.timestamp_ns > 0:
                    try:
                        camera_image = sdk.enhanced_imaging.peek_depth_camera_related_rectified_image(frame.timestamp_ns)
                        if camera_image and debug_mode:
                            print(f"Got camera image: {camera_image.width}x{camera_image.height}")
                    except Exception as e:
                        if frame_count == 0:  # Only print once
                            print(f"Note: Camera image not available for colorization: {e}")
                
                # Parse point cloud data with optional camera image
                points, colors, timestamp = parse_point_cloud_data(frame, camera_image, max_points)
                
                if points is not None and colors is not None:
                    with point_cloud_lock:
                        point_cloud_data = points.copy()
                        color_data = colors.copy()
                    
                    frame_count += 1
                    last_update = current_time
                    
                    # Print statistics periodically
                    if frame_count % 30 == 0:
                        has_camera = "with camera colors" if camera_image else "with height colors"
                        print(f"Acquired {frame_count} frames, {len(points)} points {has_camera}")
                else:
                    error_count += 1
                    if error_count % 50 == 0:
                        print(f"Warning: Failed to parse {error_count} frames")
            
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            
        except Exception as e:
            error_count += 1
            # Check if it's a NOT_READY error (error code -7)
            if "error code: -7" in str(e) or "NOT_READY" in str(e):
                # This is normal - depth camera data not ready yet
                if error_count == 1:
                    print("Waiting for depth camera data to become available...")
                time.sleep(0.1)  # Wait a bit longer for data to be ready
            else:
                # Other errors - print less frequently
                if error_count % 10 == 0:
                    print(f"Acquisition error: {e}")
                time.sleep(0.1)

def create_open3d_visualization(window_name="Aurora Dense Point Cloud", use_software_render=False):
    """
    Create Open3D visualization window.
    """
    try:
        if use_software_render:
            print("Using software rendering mode")
            os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
            
        # Create visualizer
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=window_name, width=1024, height=768)
        
        # Create initial point cloud geometry
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.array([[0, 0, 0]]))  # Dummy point
        pcd.colors = o3d.utility.Vector3dVector(np.array([[1, 1, 1]]))  # White
        
        # Add to visualizer
        vis.add_geometry(pcd)
        
        # Add coordinate frame for reference
        coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
        vis.add_geometry(coord_frame)
        
        # Set rendering options
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.1, 0.1, 0.1])  # Dark gray background
        opt.point_size = 3.0  # Larger points for better visibility
        opt.show_coordinate_frame = True
        opt.light_on = False  # Disable lighting to show true colors
        
        return vis, pcd, coord_frame
        
    except Exception as e:
        print(f"Failed to create visualization: {e}")
        return None, None, None

def main():
    """Main function."""
    global is_ctrl_c, point_cloud_data, color_data, debug_mode
    
    parser = argparse.ArgumentParser(
        description='Aurora Dense Point Cloud Demo - Real-time 3D point cloud visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--device', '-d', type=str, help='Device IP address', default='192.168.11.1')
    parser.add_argument('--max-points', type=int, help='Maximum points per frame', default=50000)
    parser.add_argument('--update-rate', type=float, help='Update rate in Hz', default=10.0)
    parser.add_argument('--software-render', action='store_true', help='Use software rendering')
    parser.add_argument('--headless', action='store_true', help='Run without visualization')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    debug_mode = args.debug
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=== Aurora Dense Point Cloud Demo ===")
    
    sdk = AuroraSDK()
    acquisition_thread = None
    
    try:
        # Connect to device
        print("1. Connecting to device...")
        sdk.connect(connection_string=args.device)
        print("✅ Connected")
        
        # Check depth camera support
        print("2. Checking depth camera support...")
        if not sdk.enhanced_imaging.is_depth_camera_supported():
            print("❌ Depth camera not supported by this device")
            return 1
        print("✅ Depth camera supported")
        
        # Enable subscriptions
        print("3. Setting up subscriptions...")
        success = sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_DEPTH, True)
        print(f"   Depth camera subscription: {'✅' if success else '❌'}")
        
        if not success:
            print("❌ Failed to enable depth camera subscription")
            return 1
        
        # Give the device some time to start streaming depth data
        print("   Waiting for depth camera to initialize...")
        time.sleep(2.0)  # Wait 2 seconds for depth camera to start
        
        # Start acquisition thread
        print("4. Starting acquisition thread...")
        acquisition_thread = threading.Thread(
            target=point_cloud_acquisition_thread,
            args=(sdk, args.max_points, args.update_rate),
            daemon=True
        )
        acquisition_thread.start()
        
        if args.headless:
            # Headless mode
            print("5. Running in headless mode...")
            print("   Press Ctrl+C to exit")
            
            while not is_ctrl_c:
                with point_cloud_lock:
                    if point_cloud_data is not None:
                        print(f"Points: {len(point_cloud_data)}")
                time.sleep(1)
        else:
            # Visualization mode
            print("6. Starting visualization...")
            vis, pcd, coord_frame = create_open3d_visualization(use_software_render=args.software_render)
            
            if vis is None or pcd is None:
                print("❌ Failed to create visualization")
                return 1
            
            print("Controls:")
            print("  Mouse: Rotate view")
            print("  Scroll: Zoom")
            print("  Shift+Mouse: Pan")
            print("  R: Reset view")
            print("\nColoring: Camera-aligned texture (grayscale on mono-camera devices)")
            print("Coordinate frame: Red=X, Green=Y, Blue=Z")
            print("SDK camera coordinates: X=right, Y=down, Z=forward")
            print("Lighting: Disabled for true color display")
            
            # Main visualization loop
            frame_count = 0
            last_update = time.time()
            first_frame = True
            
            while not is_ctrl_c:
                # Update point cloud
                updated = False
                with point_cloud_lock:
                    if point_cloud_data is not None and color_data is not None:
                        pcd.points = o3d.utility.Vector3dVector(point_cloud_data)
                        pcd.colors = o3d.utility.Vector3dVector(color_data)
                        frame_count += 1
                        updated = True
                
                if updated:
                    # Update visualization
                    vis.update_geometry(pcd)
                    
                    # Reset view on first real frame
                    if first_frame and len(point_cloud_data) > 100:
                        vis.reset_view_point(True)
                        first_frame = False
                
                if not vis.poll_events():
                    break
                vis.update_renderer()
                
                # Print FPS
                current_time = time.time()
                if current_time - last_update >= 5.0:
                    fps = frame_count / (current_time - last_update)
                    points = len(point_cloud_data) if point_cloud_data is not None else 0
                    print(f"FPS: {fps:.1f}, Points: {points}")
                    frame_count = 0
                    last_update = current_time
                
                time.sleep(0.01)
            
            vis.destroy_window()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        is_ctrl_c = True
        if acquisition_thread and acquisition_thread.is_alive():
            acquisition_thread.join(timeout=2.0)
        
        try:
            sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_DEPTH, False)
            sdk.disconnect()
            sdk.release()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
