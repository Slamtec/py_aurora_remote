#!/usr/bin/env python3
"""
Context Manager Demo

This example demonstrates how to use the AuroraSDK with Python's context manager
to ensure proper cleanup of resources even if an exception occurs.

The context manager automatically calls:
- sdk.disconnect() if connected
- sdk.release() to clean up the session

Usage:
    python context_manager_demo.py [connection_string]
    
Example:
    python context_manager_demo.py 192.168.1.212
"""

import sys
import time
import argparse
import os

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, AuroraSDKError, ConnectionError)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK, AuroraSDKError, ConnectionError
        return AuroraSDK, AuroraSDKError, ConnectionError
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK, AuroraSDKError, ConnectionError
        return AuroraSDK, AuroraSDKError, ConnectionError

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError = setup_sdk_import()


def run_demo(connection_string=None):
    """
    Run the context manager demo.
    
    Args:
        connection_string: Optional connection string (e.g., "192.168.1.212")
    """
    print("=== Aurora SDK Context Manager Demo ===")
    print("This demo shows how to use AuroraSDK with automatic cleanup.")
    print()
    
    # Using context manager ensures automatic cleanup
    with AuroraSDK() as sdk:
        try:
            # Connect to device
            if connection_string:
                print(f"1. Connecting to {connection_string}...")
                sdk.connect(connection_string=connection_string)
            else:
                print("1. Auto-discovering devices...")
                devices = sdk.discover_devices(timeout=5.0)
                if not devices:
                    print("❌ No Aurora devices found")
                    return 1
                
                print(f"Found {len(devices)} device(s), connecting to first one...")
                sdk.connect(device_info=devices[0])
            
            print("✅ Connected successfully!")
            
            # Get device info
            try:
                device_info = sdk.get_device_info()
                print(f"Device: {device_info.device_name} (FW: {device_info.firmware_version})")
            except Exception as e:
                print(f"Warning: Could not get device info: {e}")
            
            print()
            print("2. Getting pose data for 5 seconds...")
            print("Format: x, y, z, qx, qy, qz, qw")
            
            # Get pose data for a few seconds
            start_time = time.time()
            pose_count = 0
            
            while time.time() - start_time < 5.0:
                try:
                    position, rotation, timestamp = sdk.get_current_pose(use_se3=True)
                    print(f"Pose {pose_count:3d}: {position[0]:7.3f}, {position[1]:7.3f}, {position[2]:7.3f}, "
                          f"{rotation[0]:6.3f}, {rotation[1]:6.3f}, {rotation[2]:6.3f}, {rotation[3]:6.3f}")
                    pose_count += 1
                    time.sleep(0.1)  # 10 Hz
                    
                except Exception as e:
                    if "NOT_READY" not in str(e):
                        print(f"Pose error: {e}")
                    time.sleep(0.1)
            
            print(f"✅ Retrieved {pose_count} pose samples")
            
            # Intentionally cause an exception to test cleanup
            if False:  # Set to True to test exception handling
                raise Exception("Test exception to verify cleanup works")
            
            print("✅ Demo completed successfully!")
            return 0
            
        except ConnectionError as e:
            print(f"❌ Connection error: {e}")
            return 1
        except AuroraSDKError as e:
            print(f"❌ Aurora SDK error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1
    
    # Note: No need for explicit cleanup here - the context manager handles it!
    print("🔧 Cleanup completed automatically by context manager")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Context Manager Demo - Automatic resource cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python context_manager_demo.py                    # Auto-discover device
    python context_manager_demo.py 192.168.1.212     # Connect to specific IP

Benefits of using context manager:
    - Automatic cleanup even if exceptions occur
    - Cleaner code without explicit try/finally blocks
    - Guaranteed resource release
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    
    args = parser.parse_args()
    return run_demo(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())