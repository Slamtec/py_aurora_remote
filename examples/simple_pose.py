#!/usr/bin/env python3
"""
Simple Pose Example

This example demonstrates how to connect to an Aurora device and retrieve pose data.
It's the Python equivalent of the simple_pose C++ demo.

Usage:
    python simple_pose.py [connection_string]
    
Example:
    python simple_pose.py 192.168.1.212
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

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError = setup_sdk_import()


class SimplePoseDemo:
    """Simple pose demonstration class."""
    
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
    
    def run(self, connection_string = None):
        """
        Run the simple pose demo.
        
        Args:
            connection_string connection string (e.g., "192.168.1.212")
        """
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
                print(f"Firmware Version: {device_info.firmware_version}")
                print(f"Hardware Version: {device_info.hardware_version}")
                print(f"Serial Number: {device_info.serial_number}")
            except Exception as e:
                print(f"Warning: Could not get device info: {e}")
            
            print("\nWaiting for device to be ready...")
            # Give the device some time to initialize and start providing data
            time.sleep(2.0)
            
            print("Starting pose monitoring (Ctrl+C to exit)...")
            print("Pose format: x, y, z, qx, qy, qz, qw")
            
            pose_retry_count = 0
            max_pose_retries = 50  # 5 seconds of retries
            
            # Main pose monitoring loop
            while self.running:
                try:
                    # Get current pose in SE3 format (recommended)
                    position, rotation, timestamp = self.sdk.get_current_pose(use_se3=True)
                    
                    # Print pose data
                    print(f"Pose: {position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}, "
                          f"{rotation[0]:.3f}, {rotation[1]:.3f}, {rotation[2]:.3f}, {rotation[3]:.3f}")
                    
                    # Reset retry count on successful pose read
                    pose_retry_count = 0
                    
                except DataNotReadyError:
                    pose_retry_count += 1
                    if pose_retry_count <= max_pose_retries:
                        if pose_retry_count % 10 == 1:  # Print every second
                            print(f"Pose data not ready, waiting... (attempt {pose_retry_count}/{max_pose_retries})")
                    else:
                        print("Pose data not available after maximum retries. Device may not be tracking.")
                        break
                except Exception as e:
                    print(f"Error getting pose: {e}")
                    pose_retry_count += 1
                    if pose_retry_count > max_pose_retries:
                        print("Too many pose errors, stopping.")
                        break
                
                # Wait before next update
                time.sleep(0.1)  # 10 Hz update rate
                
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
            if self.sdk:
                print("Disconnecting...")
                self.sdk.disconnect()
                self.sdk.release()
            print("Demo finished.")
        
        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Simple Pose Demo - Get pose data from Aurora device",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python simple_pose.py                    # Auto-discover and connect
    python simple_pose.py 192.168.1.212     # Connect to specific IP
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    
    args = parser.parse_args()
    
    demo = SimplePoseDemo()
    return demo.run(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())