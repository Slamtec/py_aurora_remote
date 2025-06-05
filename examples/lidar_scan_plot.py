#!/usr/bin/env python3
"""
LiDAR Scan Plot Example

This example demonstrates how to retrieve and visualize 2D LiDAR scan data from Aurora device.
It's the Python equivalent of the lidar_scan_plot C++ demo.

Usage:
    python lidar_scan_plot.py [connection_string]
    
Example:
    python lidar_scan_plot.py 192.168.1.212
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
    print("Warning: OpenCV not available. Install with: pip install opencv-python")

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError = setup_sdk_import()


class LidarScanPlotter:
    """LiDAR scan plotting demonstration class."""
    
    def __init__(self):
        self.sdk = None
        self.running = True
        self.canvas_size = 500
        self.max_distance = 20.0  # meters
        self.scale = self.canvas_size / self.max_distance
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C signal for graceful exit."""
        print("\nCtrl-C pressed, exiting...")
        self.running = False
    
    def plot_lidar_scan(self, scan_data):
        """
        Plot LiDAR scan data on OpenCV canvas.
        
        Args:
            scan_data: LidarScanData object containing scan points
            
        Returns:
            numpy.ndarray: OpenCV image with plotted scan points
        """
        if not OPENCV_AVAILABLE:
            return None
        
        # Create blank canvas
        canvas = np.zeros((self.canvas_size, self.canvas_size, 3), dtype=np.uint8)
        
        if scan_data is None or scan_data.get_scan_count() == 0:
            # No scan data, just show empty canvas with info
            cv2.putText(canvas, "No LiDAR data", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return canvas
        
        # Plot each scan point
        valid_points = 0
        for dist, angle, quality in scan_data.points:
            if quality > 0:  # Valid point
                # Convert polar to cartesian coordinates
                x = dist * math.cos(angle) * self.scale
                y = dist * math.sin(angle) * self.scale
                
                # Convert to image coordinates (center origin, y-axis flipped)
                img_x = int(x + self.canvas_size // 2)
                img_y = int(self.canvas_size // 2 - y)
                
                # Check if point is within canvas bounds
                if 0 <= img_x < self.canvas_size and 0 <= img_y < self.canvas_size:
                    # Color based on quality (RSSI)
                    color_intensity = min(255, quality * 4)
                    color = (color_intensity, 0, 255 - quality)
                    cv2.circle(canvas, (img_x, img_y), 1, color, 1)
                    valid_points += 1
        
        # Add information text
        info_text = "Scan Points: {}".format(scan_data.get_scan_count())
        cv2.putText(canvas, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        valid_text = "Valid Points: {}".format(valid_points)
        cv2.putText(canvas, valid_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add timestamp if available
        if hasattr(scan_data, 'timestamp_ns') and scan_data.timestamp_ns > 0:
            timestamp_sec = scan_data.timestamp_ns / 1e9
            time_text = "Time: {:.3f}s".format(timestamp_sec)
            cv2.putText(canvas, time_text, (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Draw coordinate system
        center = self.canvas_size // 2
        cv2.line(canvas, (center - 20, center), (center + 20, center), (100, 100, 100), 1)
        cv2.line(canvas, (center, center - 20), (center, center + 20), (100, 100, 100), 1)
        
        # Draw distance rings
        for ring_dist in [5, 10, 15]:  # meters
            if ring_dist <= self.max_distance:
                radius = int(ring_dist * self.scale)
                cv2.circle(canvas, (center, center), radius, (50, 50, 50), 1)
        
        return canvas
    
    def run(self, connection_string=None):
        """
        Run the LiDAR scan plotter.
        
        Args:
            connection_string: Aurora device connection string (e.g., "192.168.1.212")
        """
        if not OPENCV_AVAILABLE:
            print("Error: OpenCV is required for this demo.")
            print("Install with: pip install opencv-python")
            return 1
        
        try:
            # Create SDK instance
            print("Creating Aurora SDK instance...")
            self.sdk = AuroraSDK()
            
            # Print version info
            try:
                version_info = self.sdk.get_version_info()
                print(f"Aurora SDK Version: {version_info['version_string']}")
            except Exception as e:
                print(f"Warning: Could not get SDK version: {e}")
            
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
            
            print("\nStarting LiDAR scan visualization (Press ESC to exit)...")
            
            # Create OpenCV window
            cv2.namedWindow("LiDAR Scan Plot", cv2.WINDOW_AUTOSIZE)
            
            # Main visualization loop
            last_scan_count = 0
            no_data_count = 0
            
            while self.running:
                try:
                    # Get recent LiDAR scan data
                    scan_data = self.sdk.get_recent_lidar_scan()
                    
                    if scan_data is not None:
                        no_data_count = 0
                        if scan_data.get_scan_count() != last_scan_count:
                            print(f"LiDAR scan: {scan_data.get_scan_count()} points, "
                                  f"{len(scan_data.get_valid_points())} valid")
                            last_scan_count = scan_data.get_scan_count()
                    else:
                        no_data_count += 1
                        if no_data_count % 30 == 1:  # Print every second (assuming 30 FPS)
                            print("Waiting for LiDAR scan data...")
                    
                    # Create and display visualization
                    canvas = self.plot_lidar_scan(scan_data)
                    if canvas is not None:
                        cv2.imshow("LiDAR Scan Plot", canvas)
                    
                    # Check for key presses
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27:  # ESC key
                        break
                    elif key == ord(' '):  # Space key - show detailed info
                        if scan_data is not None:
                            print(f"\nDetailed scan info:")
                            print(f"  Timestamp: {scan_data.timestamp_ns} ns")
                            print(f"  Layer ID: {scan_data.layer_id}")
                            print(f"  Binded KF ID: {scan_data.binded_kf_id}")
                            print(f"  Delta Yaw: {scan_data.dyaw:.3f} rad")
                            print(f"  Total Points: {scan_data.get_scan_count()}")
                            print(f"  Valid Points: {len(scan_data.get_valid_points())}")
                        else:
                            print("No scan data available")
                
                except DataNotReadyError:
                    # LiDAR data not ready, continue
                    pass
                except Exception as e:
                    print(f"Error in visualization loop: {e}")
                    # Continue anyway
                
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
            import traceback
            traceback.print_exc()
            return 1
        finally:
            # Cleanup
            if OPENCV_AVAILABLE:
                cv2.destroyAllWindows()
            if self.sdk:
                print("Disconnecting...")
                try:
                    self.sdk.disconnect()
                    self.sdk.release()
                except:
                    pass
            print("Demo finished.")
        
        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="LiDAR Scan Plot Demo - Visualize 2D LiDAR scan data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python lidar_scan_plot.py                    # Auto-discover and connect
    python lidar_scan_plot.py 192.168.1.212     # Connect to specific IP

Controls:
    ESC    - Exit the demo
    Space  - Show detailed scan information

This demo visualizes real-time 2D LiDAR scan data from Aurora device:
    - Scan points plotted in polar coordinates
    - Color intensity represents signal quality (RSSI)
    - Distance rings for reference (5m, 10m, 15m)
    - Real-time scan statistics
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    
    args = parser.parse_args()
    
    demo = LidarScanPlotter()
    return demo.run(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())