#!/usr/bin/env python3
"""
Map Render Example

This example demonstrates how to connect to an Aurora device and visualize map data.
It's the Python equivalent of the map_render C++ demo.

Note example requires OpenCV and NumPy for visualization.

Usage:
    python map_render.py [connection_string]
    
Example:
    python map_render.py 192.168.1.212
"""

import sys
import time
import argparse
import signal
import math
from typing import Optional, List, Tuple

import os

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError
        return AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError
        return AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Warning not available. Install with install opencv-python")

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError = setup_sdk_import()


class MapRenderDemo:
    """Map rendering demonstration class."""
    
    def __init__(self):
        self.sdk = None
        self.running = True
        self.map_width = 1200  # Larger window
        self.map_height = 900
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C signal for graceful exit."""
        print("\nCtrl-C pressed, exiting...")
        self.running = False
    
    def create_visualization_map(self, map_points, keyframes, current_pose):
        """
        Create a visualization map from visual map points and keyframes.
        
        Args:
            map_points: List of (x, y, z) 3D map points from VSLAM
            keyframes: List of keyframe poses for trajectory
            current_pose: Current device pose (x, y, z, qx, qy, qz, qw)
            
        Returns:
            np.ndarray: Map image
        """
        # Create blank map
        map_img = np.zeros((self.map_height, self.map_width, 3), dtype=np.uint8)
        
        if not map_points and not keyframes:
            # No data to visualize
            cv2.putText(map_img, "Waiting for map data...", 
                       (self.map_width//4, self.map_height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            return map_img
        
        # Calculate map bounds from keyframes and map points
        all_points = []
        if keyframes:
            all_points.extend([(kf[0], kf[1]) for kf in keyframes])
        if map_points:
            # Sample map points to avoid performance issues with large datasets
            step = max(1, len(map_points) // 1000)  # Sample at most 1000 points for bounds
            all_points.extend([(mp[0], mp[1]) for mp in map_points[::step]])
        if current_pose:
            all_points.append((current_pose[0], current_pose[1]))
            
        if not all_points:
            return map_img
        
        # Robust bounds calculation with outlier filtering
        x_coords = [point[0] for point in all_points]
        y_coords = [point[1] for point in all_points]
        
        # Filter outliers (remove extreme 5% on each side)
        x_coords.sort()
        y_coords.sort()
        n = len(x_coords)
        trim = max(1, n // 20)  # Remove 5% outliers
        x_coords = x_coords[trim:-trim] if n > 20 else x_coords
        y_coords = y_coords[trim:-trim] if n > 20 else y_coords
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Add reasonable margin
        width = max_x - min_x
        height = max_y - min_y
        margin = max(2.0, max(width, height) * 0.1)  # 10% margin or 2m minimum
        
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin
        
        # Calculate map center and scale
        map_center_x = (min_x + max_x) / 2.0
        map_center_y = (min_y + max_y) / 2.0
        
        # Calculate scale with better defaults
        map_width_m = max_x - min_x
        map_height_m = max_y - min_y
        
        if map_width_m > 0 and map_height_m > 0:
            scale_x = (self.map_width - 80) / map_width_m  # 40px margin on each side
            scale_y = (self.map_height - 80) / map_height_m
            scale = min(scale_x, scale_y)
            scale = max(1.0, min(scale, 100.0))  # Clamp scale between 1 and 100 px/m
        else:
            scale = 20.0  # Default 20 pixels per meter
        
        # Helper function to convert world coordinates to image coordinates
        def world_to_image(x, y):
            img_x = int((x - map_center_x) * scale + self.map_width / 2.0)
            img_y = int(self.map_height / 2.0 - (y - map_center_y) * scale)
            return img_x, img_y
        
        # Draw map points as green heat map (following C++ demo)
        # Sample map points for performance if there are too many
        points_to_draw = map_points
        if len(map_points) > 5000:
            step = len(map_points) // 5000
            points_to_draw = map_points[::step]
        
        for point in points_to_draw:
            img_x, img_y = world_to_image(point[0], point[1])
            if 0 <= img_x < self.map_width and 0 <= img_y < self.map_height:
                # Draw small square like C++ demo
                for yy in range(max(0, img_y), min(img_y + 2, self.map_height)):
                    for xx in range(max(0, img_x), min(img_x + 2, self.map_width)):
                        if 0 <= xx < self.map_width and 0 <= yy < self.map_height:
                            # Green channel heat map with safe arithmetic
                            current_val = int(map_img[yy, xx, 1])
                            if current_val == 0:
                                map_img[yy, xx, 1] = np.uint8(100)
                            else:
                                new_val = min(255, current_val + 60)
                                map_img[yy, xx, 1] = np.uint8(new_val)
        
        # Draw keyframe trajectory in red (following C++ demo)
        if len(keyframes) > 1:
            for i in range(1, len(keyframes)):
                prev_kf = keyframes[i-1]
                curr_kf = keyframes[i]
                
                prev_x, prev_y = world_to_image(prev_kf[0], prev_kf[1])
                curr_x, curr_y = world_to_image(curr_kf[0], curr_kf[1])
                
                # Draw trajectory line in red
                if (0 <= prev_x < self.map_width and 0 <= prev_y < self.map_height and
                    0 <= curr_x < self.map_width and 0 <= curr_y < self.map_height):
                    cv2.line(map_img, (prev_x, prev_y), (curr_x, curr_y), (0, 0, 100), 1)
                    cv2.circle(map_img, (curr_x, curr_y), 2, (0, 0, 100), 1)
        
        # Draw current position in bright red (following C++ demo)
        if current_pose:
            img_x, img_y = world_to_image(current_pose[0], current_pose[1])
            if 0 <= img_x < self.map_width and 0 <= img_y < self.map_height:
                cv2.circle(map_img, (img_x, img_y), 3, (0, 0, 200), 2)
        
        # Add info text (following C++ demo)
        cv2.putText(map_img, "Map Points: {}".format(len(map_points)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(map_img, "Keyframes: {}".format(len(keyframes)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(map_img, "Scale: {:.1f} px/m".format(scale), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(map_img, "Map Size: {:.1f}x{:.1f}m".format(map_width_m, map_height_m), (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return map_img
    
    def run(self, connection_string = None):
        """
        Run the map render demo.
        
        Args:
            connection_string connection string (e.g., "192.168.1.212")
        """
        if not OPENCV_AVAILABLE:
            print("Error is required for this demo.")
            print("Install with install opencv-python")
            return 1
        
        try:
            # Create SDK instance
            print("Creating Aurora SDK instance...")
            self.sdk = AuroraSDK()
            
            # Print version info
            version_info = self.sdk.get_version_info()
            print(f"Aurora SDK Version: {version_info['version_string']}")
            
            # Session created automatically
            print("SDK session created automatically...")
            
            # Connect to device
            if connection_string:
                print(f"Connecting to device at: {connection_string}")
                self.sdk.connect(connection_string=connection_string)
            else:
                print("Discovering Aurora devices...")
                devices = self.sdk.discover_devices(timeout=5.0)
                
                if not devices:
                    print("No Aurora devices found!")
                    return 1
                
                print(f"Found {len(devices)} Aurora device(s):")
                for i, device in enumerate(devices):
                    print(f"  Device {i}: {device['device_name']}")
                
                print("Connecting to first device...")
                self.sdk.connect(device_info=devices[0])
            
            print("Connected to Aurora device!")
            
            # Get device info
            try:
                device_info = self.sdk.get_device_info()
                print(f"Device Name: {device_info.device_name}")
                print(f"Device Model: {device_info.device_model_string}")
            except Exception as e:
                print(f"Warning: Could not get device info: {e}")
            
            # Get map info
            try:
                map_info = self.sdk.get_map_info()
                print(f"Map Info: {map_info}")
            except Exception as e:
                print(f"Warning: Could not get map info: {e}")
            
            # Enable map data syncing for visual map data
            try:
                print("Enabling map data syncing...")
                self.sdk.enable_map_data_syncing(True)
                print("Map data syncing enabled")
            except Exception as e:
                print(f"Warning: Could not enable map data syncing: {e}")
            
            self.sdk.controller.resync_map_data()
            
            print("\nStarting map visualization (Press ESC to exit, Space for info)...")
            
            # Create OpenCV window (resizable)
            cv2.namedWindow("Aurora Map Visualization", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Aurora Map Visualization", self.map_width, self.map_height)
            
            # Data storage
            map_points = []
            keyframes = []
            current_pose = None
            last_map_refresh_time = 0
            
            # Main visualization loop
            while self.running:
                try:
                    # Get current pose
                    try:
                        position, rotation, timestamp = self.sdk.get_current_pose(use_se3=True)
                        current_pose = position + rotation  # Combine position and rotation
                    except DataNotReadyError:
                        pass  # Pose not ready, continue with existing data
                    
                    # Get map data periodically (every 2 seconds to avoid overwhelming)
                    current_time = time.time()
                    if current_time - last_map_refresh_time > 2.0:
                        try:
                            # Get visual map data (map points and keyframes)
                            map_data = self.sdk.get_map_data()
                            if map_data:
                                new_map_points = map_data.get('map_points', [])
                                new_keyframes = map_data.get('keyframes', [])
                                
                                # Update data if we got something new
                                if new_map_points or new_keyframes:
                                    map_points = new_map_points
                                    keyframes = new_keyframes
                                    print(f"Updated: {len(map_points)} map points, {len(keyframes)} keyframes")
                                
                                last_map_refresh_time = current_time
                                
                                # Force resync every 10 seconds to get latest data
                                if current_time % 10 < 2:
                                    try:
                                        self.sdk.resync_map_data(invalidate_cache=False)
                                    except:
                                        pass
                                        
                        except DataNotReadyError:
                            pass  # Map data not ready
                        except Exception as e:
                            # Map data access might not be implemented yet
                            if "not implemented" not in str(e).lower() and current_time % 5 < 2:
                                print(f"Map data access error: {e}")
                    
                    # Create and display visualization
                    map_img = self.create_visualization_map(map_points, keyframes, current_pose)
                    cv2.imshow("Aurora Map Visualization", map_img)
                    
                except Exception as e:
                    print(f"Error in visualization loop: {e}")
                    # Create error image
                    error_img = np.zeros((self.map_height, self.map_width, 3), dtype=np.uint8)
                    cv2.putText(error_img, f"Error: {str(e)[:50]}", 
                               (50, self.map_height//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.imshow("Aurora Map Visualization", error_img)
                
                # Check for key presses
                key = cv2.waitKey(30) & 0xFF
                if key == 27:  # ESC key
                    break
                elif key == ord(' '):  # Space key - show info
                    print(f"Map points: {len(map_points)}")
                    print(f"Keyframes: {len(keyframes)}")
                    if current_pose:
                        print(f"Current pose: x={current_pose[0]:.3f}, y={current_pose[1]:.3f}, z={current_pose[2]:.3f}")
                elif key == ord('c'):  # 'c' key - clear history
                    map_points.clear()
                    keyframes.clear()
                    print("Cleared map data")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.033)  # ~30 FPS
                
        except ConnectionError as e:
            print(f"Connection error: {e}")
            return 1
        except AuroraSDKError as e:
            print(f"Aurora SDK error: {e}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1
        finally:
            # Cleanup
            if OPENCV_AVAILABLE:
                cv2.destroyAllWindows()
            if self.sdk:
                print("Disconnecting...")
                try:
                    self.sdk.enable_map_data_syncing(False)
                except:
                    pass
                self.sdk.disconnect()
                self.sdk.release()
            print("Demo finished.")
        
        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Map Render Demo - Visualize map data from Aurora device",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python map_render.py                    # Auto-discover and connect
    python map_render.py 192.168.1.212     # Connect to specific IP

Controls:
    ESC    - Exit the demo
    Space  - Show current map information (map points, keyframes, pose)
    c      - Clear map data

This demo visualizes VSLAM map data including:
    - Map points (green heat map)
    - Keyframe trajectory (red lines and circles)
    - Current pose (bright red circle)
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    
    args = parser.parse_args()
    
    demo = MapRenderDemo()
    return demo.run(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())