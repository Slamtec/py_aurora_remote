#!/usr/bin/env python3
"""
Simple Map Render Example - No OpenCV dependency

This example demonstrates map functionality without requiring OpenCV.
"""

import sys
import time
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

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError = setup_sdk_import()

def simple_map_demo(connection_string=None):
    """Simple map demonstration without OpenCV.

    Args:
        connection_string: IP address or connection string. If None, auto-discover.
    """
    try:
        # Create SDK instance
        print("Creating Aurora SDK instance...")
        sdk = AuroraSDK()

        # Print version info
        version_info = sdk.get_version_info()
        print(f"Aurora SDK Version: {version_info['version_string']}")

        # Session created automatically
        print("SDK session created automatically...")

        # Connect to device
        if connection_string:
            print(f"Connecting to device at {connection_string}...")
            sdk.connect(connection_string=connection_string)
        else:
            print("Discovering devices...")
            devices = sdk.discover_devices(timeout=5.0)
            if not devices:
                print("No devices found!")
                return 1
            print(f"Found device: {devices[0].device_address}")
            sdk.connect(device_info=devices[0])
        print("Connected!")
        
        # Get device info
        device_info = sdk.get_device_info()
        print(f"Device Name: {device_info.device_name}")
        print(f"Device Model: {device_info.device_model_string}")
        
        # Get map info
        print("\nGetting map info...")
        map_info = sdk.get_map_info()
        print(f"Map Info: {map_info}")
        
        # Start LIDAR 2D map preview
        print("\nStarting LIDAR 2D map preview...")
        sdk.start_lidar_2d_map_preview(resolution=0.05)
        print("LIDAR 2D map preview started")
        
        # Monitor data for a short time
        print("\nMonitoring data for 10 seconds...")
        pose_count = 0
        scan_count = 0
        
        for i in range(20):  # 10 seconds at 0.5s intervals
            try:
                # Get current pose
                position, rotation, timestamp = sdk.get_current_pose(use_se3=True)
                pose_count += 1
                if i % 4 == 0:  # Print every 2 seconds
                    print(f"Pose: {position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}")
            except DataNotReadyError:
                pass
            except Exception as e:
                print(f"Pose error: {e}")
            
            try:
                # Try to get LiDAR scan
                scan_data = sdk.get_recent_lidar_scan()
                if scan_data is not None:
                    scan_count += 1
                    if i % 4 == 0:  # Print every 2 seconds
                        print(f"LiDAR scan: {len(scan_data.points)} points")
            except DataNotReadyError:
                pass
            except Exception as e:
                if i % 10 == 0:  # Print error occasionally
                    print(f"LiDAR scan not ready: {e}")
            
            time.sleep(0.5)
        
        print(f"\nSummary:")
        print(f"  Pose updates: {pose_count}")
        print(f"  LiDAR scans: {scan_count}")
        
        # Stop LIDAR 2D map preview
        print("\nStopping LIDAR 2D map preview...")
        sdk.stop_lidar_2d_map_preview()
        print("LIDAR 2D map preview stopped")
        
        # Cleanup
        print("\nCleaning up...")
        sdk.disconnect()
        sdk.release()
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Get connection string from command line argument
    connection_string = sys.argv[1] if len(sys.argv) > 1 else None

    if connection_string:
        print(f"Using specified connection: {connection_string}")
    else:
        print("No connection specified, will auto-discover device")

    sys.exit(simple_map_demo(connection_string))