#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - Depth Camera Preview

This demo shows how to capture and display depth camera frames using Enhanced Imaging API.
Features:
- Real-time depth map display with color mapping for better visualization
- Support for different color maps (JET, HSV, HOT, etc.)
- Depth value inspection with mouse hover
- Keyboard controls for color map switching
- Connection to Aurora device with depth camera support

Requirements:
- numpy
- opencv-python
- Aurora device with depth camera support and SDK 2.0
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
        tuple: (AuroraSDK, AuroraSDKError)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.exceptions import AuroraSDKError
        return AuroraSDK, AuroraSDKError
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.exceptions import AuroraSDKError
        return AuroraSDK, AuroraSDKError

# Setup SDK import
AuroraSDK, AuroraSDKError = setup_sdk_import()

try:
    import cv2
    import numpy as np
except ImportError as e:
    print("Error: Required dependencies not found.")
    print("Please install: pip install opencv-python numpy")
    sys.exit(1)

# Global variables
is_ctrl_c = False
current_colormap = cv2.COLORMAP_JET
colormap_names = {
    cv2.COLORMAP_JET: "JET",
    cv2.COLORMAP_HSV: "HSV", 
    cv2.COLORMAP_HOT: "HOT",
    cv2.COLORMAP_COOL: "COOL",
    cv2.COLORMAP_SPRING: "SPRING",
    cv2.COLORMAP_SUMMER: "SUMMER",
    cv2.COLORMAP_AUTUMN: "AUTUMN",
    cv2.COLORMAP_WINTER: "WINTER",
    cv2.COLORMAP_RAINBOW: "RAINBOW",
    cv2.COLORMAP_OCEAN: "OCEAN",
    cv2.COLORMAP_BONE: "BONE",
    cv2.COLORMAP_PINK: "PINK"
}
colormap_list = list(colormap_names.keys())
current_colormap_index = 0

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    global is_ctrl_c
    print("\nCtrl-C pressed, exiting...")
    is_ctrl_c = True

def mouse_callback(event, x, y, flags, param):
    """Mouse callback for depth value inspection."""
    depth_frame, depth_map = param
    if depth_map is not None and event == cv2.EVENT_MOUSEMOVE:
        if 0 <= x < depth_map.shape[1] and 0 <= y < depth_map.shape[0]:
            depth_value = depth_map[y, x]
            if depth_value > 0 and depth_value < float('inf'):
                # Update window title with depth info
                title = f"Depth Camera Preview - Depth at ({x},{y}): {depth_value:.3f}m"
                cv2.setWindowTitle("Depth Camera Preview", title)

def discover_and_select_device(sdk):
    """Discover and select Aurora device."""
    print("Discovering Aurora devices...")
    
    # Discover devices with timeout
    devices = sdk.discover_devices(timeout=5.0)
    
    if not devices:
        print("No Aurora devices found.")
        return None
    
    print(f"Found {len(devices)} Aurora device(s):")
    for i, device in enumerate(devices):
        print(f"Device {i}: {device['device_name']}")
        for j, option in enumerate(device['options']):
            print(f"  Option {j}: {option['protocol']}://{option['address']}:{option['port']}")
    
    # Use first device for simplicity
    selected_device = devices[0]
    print(f"Selected device: {selected_device['device_name']}")
    
    return selected_device

def connect_to_device(sdk, device_info):
    """Connect to Aurora device."""
    try:
        print(f"Connecting to device...")
        sdk.connect(device_info=device_info)
        print("Connected successfully!")
        
        # Check if depth camera is supported before subscription
        if sdk.enhanced_imaging.is_depth_camera_supported():
            print("Device supports depth camera.")
            
            # Enable Enhanced Imaging subscription using SDK 2.0 API (AFTER connection)
            from slamtec_aurora_sdk import ENHANCED_IMAGE_TYPE_DEPTH
            try:
                sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_DEPTH, True)
                print("Enhanced imaging depth camera subscription enabled.")
            except Exception as e:
                print(f"Warning: Failed to subscribe to depth camera: {e}")
                print("Continuing anyway to test frame retrieval...")
                # Don't return False, continue to test if frames are available
        else:
            print("Warning: Device does not support depth camera.")
            print("Continuing anyway to test frame retrieval...")
        
        return True
        
    except AuroraSDKError as e:
        print(f"Failed to connect to device: {e}")
        return False

def get_depth_frame(sdk, verbose=True):
    """Get depth camera frame from the device."""
    try:
        # Follow C++ demo pattern: first wait, then peek with DEPTH_MAP frame type
        from slamtec_aurora_sdk import DEPTHCAM_FRAME_TYPE_DEPTH_MAP
        
        # Wait for next frame (like C++ demo)
        if not sdk.enhanced_imaging.wait_depth_camera_next_frame(1000):
            if verbose:
                print("wait_depth_camera_next_frame timed out")
            return None
            
        # Peek depth map frame (using DEPTH_MAP type for visualization like C++ demo)
        depth_frame = sdk.enhanced_imaging.peek_depth_camera_frame(
            frame_type=DEPTHCAM_FRAME_TYPE_DEPTH_MAP
        )
        return depth_frame
        
    except AuroraSDKError as e:
        if verbose and "NOT_READY" not in str(e):
            print(f"Warning: Failed to get depth frame: {e}")
    except Exception as e:
        if verbose:
            print(f"Error getting depth frame: {e}")
    
    return None

def get_camera_overlay(sdk, depth_frame, verbose=True):
    """Get camera image overlay for depth frame."""
    if not depth_frame:
        return None
        
    try:
        # Get related rectified camera image for the depth frame timestamp
        camera_frame = sdk.enhanced_imaging.peek_depth_camera_related_rectified_image(
            depth_frame.timestamp_ns
        )
        return camera_frame
        
    except AuroraSDKError as e:
        if verbose and "NOT_READY" not in str(e):
            print(f"Warning: Failed to get camera overlay: {e}")
    except Exception as e:
        if verbose:
            print(f"Error getting camera overlay: {e}")
    
    return None

def create_depth_overlay(depth_frame, camera_frame, colormap):
    """Create overlay of depth map and camera image."""
    if not depth_frame or not camera_frame:
        return None
        
    try:
        # Get colorized depth map
        depth_colorized = depth_frame.to_colorized_depth_map(colormap)
        if depth_colorized is None:
            return None
            
        # Convert camera frame to OpenCV image using ImageFrame interface
        camera_image = None
        if camera_frame and camera_frame.data:
            # Use ImageFrame's built-in OpenCV conversion
            camera_image = camera_frame.to_opencv_image()
        
        if camera_image is None:
            return depth_colorized
            
        # Resize images to match if needed
        if camera_image.shape[:2] != depth_colorized.shape[:2]:
            camera_image = cv2.resize(camera_image, 
                                    (depth_colorized.shape[1], depth_colorized.shape[0]))
        
        # Blend images using 50/50 alpha like C++ demo
        overlay = cv2.addWeighted(depth_colorized, 0.5, camera_image, 0.5, 0)
        return overlay
        
    except Exception as e:
        print(f"Error creating depth overlay: {e}")
        return depth_colorized  # Return depth only if overlay fails

def display_help():
    """Display help information."""
    help_text = """
Depth Camera Preview Controls:
==============================
ESC/Q     - Quit application
SPACE     - Switch color map
H         - Show this help
R         - Reset view
S         - Save current frame
Mouse     - Hover to see depth values

Color Maps:
- JET (default): Blue (close) to Red (far)
- HSV: Full color spectrum
- HOT: Black-Red-Yellow-White
- COOL: Cyan to Magenta
- And more...

Note: Move mouse over depth image to see depth values.
"""
    print(help_text)

def main():
    """Main function."""
    global is_ctrl_c, current_colormap, current_colormap_index
    
    parser = argparse.ArgumentParser(description='Aurora Depth Camera Preview Demo')
    parser.add_argument('--device', '-d', type=str, 
                       help='Device IP address (default: auto-discover)', default=None)
    parser.add_argument('--colormap', '-c', type=str, 
                       choices=['jet', 'hsv', 'hot', 'cool', 'spring', 'summer', 'autumn', 'winter'],
                       help='Initial color map (default: jet)', default='jet')
    parser.add_argument('--fps', '-f', type=int, 
                       help='Target FPS (default: 30)', default=30)
    parser.add_argument('--headless', action='store_true',
                       help='Run in headless mode (no GUI, just test frame retrieval)')
    
    args = parser.parse_args()
    
    # Set initial colormap
    colormap_mapping = {
        'jet': cv2.COLORMAP_JET,
        'hsv': cv2.COLORMAP_HSV,
        'hot': cv2.COLORMAP_HOT,
        'cool': cv2.COLORMAP_COOL,
        'spring': cv2.COLORMAP_SPRING,
        'summer': cv2.COLORMAP_SUMMER,
        'autumn': cv2.COLORMAP_AUTUMN,
        'winter': cv2.COLORMAP_WINTER
    }
    if args.colormap in colormap_mapping:
        current_colormap = colormap_mapping[args.colormap]
        current_colormap_index = colormap_list.index(current_colormap)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize SDK
    print("Initializing Aurora SDK...")
    sdk = AuroraSDK()
    
    try:
        
        # Connect to device
        if args.device:
            # Connect to specific device IP
            print(f"Connecting to device at {args.device}...")
            sdk.connect(connection_string=args.device)
            print("Connected successfully!")
            
            # Check if depth camera is supported before subscription
            if sdk.enhanced_imaging.is_depth_camera_supported():
                print("Device supports depth camera.")
                
                # Enable Enhanced Imaging subscription using SDK 2.0 API (AFTER connection)
                from slamtec_aurora_sdk import ENHANCED_IMAGE_TYPE_DEPTH
                try:
                    sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_DEPTH, True)
                    print("Enhanced imaging depth camera subscription enabled.")
                except Exception as e:
                    print(f"Warning: Failed to subscribe to depth camera: {e}")
                    print("Continuing anyway to test frame retrieval...")
            else:
                print("Warning: Device does not support depth camera.")
                print("Continuing anyway to test frame retrieval...")
        else:
            # Discover and connect to first available device
            device_info = discover_and_select_device(sdk)
            if not device_info:
                return 1
            
            if not connect_to_device(sdk, device_info):
                return 1
        
        # Check device info
        try:
            device_info = sdk.get_device_info()
            print(f"Connected to: {device_info.device_name} (FW: {device_info.firmware_version})")
        except Exception as e:
            print(f"Warning: Could not get device info: {e}")
            print("Continuing with depth camera test...")
        
        # Display help (unless headless)
        if not args.headless:
            display_help()
            
            # Create OpenCV windows
            cv2.namedWindow('Depth Camera Preview', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Depth Camera Preview', 800, 600)
            cv2.namedWindow('Depth Map (Overlay)', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Depth Map (Overlay)', 800, 600)
        
        # Main loop
        frame_count = 0
        fps_counter = time.time()
        target_interval = 1.0 / args.fps
        last_timestamp = 0  # Track previous frame timestamp to avoid duplicates
        
        if args.headless:
            print(f"Starting headless depth camera test...")
            print("Waiting 2 seconds for device to start streaming...")
            time.sleep(2)  # Give device time to start streaming
            print("Testing frame retrieval for 10 seconds...")
            
            test_duration = 10  # seconds
            start_test = time.time()
            
            # Track successful frames
            success_count = 0
            last_status_time = time.time()
            
            while not is_ctrl_c and (time.time() - start_test) < test_duration:
                # Get depth frame (with verbosity for debugging)
                try:
                    depth_frame = get_depth_frame(sdk, verbose=True)
                except Exception as e:
                    print(f"Exception in get_depth_frame: {e}")
                    depth_frame = None
                
                if depth_frame:
                    # Check timestamp to avoid processing duplicate frames
                    current_timestamp = depth_frame.timestamp_ns
                    if current_timestamp == last_timestamp:
                        # Skip duplicate frame
                        continue
                    
                    last_timestamp = current_timestamp
                    frame_count += 1
                    success_count += 1
                    if frame_count <= 3 or frame_count % 10 == 0:  # Limit output
                        print(f"Frame {frame_count}: Size={depth_frame.width}x{depth_frame.height}, "
                              f"Min={depth_frame.min_depth:.3f}m, Max={depth_frame.max_depth:.3f}m")
                        
                        # Test frame conversion on first few frames
                        if frame_count <= 3:
                            try:
                                depth_map = depth_frame.to_numpy_depth_map()
                                if depth_map is not None:
                                    print(f"  → Successfully converted to numpy array: {depth_map.shape}")
                                else:
                                    print(f"  → Failed to convert to numpy array")
                            except Exception as e:
                                print(f"  → Error converting frame: {e}")
                
                # Print status every 2 seconds
                if time.time() - last_status_time >= 2.0:
                    print(f"Status: {success_count} successful frames retrieved")
                    last_status_time = time.time()
                
                time.sleep(0.1)  # 100ms between checks
            
        else:
            print(f"Starting depth camera preview (target: {args.fps} FPS)...")
            print("Press 'H' for help, 'ESC' or 'Q' to quit...")
            
            while not is_ctrl_c:
                start_time = time.time()
                
                # Get depth frame
                depth_frame = get_depth_frame(sdk, verbose=True)
                
                if depth_frame:
                    # Check timestamp to avoid processing duplicate frames
                    current_timestamp = depth_frame.timestamp_ns
                    if current_timestamp == last_timestamp:
                        # Skip duplicate frame, but still check for key presses
                        key = cv2.waitKey(10) & 0xFF
                        if key == 27 or key == ord('q') or key == ord('Q'):  # ESC or Q
                            break
                        elif key == ord(' '):  # Space - switch colormap
                            current_colormap_index = (current_colormap_index + 1) % len(colormap_list)
                            current_colormap = colormap_list[current_colormap_index]
                            print(f"Switched to colormap: {colormap_names[current_colormap]}")
                        elif key == ord('h') or key == ord('H'):  # Help
                            display_help()
                        elif key == ord('r') or key == ord('R'):  # Reset
                            cv2.destroyAllWindows()
                            cv2.namedWindow('Depth Camera Preview', cv2.WINDOW_NORMAL)
                            cv2.resizeWindow('Depth Camera Preview', 800, 600)
                            cv2.namedWindow('Depth Map (Overlay)', cv2.WINDOW_NORMAL)
                            cv2.resizeWindow('Depth Map (Overlay)', 800, 600)
                        elif key == ord('s') or key == ord('S'):  # Save
                            if depth_frame:
                                try:
                                    colorized = depth_frame.to_colorized_depth_map(current_colormap)
                                    if colorized is not None:
                                        filename = f"depth_frame_{int(time.time())}.png"
                                        cv2.imwrite(filename, colorized)
                                        print(f"Saved frame: {filename}")
                                except Exception as e:
                                    print(f"Error saving frame: {e}")
                        continue
                    
                    last_timestamp = current_timestamp
                    # Convert to colorized depth map
                    try:
                        colorized_depth = depth_frame.to_colorized_depth_map(current_colormap)
                        
                        if colorized_depth is not None:
                            # Get raw depth map for mouse inspection
                            depth_map = depth_frame.to_numpy_depth_map()
                            
                            # Add info overlay
                            height, width = colorized_depth.shape[:2]
                            info_text = [
                                f"Colormap: {colormap_names[current_colormap]}",
                                f"Size: {width}x{height}",
                                f"Min: {depth_frame.min_depth:.2f}m",
                                f"Max: {depth_frame.max_depth:.2f}m",
                                f"FPS: {frame_count / (time.time() - fps_counter + 0.001):.1f}"
                            ]
                            
                            for i, text in enumerate(info_text):
                                cv2.putText(colorized_depth, text, (10, 30 + i * 25), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            # Set mouse callback with current frame data
                            cv2.setMouseCallback('Depth Camera Preview', mouse_callback, 
                                               (depth_frame, depth_map))
                            
                            # Display the depth-only frame
                            cv2.imshow('Depth Camera Preview', colorized_depth)
                            
                            # Get camera overlay and display blended version
                            camera_frame = get_camera_overlay(sdk, depth_frame, verbose=False)
                            if camera_frame:
                                overlay_image = create_depth_overlay(depth_frame, camera_frame, current_colormap)
                                if overlay_image is not None:
                                    # Add overlay info
                                    overlay_info_text = [
                                        f"Overlay: Depth + Camera",
                                        f"Alpha: 50% + 50%",
                                        f"Timestamp: {depth_frame.timestamp_ns}"
                                    ]
                                    
                                    for i, text in enumerate(overlay_info_text):
                                        cv2.putText(overlay_image, text, (10, height - 80 + i * 25), 
                                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                                    
                                    cv2.imshow('Depth Map (Overlay)', overlay_image)
                            else:
                                # Show depth-only in overlay window too if no camera frame
                                cv2.imshow('Depth Map (Overlay)', colorized_depth)
                            
                            frame_count += 1
                            
                    except Exception as e:
                        print(f"Error processing depth frame: {e}")
                
                # Handle keyboard input
                key = cv2.waitKey(10) & 0xFF
                if key == 27 or key == ord('q') or key == ord('Q'):  # ESC or Q
                    break
                elif key == ord(' '):  # Space - switch colormap
                    current_colormap_index = (current_colormap_index + 1) % len(colormap_list)
                    current_colormap = colormap_list[current_colormap_index]
                    print(f"Switched to colormap: {colormap_names[current_colormap]}")
                elif key == ord('h') or key == ord('H'):  # Help
                    display_help()
                elif key == ord('r') or key == ord('R'):  # Reset
                    cv2.destroyAllWindows()
                    cv2.namedWindow('Depth Camera Preview', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Depth Camera Preview', 800, 600)
                    cv2.namedWindow('Depth Map (Overlay)', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Depth Map (Overlay)', 800, 600)
                elif key == ord('s') or key == ord('S'):  # Save
                    if depth_frame:
                        try:
                            colorized = depth_frame.to_colorized_depth_map(current_colormap)
                            if colorized is not None:
                                filename = f"depth_frame_{int(time.time())}.png"
                                cv2.imwrite(filename, colorized)
                                print(f"Saved frame: {filename}")
                        except Exception as e:
                            print(f"Error saving frame: {e}")
        
        # Calculate final FPS
        total_time = time.time() - fps_counter
        if total_time > 0:
            print(f"Average FPS: {frame_count / total_time:.2f}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Cleanup
        try:
            cv2.destroyAllWindows()
            sdk.disconnect()
            print("Disconnected from device")
        except:
            pass
    
    print("Depth camera preview demo completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())