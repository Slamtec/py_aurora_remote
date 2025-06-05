#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - IMU Data Fetcher

This demo shows how to get IMU data from the Aurora device.
It continuously prints IMU data (accelerometer and gyroscope) to the terminal.

Based on the C++ imu_fetcher demo.

Features:
- Retrieves cached IMU data from the device
- Displays accelerometer and gyroscope readings
- Real-time continuous monitoring
- Duplicate timestamp filtering
- Command-line interface with device discovery

Requirements:
- Aurora device with IMU sensor support
- Device running Aurora SDK 2.0
"""

import sys
import os
import time
import signal
import argparse
from datetime import datetime

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, AuroraSDKError, DataNotReadyError)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.exceptions import AuroraSDKError, DataNotReadyError
        return AuroraSDK, AuroraSDKError, DataNotReadyError
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.exceptions import AuroraSDKError, DataNotReadyError
        return AuroraSDK, AuroraSDKError, DataNotReadyError

# Setup SDK import
AuroraSDK, AuroraSDKError, DataNotReadyError = setup_sdk_import()

# Global flag for Ctrl+C handling
is_ctrl_c = False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    global is_ctrl_c
    print("\nCtrl-C pressed, exiting...")
    is_ctrl_c = True

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

def check_imu_support(sdk):
    """Check if the device supports IMU."""
    try:
        device_info = sdk.data_provider.getLastDeviceBasicInfo()
        if device_info.isSupportIMU():
            print("✓ Device supports IMU sensor")
            return True
        else:
            print("✗ Device does not support IMU sensor")
            return False
    except Exception as e:
        print(f"Warning: Could not check IMU support: {e}")
        return True  # Assume supported and let it fail later if not

def format_imu_data(imu_data):
    """Format IMU data for display."""
    acc = imu_data.get_acceleration()
    gyro = imu_data.get_gyroscope()
    timestamp = imu_data.get_timestamp_seconds()
    
    return (f"IMU Data: "
            f"Accel: {acc[0]:8.4f}, {acc[1]:8.4f}, {acc[2]:8.4f} (g) | "
            f"Gyro: {gyro[0]:8.4f}, {gyro[1]:8.4f}, {gyro[2]:8.4f} (dps) | "
            f"Time: {timestamp:.3f}s")

def main():
    """Main function."""
    global is_ctrl_c
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Aurora IMU Data Fetcher Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch IMU data using auto-discovery
  python3 imu_fetcher.py
  
  # Connect to specific device
  python3 imu_fetcher.py 192.168.1.212
  
  # Adjust update rate to 50 Hz
  python3 imu_fetcher.py --rate 50
  
  # Force execution even if IMU not detected
  python3 imu_fetcher.py --force
        """
    )
    
    parser.add_argument('device', nargs='?', 
                       help='Aurora device IP address (default: auto-discover)')
    parser.add_argument('--rate', '-r', type=float, default=10.0,
                       help='Update rate in Hz (default: 10.0)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with timestamps and IDs')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force execution even if IMU not detected')
    
    args = parser.parse_args()
    
    # Use fixed 100ms interval like C++ version for optimal performance
    sleep_interval = 0.1  # 100ms like C++ version
    
    # Use buffer size that ensures we consume enough of the circular buffer to reach new data
    # Small buffers (1-10) may only return old data from the circular buffer
    batch_size = 100  # Optimal size to consistently get new data from circular buffer
    
    print("=" * 80)
    print("Aurora IMU Data Fetcher Demo")
    print("=" * 80)
    print(f"Device: {args.device if args.device else 'Auto-discover'}")
    print(f"Update rate: {1/sleep_interval:.1f} Hz ({sleep_interval*1000:.0f}ms interval - matches C++)")
    print(f"Buffer size: {batch_size} samples (optimal for circular buffer)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Initialize SDK
    print("Initializing Aurora SDK...")
    sdk = AuroraSDK()
    
    try:
        
        # Connect to device
        if args.device:
            # Connect to specific device
            print(f"Connecting to device at {args.device}...")
            sdk.connect(connection_string=args.device)
            print("Connected successfully!")
        else:
            # Discover and connect to first available device
            print("Device connection string not provided, trying to discover Aurora devices...")
            print("Waiting for Aurora devices...")
            time.sleep(5)  # Wait for discovery like C++ version
            
            device_info = discover_and_select_device(sdk)
            if not device_info:
                print("Failed to discover Aurora devices")
                return 1
            
            print("Connecting to the selected device...")
            sdk.connect(device_info=device_info)
            print("Connected to the selected device")
        
        # Check IMU support
        imu_supported = check_imu_support(sdk)
        if not imu_supported:
            print("Warning: Device does not report IMU support.")
            print("Continuing anyway to test the API...")
        
        # Test IMU data availability
        print("Testing IMU data availability...")
        try:
            test_samples = sdk.data_provider.peek_imu_data(max_count=1)
            if len(test_samples) == 0:
                print("No IMU data available from device.")
                print("This may indicate:")
                print("- Device lacks IMU hardware")
                print("- IMU sensor is not enabled")
                print("- Device needs to be calibrated or started")
                if not args.force:
                    response = input("Continue anyway to demonstrate API? (y/N): ").strip().lower()
                    if response != 'y':
                        return 1
                else:
                    print("Force mode enabled, continuing anyway...")
        except Exception as e:
            print(f"IMU test failed: {e}")
            return 1
        
        # Main IMU data fetching loop - simplified like C++ version
        print("\nStarting IMU data fetching...")
        print("Press Ctrl+C to exit\n")
        
        if args.verbose:
            print("Format: IMU(id=X, timestamp, accel_xyz, gyro_xyz)")
        else:
            print("Format: Accel(x,y,z) in g | Gyro(x,y,z) in dps")
        print("-" * 80)
        
        last_timestamp = 0
        total_samples = 0
        start_time = time.time()
        
        while not is_ctrl_c:
            try:
                # Get IMU data from circular buffer
                imu_data_list = sdk.data_provider.peek_imu_data(max_count=batch_size)
                
                # Process each IMU sample, filtering out old data
                for imu_data in imu_data_list:
                    # Skip old data that has been fetched before (normal circular buffer behavior)
                    if imu_data.timestamp_ns <= last_timestamp:
                        continue
                    
                    # This is new data
                    last_timestamp = imu_data.timestamp_ns
                    total_samples += 1
                    
                    # Display IMU data immediately
                    if args.verbose:
                        print(f"{imu_data}")
                    else:
                        print(format_imu_data(imu_data))
                
            except AuroraSDKError as e:
                print(f"Failed to get IMU data: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            
            # Sleep 100ms like C++ version
            time.sleep(0.1)
        
        # Display statistics
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            avg_rate = total_samples / elapsed_time
            print(f"\n" + "=" * 80)
            print(f"Statistics:")
            print(f"  Total samples: {total_samples}")
            print(f"  Elapsed time: {elapsed_time:.1f}s")
            print(f"  Average rate: {avg_rate:.1f} Hz")
            print("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except AuroraSDKError as e:
        print(f"\nAurora SDK Error: {e}")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1
    finally:
        # Cleanup
        try:
            if sdk.is_connected():
                sdk.disconnect()
            sdk.release()
            print("Disconnected from device")
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())