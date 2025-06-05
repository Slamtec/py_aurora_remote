#!/usr/bin/env python3
"""
Camera Preview Example

This example demonstrates how to connect to an Aurora device and display camera preview images.
This is a simple version that only shows the camera preview without keypoints or tracking data.

Note: This example requires OpenCV for image display.

Usage:
    python camera_preview.py [connection_string]
    
Example:
    python camera_preview.py 192.168.1.212
"""

import sys
import time
import argparse
import signal
from typing import Optional

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
        import os
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


class CameraPreviewDemo:
    """Simple camera preview demonstration class."""
    
    def __init__(self):
        self.sdk = None
        self.running = True
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C signal for graceful exit."""
        print("\nCtrl-C pressed, exiting...")
        self.running = False
    
    def run(self, connection_string=None):
        """
        Run the camera preview demo.
        
        Args:
            connection_string: connection string (e.g., "192.168.1.212")
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
            version_info = self.sdk.get_version_info()
            print(f"Aurora SDK Version: {version_info['version_string']}")
                 
            # Connect to device
            if connection_string:
                print(f"Connecting to device at: {connection_string}")
                # First discover devices to see what's available
                devices = self.sdk.discover_devices(timeout=5.0)
                
                if not devices:
                    print("No Aurora devices found!")
                    return 1
                
                print(f"Found {len(devices)} Aurora device(s):")
                for i, device in enumerate(devices):
                    print(f"  Device {i}: {device['device_name']}")
                    for j, option in enumerate(device['options']):
                        print(f"    Option {j}: {option['protocol']}://{option['address']}:{option['port']}")
                
                # Find device matching the connection string
                target_device = None
                for device in devices:
                    for option in device['options']:
                        if connection_string in option['address']:
                            target_device = device
                            break
                    if target_device:
                        break
                
                if target_device:
                    print(f"Found matching device for {connection_string}")
                    self.sdk.connect(device_info=target_device)
                else:
                    print(f"No discovered device matches {connection_string}, trying direct connection...")
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
                    for j, option in enumerate(device['options']):
                        print(f"    Option {j}: {option['protocol']}://{option['address']}:{option['port']}")
                
                print("Trying to connect to devices...")
                connected = False
                for i, device in enumerate(devices):
                    try:
                        print(f"Attempting to connect to device {i}...")
                        self.sdk.connect(device_info=device)
                        print(f"Successfully connected to device {i}!")
                        connected = True
                        break
                    except Exception as e:
                        print(f"Failed to connect to device {i}: {e}")
                        continue
                
                if not connected:
                    print("Failed to connect to any discovered device!")
                    return 1
            
            print("Connected to Aurora device!")
            
            # Get device info
            try:
                device_info = self.sdk.get_device_info()
                print(f"Device Name: {device_info.device_name}")
                print(f"Device Model: {device_info.device_model_string}")
            except Exception as e:
                print(f"Warning: Could not get device info: {e}")
            
            print("\nStarting camera preview (Press ESC to exit, Space for info)...")
            
            # Create OpenCV windows
            cv2.namedWindow("Aurora Camera Preview", cv2.WINDOW_AUTOSIZE)
            
            frame_count = 0
            last_time = time.time()
            fps = 0.0
            last_timestamp = 0  # Track previous frame timestamp to avoid duplicates
            
            # Main preview loop
            while self.running:
                try:
                    # Get camera preview images
                    left_frame, right_frame = self.sdk.get_camera_preview()
                    
                    if left_frame and right_frame:
                        # Check timestamp to avoid processing duplicate frames
                        current_timestamp = left_frame.timestamp_ns
                        if current_timestamp == last_timestamp:
                            # Skip duplicate frame, but still check for key presses
                            key = cv2.waitKey(10) & 0xFF
                            if key == 27:  # ESC key
                                break
                            elif key == ord(' '):  # Space key - show info
                                try:
                                    position, rotation, timestamp = self.sdk.get_current_pose(use_se3=True)
                                    print(f"Current pose=({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}), "
                                          f"rot=({rotation[0]:.3f}, {rotation[1]:.3f}, {rotation[2]:.3f}, {rotation[3]:.3f})")
                                except:
                                    print("Pose data not available")
                            continue
                        
                        last_timestamp = current_timestamp
                        
                        # Convert images to OpenCV format
                        left_img = left_frame.to_opencv_image()
                        right_img = right_frame.to_opencv_image()
                        
                        # Create fallback placeholder if conversion failed
                        if left_img is None:
                            left_img = np.zeros((left_frame.height, left_frame.width, 3), dtype=np.uint8)
                            cv2.putText(left_img, "No Image Data", (left_frame.width//4, left_frame.height//2), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        
                        if right_img is None:
                            right_img = np.zeros((right_frame.height, right_frame.width, 3), dtype=np.uint8)
                            cv2.putText(right_img, "No Image Data", (right_frame.width//4, right_frame.height//2), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        
                        # Add text overlay with frame information
                        text_left = f"Left {left_frame.width}x{left_frame.height}"
                        text_right = f"Right {right_frame.width}x{right_frame.height}"
                        
                        cv2.putText(left_img, text_left, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(right_img, text_right, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Add frame counter and timestamp
                        frame_count += 1
                        current_time = time.time()
                        if current_time - last_time >= 1.0:
                            fps = frame_count / (current_time - last_time)
                            frame_count = 0
                            last_time = current_time
                        
                        cv2.putText(left_img, f"FPS: {fps:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        cv2.putText(right_img, f"Timestamp: {left_frame.timestamp_ns}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        
                        # Concatenate left and right images side by side
                        combined_img = np.hstack((left_img, right_img))
                        
                        # Display the combined image
                        cv2.imshow("Aurora Camera Preview", combined_img)
                        
                    else:
                        # No frames available, show waiting message
                        wait_img = np.zeros((240, 640, 3), dtype=np.uint8)
                        cv2.putText(wait_img, "Waiting for camera frames...", (150, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        cv2.imshow("Aurora Camera Preview", wait_img)
                    
                except DataNotReadyError:
                    # Data not ready, show waiting message
                    wait_img = np.zeros((240, 640, 3), dtype=np.uint8)
                    cv2.putText(wait_img, "Camera data not ready...", (180, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.imshow("Aurora Camera Preview", wait_img)
                except Exception as e:
                    print(f"Error getting camera preview: {e}")
                    # Show error message
                    wait_img = np.zeros((240, 640, 3), dtype=np.uint8)
                    cv2.putText(wait_img, f"Error: {str(e)[:50]}", (50, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.imshow("Aurora Camera Preview", wait_img)
                
                # Check for key presses
                key = cv2.waitKey(10) & 0xFF
                if key == 27:  # ESC key
                    break
                elif key == ord(' '):  # Space key - show info
                    try:
                        position, rotation, timestamp = self.sdk.get_current_pose(use_se3=True)
                        print(f"Current pose=({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}), "
                              f"rot=({rotation[0]:.3f}, {rotation[1]:.3f}, {rotation[2]:.3f}, {rotation[3]:.3f})")
                    except:
                        print("Pose data not available")
                
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
                self.sdk.disconnect()
                self.sdk.release()
            print("Demo finished.")
        
        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Camera Preview Demo - Display camera frames from Aurora device",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python camera_preview.py                    # Auto-discover and connect
    python camera_preview.py 192.168.1.212     # Connect to specific IP

Controls:
    ESC    - Exit the demo
    Space  - Show current pose information
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    
    args = parser.parse_args()
    
    demo = CameraPreviewDemo()
    return demo.run(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())