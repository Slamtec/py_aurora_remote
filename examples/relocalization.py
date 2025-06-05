#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - Relocalization

This demo shows how to perform relocalization with the Aurora device.
Relocalization allows the device to determine its position within a previously built map.

Based on the C++ relocalization demo.

Features:
- Connects to Aurora device
- Performs relocalization operation
- Reports success or failure
- Command-line interface with device discovery

Requirements:
- Aurora device with existing map data
- Device running Aurora SDK 2.0
- Previously built VSLAM map loaded on the device
"""

import sys
import os
import signal
import argparse
from datetime import datetime

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

def check_vslam_support(sdk):
    """Check if the device supports VSLAM."""
    try:
        device_info = sdk.data_provider.getLastDeviceBasicInfo()
        if device_info.isSupportVSLAM():
            print("✓ Device supports VSLAM")
            return True
        else:
            print("✗ Device does not support VSLAM")
            return False
    except Exception as e:
        print(f"Warning: Could not check VSLAM support: {e}")
        return True  # Assume supported and let it fail later if not

def main():
    """Main function."""
    global is_ctrl_c
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Aurora Relocalization Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Perform relocalization using auto-discovery
  python3 relocalization.py
  
  # Connect to specific device
  python3 relocalization.py 192.168.1.212
  
  # Use custom timeout
  python3 relocalization.py --timeout 10000
        """
    )
    
    parser.add_argument('device', nargs='?', 
                       help='Aurora device IP address (default: auto-discover)')
    parser.add_argument('--timeout', '-t', type=int, default=5000,
                       help='Relocalization timeout in milliseconds (default: 5000)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with additional information')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Aurora Relocalization Demo")
    print("=" * 60)
    print(f"Device: {args.device if args.device else 'Auto-discover'}")
    print(f"Timeout: {args.timeout}ms ({args.timeout/1000.0}s)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize SDK
    print("Initializing Aurora SDK...")
    sdk = AuroraSDK()
    
    try:
        # Print SDK version info
        if args.verbose:
            try:
                version_info = sdk.controller.get_version_info()
                print(f"Aurora SDK Version: {version_info}")
            except Exception as e:
                print(f"Could not get SDK version: {e}")
        
        # Session created automatically
        print("Session created automatically...")
        
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
            import time
            time.sleep(5)  # Wait for discovery like C++ version
            
            device_info = discover_and_select_device(sdk)
            if not device_info:
                print("Failed to discover Aurora devices")
                return 1
            
            print("Connecting to the selected device...")
            sdk.connect(device_info=device_info)
            print("Connected to the selected device")
        
        # Check VSLAM support
        if args.verbose and not check_vslam_support(sdk):
            print("Warning: Device may not support VSLAM. Continuing anyway...")
        
        # Get device information
        if args.verbose:
            try:
                device_info = sdk.data_provider.getLastDeviceBasicInfo()
                print(f"Device Model: {device_info.getModelString()}")
                print(f"Firmware Version: {device_info.getFirmwareVersionString()}")
                features = []
                if device_info.isSupportVSLAM():
                    features.append("VSLAM")
                if device_info.isSupportCoMap():
                    features.append("CoMap")
                if device_info.isSupportLiDAR():
                    features.append("LiDAR")
                if device_info.isSupportIMU():
                    features.append("IMU")
                print(f"Supported Features: {', '.join(features) if features else 'None detected'}")
            except Exception as e:
                print(f"Could not get device info: {e}")
        
        print("\n" + "=" * 60)
        print("Starting relocalization...")
        print("=" * 60)
        
        # Perform relocalization
        try:
            print(f"Requesting relocalization (timeout: {args.timeout}ms)...")
            success = sdk.controller.require_relocalization(timeout_ms=args.timeout)
            
            print("\n" + "=" * 60)
            if success:
                print("✓ Relocalization succeeded!")
                print("The device has successfully determined its position in the map.")
            else:
                print("✗ Relocalization failed!")
                print("The device could not determine its position in the map.")
                print("\nPossible reasons:")
                print("- No existing map loaded on the device")
                print("- Current location not recognizable in the existing map")
                print("- Environmental conditions have changed significantly")
                print("- Device sensors need calibration")
            print("=" * 60)
            
            return 0 if success else 1
            
        except AuroraSDKError as e:
            print(f"\nRelocalization operation failed: {e}")
            print("=" * 60)
            return 1
        except Exception as e:
            print(f"\nUnexpected error during relocalization: {e}")
            print("=" * 60)
            return 1
        
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