#!/usr/bin/env python3
"""
Frame Preview Example (Component-based SDK)

This example demonstrates the new component-based Aurora SDK architecture.
It shows how to use the Controller, DataProvider, and Mapping components
to display camera frames with keypoints.

Usage:
    python frame_preview_v2.py [connection_string]
    
Example:
    python frame_preview_v2.py 192.168.1.212
"""

import sys
import time
import argparse
import signal
from typing import Optional

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


class FramePreviewDemo:
    """Frame preview demonstration using component-based SDK."""
    
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
        Run the frame preview demo using component-based SDK.
        
        Args:
            connection_string: connection string (e.g., "192.168.1.212")
        """
        if not OPENCV_AVAILABLE:
            print("Error: OpenCV is required for this demo.")
            print("Install with: pip install opencv-python")
            return 1
        
        try:
            # Create component-based SDK instance
            print("Creating Aurora SDK (component-based architecture)...")
            self.sdk = AuroraSDK()
            
            # Print version info using convenience method
            version_info = self.sdk.get_version_info()
            print(f"Aurora SDK Version: {version_info['version_string']}")
            
            
            # Connect to device using convenience methods
            if connection_string:
                print(f"Connecting to device at: {connection_string}")
                self.sdk.connect(connection_string=connection_string)
            else:
                # Auto-discover and connect using convenience method
                print("Auto-discovering and connecting...")
                if not self.sdk.quick_start_preview():
                    print("Failed to auto-connect to any device!")
                    return 1
            
            print("Connected to Aurora device!")
            
            # Get device info using convenience method
            try:
                status = self.sdk.get_device_status()
                if status['device_info']:
                    print(f"Device Name: {status['device_info'].device_name}")
                    print(f"Device Model: {status['device_info'].device_model_string}")
            except Exception as e:
                print(f"Warning: Could not get device info: {e}")
            
            print("\nStarting camera preview with keypoints (Press ESC to exit, Space for info)...")
            
            # Create OpenCV windows
            cv2.namedWindow("Aurora Camera Preview (Component-based)", cv2.WINDOW_AUTOSIZE)
            
            frame_count = 0
            last_time = time.time()
            fps = 0.0
            last_timestamp = 0  # Track previous frame timestamp to avoid duplicates
            
            # Main preview loop
            while self.running:
                try:
                    # Get tracking frame via DataProvider (includes images and keypoints)
                    tracking_frame = self.sdk.data_provider.get_tracking_frame()
                    
                    if tracking_frame and tracking_frame.left_image and tracking_frame.right_image:
                        left_frame = tracking_frame.left_image
                        right_frame = tracking_frame.right_image
                        
                        # Check timestamp to avoid processing duplicate frames
                        current_timestamp = left_frame.timestamp_ns
                        if current_timestamp == last_timestamp:
                            # Skip duplicate frame, but still check for key presses
                            key = cv2.waitKey(10) & 0xFF
                            if key == 27:  # ESC key
                                break
                            elif key == ord(' '):  # Space key - show info
                                try:
                                    position, rotation, timestamp = self.sdk.data_provider.get_current_pose(use_se3=True)
                                    print(f"Current pose=({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}), "
                                          f"rot=({rotation[0]:.3f}, {rotation[1]:.3f}, {rotation[2]:.3f}, {rotation[3]:.3f})")
                                    status = self.sdk.get_device_status()
                                    print(f"Device status: connected={status['connected']}, session_active={status['session_active']}")
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
                        
                        # Draw keypoints on images
                        tracking_frame.draw_keypoints_on_image(left_img, 'left')
                        tracking_frame.draw_keypoints_on_image(right_img, 'right')
                        
                        # Add text overlay with frame information
                        left_kp_count = len(tracking_frame.left_keypoints)
                        right_kp_count = len(tracking_frame.right_keypoints)
                        
                        text_left = f"Left {left_frame.width}x{left_frame.height} KP:{left_kp_count}"
                        text_right = f"Right {right_frame.width}x{right_frame.height} KP:{right_kp_count}"
                        
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
                        
                        # Add component info
                        cv2.putText(left_img, "Component-based SDK", (10, left_img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
                        
                        # Concatenate left and right images side by side
                        combined_img = np.hstack((left_img, right_img))
                        
                        # Display the combined image
                        cv2.imshow("Aurora Camera Preview (Component-based)", combined_img)
                        
                    else:
                        # No tracking frame available, show waiting message
                        wait_img = np.zeros((240, 640, 3), dtype=np.uint8)
                        cv2.putText(wait_img, "Waiting for tracking data...", (150, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        cv2.imshow("Aurora Camera Preview (Component-based)", wait_img)
                    
                except DataNotReadyError:
                    # Data not ready, show waiting message
                    wait_img = np.zeros((240, 640, 3), dtype=np.uint8)
                    cv2.putText(wait_img, "Tracking data not ready...", (180, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.imshow("Aurora Camera Preview (Component-based)", wait_img)
                except Exception as e:
                    print(f"Error getting tracking frame: {e}")
                    # Show error message
                    wait_img = np.zeros((240, 640, 3), dtype=np.uint8)
                    cv2.putText(wait_img, f"Error: {str(e)[:50]}", (50, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.imshow("Aurora Camera Preview (Component-based)", wait_img)
                
                # Check for key presses
                key = cv2.waitKey(10) & 0xFF
                if key == 27:  # ESC key
                    break
                elif key == ord(' '):  # Space key - show info
                    try:
                        # Get pose via DataProvider
                        position, rotation, timestamp = self.sdk.data_provider.get_current_pose(use_se3=True)
                        print(f"Current pose=({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}), "
                              f"rot=({rotation[0]:.3f}, {rotation[1]:.3f}, {rotation[2]:.3f}, {rotation[3]:.3f})")
                        
                        # Show device status
                        status = self.sdk.get_device_status()
                        print(f"Device status: connected={status['connected']}, session_active={status['session_active']}")
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
            # Cleanup using context manager-like behavior
            if OPENCV_AVAILABLE:
                cv2.destroyAllWindows()
            if self.sdk:
                print("Disconnecting...")
                try:
                    if self.sdk.is_connected():
                        self.sdk.disconnect()
                except:
                    pass
            print("Demo finished.")
        
        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Frame Preview Demo (Component-based SDK) - Display camera frames with keypoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python frame_preview_v2.py                    # Auto-discover and connect
    python frame_preview_v2.py 192.168.1.212     # Connect to specific IP

Features:
    - Component-based SDK architecture
    - Controller for device management
    - DataProvider for data retrieval
    - Automatic keypoint rendering
    - Device status information

Controls:
    ESC    - Exit the demo
    Space  - Show current pose and device status
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    
    args = parser.parse_args()
    
    demo = FramePreviewDemo()
    return demo.run(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())