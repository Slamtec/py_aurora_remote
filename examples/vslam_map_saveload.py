#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - VSLAM Map Save/Load

This demo shows how to download or upload VSLAM maps from/to the Aurora device.
Based on the C++ vslam_map_saveload demo.

Features:
- Download VSLAM maps from Aurora device to local files
- Upload VSLAM maps from local files to Aurora device
- Real-time progress monitoring during transfer
- Async operation with callback support
- Command-line interface with device discovery

Requirements:
- Aurora device with VSLAM map storage support
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
    print("\\nCtrl-C pressed, aborting operation...")
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

def progress_callback(status):
    """Progress callback for map storage operations."""
    print(f"\rProgress: {status.progress:.1f}% [{status.get_status_string()}]", end="", flush=True)

def download_vslam_map(sdk, map_file):
    """Download VSLAM map from Aurora device."""
    print(f"Downloading VSLAM map to {map_file}")
    
    # Use MapManager for async map download
    map_manager = sdk.map_manager
    
    try:
        # Start download session
        if not map_manager.start_download_session(map_file):
            print("Failed to start download session")
            return False
        
        # Monitor progress until completion
        while map_manager.is_session_active():
            if is_ctrl_c:
                print("\nAborting download session...")
                map_manager.abort_session()
                return False
            
            # Get and display progress
            try:
                status = map_manager.query_session_status()
                progress_callback(status)
            except Exception as e:
                print(f"\nFailed to query session status: {e}")
                return False
            
            time.sleep(1)
        
        # Session is no longer active, determine final result
        try:
            final_status = map_manager.query_session_status()
            result = final_status.is_finished()
            print(f"\nDownloading VSLAM map {'succeeded' if result else 'failed'}")
            
            # If failed, show more info
            if not result:
                print(f"Final status: {final_status.get_status_string()}, progress: {final_status.progress}%")
        except Exception as e:
            print(f"\nFailed to determine final result: {e}")
            result = False
        
        return result
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def upload_vslam_map(sdk, map_file):
    """Upload VSLAM map to Aurora device."""
    print(f"Uploading VSLAM map from {map_file}")
    
    # Check if file exists
    if not os.path.exists(map_file):
        print(f"Error: Map file '{map_file}' does not exist")
        return False
    
    # Use MapManager for async map upload
    map_manager = sdk.map_manager
    
    try:
        # Start upload session
        if not map_manager.start_upload_session(map_file):
            print("Failed to start upload session")
            return False
        
        # Monitor progress until completion
        while map_manager.is_session_active():
            if is_ctrl_c:
                print("\nAborting upload session...")
                map_manager.abort_session()
                return False
            
            # Get and display progress
            try:
                status = map_manager.query_session_status()
                progress_callback(status)
            except Exception as e:
                print(f"\nFailed to query session status: {e}")
                return False
            
            time.sleep(1)
        
        # Session is no longer active, determine final result
        try:
            final_status = map_manager.query_session_status()
            result = final_status.is_finished()
            print(f"\nUploading VSLAM map {'succeeded' if result else 'failed'}")
            
            # If failed, show more info
            if not result:
                print(f"Final status: {final_status.get_status_string()}, progress: {final_status.progress}%")
        except Exception as e:
            print(f"\nFailed to determine final result: {e}")
            result = False
        
        return result
        
    except Exception as e:
        print(f"\nUpload failed: {e}")
        return False

def show_help():
    """Show usage help."""
    help_text = """
Usage: vslam_map_saveload.py [options] [-s <server_locator>] [map_file]

Options:
  -h, --help            Show this help message
  -s, --server          The server locator of the aurora device
                        Format: tcp://IP:PORT or just IP address
                        If not specified, auto-discovery will be used
  -d, --download        Download the VSLAM map from the aurora device (default)
  -u, --upload          Upload the VSLAM map to the aurora device
  [map_file]            The map file to be downloaded or uploaded
                        Default: auroramap.stcm

Examples:
  # Download map using auto-discovery
  python3 vslam_map_saveload.py -d my_map.stcm
  
  # Upload map to specific device
  python3 vslam_map_saveload.py -s 192.168.1.212 -u existing_map.stcm
  
  # Download with default filename
  python3 vslam_map_saveload.py -d
"""
    print(help_text)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Aurora VSLAM Map Save/Load Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download map using auto-discovery
  python3 vslam_map_saveload.py -d my_map.stcm
  
  # Upload map to specific device  
  python3 vslam_map_saveload.py -s 192.168.1.212 -u existing_map.stcm
  
  # Download with default filename
  python3 vslam_map_saveload.py -d
        """
    )
    
    parser.add_argument('-s', '--server', type=str, 
                       help='Aurora device IP address or locator (default: auto-discover)')
    parser.add_argument('-d', '--download', action='store_true',
                       help='Download VSLAM map from Aurora device')
    parser.add_argument('-u', '--upload', action='store_true',
                       help='Upload VSLAM map to Aurora device')
    parser.add_argument('map_file', nargs='?', default='auroramap.stcm',
                       help='Map file path (default: auroramap.stcm)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.download and args.upload:
        parser.error("Cannot specify both --download and --upload")
    
    if not args.download and not args.upload:
        # Default to download
        args.download = True
        print("No operation specified, defaulting to download")
    
    return args

def main():
    """Main function."""
    global is_ctrl_c
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    args = parse_arguments()
    
    print("=" * 60)
    print("Aurora VSLAM Map Save/Load Demo")
    print("=" * 60)
    print(f"Operation: {'Download' if args.download else 'Upload'}")
    print(f"Map file: {args.map_file}")
    print(f"Device: {args.server if args.server else 'Auto-discover'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize SDK
    print("Initializing Aurora SDK...")
    sdk = AuroraSDK()
    
    try:
        # Session created automatically
        print("Session created automatically...")
        
        # Connect to device
        if args.server:
            # Connect to specific device
            print(f"Connecting to device at {args.server}...")
            sdk.connect(connection_string=args.server)
            print("Connected successfully!")
        else:
            # Discover and connect to first available device
            device_info = discover_and_select_device(sdk)
            if not device_info:
                print("No Aurora devices found. Please ensure device is powered on and network accessible.")
                return 1
            
            print("Connecting to discovered device...")
            sdk.connect(device_info=device_info)
            print("Connected successfully!")
        
        # Perform requested operation
        success = False
        if args.download:
            success = download_vslam_map(sdk, args.map_file)
        elif args.upload:
            success = upload_vslam_map(sdk, args.map_file)
        
        # Display results
        print("\n" + "=" * 60)
        if success:
            operation = "Download" if args.download else "Upload"
            print(f"{operation} completed successfully!")
            if args.download and os.path.exists(args.map_file):
                file_size = os.path.getsize(args.map_file)
                print(f"Map file size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        else:
            print("Operation failed!")
        print("=" * 60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
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