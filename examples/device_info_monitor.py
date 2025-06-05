#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - Device Information Monitor

This demo shows how to continuously monitor device basic information.
Features:
- Retrieve device name, serial number, firmware/hardware versions
- Monitor device model, feature set, and uptime
- Continuous real-time updates in console
- Clean formatted output with timestamps
- Optional JSON export of device information

Requirements:
- Aurora device with SDK 2.0 support
"""

import sys
import os
import time
import signal
import argparse
import json
import threading
import queue
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

# Global variables
is_ctrl_c = False
input_queue = queue.Queue()

# Cross-platform keyboard input handling
try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    import select  # Unix/Linux/Mac
    import tty
    import termios
    WINDOWS = False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    global is_ctrl_c
    print("\nCtrl-C pressed, exiting...")
    is_ctrl_c = True

def get_char_windows():
    """Get single character input on Windows."""
    if msvcrt.kbhit():
        return msvcrt.getch().decode('utf-8').upper()
    return None

def get_char_unix():
    """Get single character input on Unix/Linux/Mac."""
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        char = sys.stdin.read(1)
        # Handle Enter key (carriage return/newline)
        if char in ['\r', '\n']:
            return '\n'  # Normalize to newline
        return char.upper()
    return None

def keyboard_input_thread():
    """Thread function to handle keyboard input."""
    global is_ctrl_c
    
    # Check if we have a proper terminal
    if not sys.stdin.isatty():
        return  # Don't try to read keyboard input if not in a terminal
    
    if WINDOWS:
        while not is_ctrl_c:
            char = get_char_windows()
            if char:
                input_queue.put(char)
            time.sleep(0.01)  # Small delay to prevent busy waiting
    else:
        # Unix/Linux setup for non-blocking input
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())  # Use cbreak instead of raw mode
            while not is_ctrl_c:
                char = get_char_unix()
                if char:
                    input_queue.put(char)
                time.sleep(0.01)  # Small delay to prevent busy waiting
        except (termios.error, OSError):
            # Not a proper terminal, skip keyboard input
            return
        finally:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass

def process_user_input(show_detailed, basic_info, timestamp_ns, update_count):
    """Process user keyboard input and return updated state."""
    commands_processed = []
    
    while not input_queue.empty():
        try:
            char = input_queue.get_nowait()
            commands_processed.append(char)
            
            # Handle Enter key - just continue without processing
            if char == '\n':
                continue
                
            if char == 'D':
                show_detailed = not show_detailed
                status = "enabled" if show_detailed else "disabled"
                print(f"\n[Detailed view {status}]")
                
            elif char == 'S' and basic_info:
                filename = f"device_info_{update_count}.json"
                if export_device_info_json(basic_info, timestamp_ns, filename):
                    print(f"\n[Device info saved to {filename}]")
                else:
                    print(f"\n[Failed to save device info]")
                    
            elif char == 'H':
                print("\n")
                display_help()
                print("\n[Press any key to continue...]")
                
            elif char == 'R':
                # Clear screen for reset
                if os.name == 'nt':  # Windows
                    os.system('cls')
                else:  # Unix/Linux/Mac
                    os.system('clear')
                print("[Display reset]")
                
            elif char == 'Q':
                global is_ctrl_c
                is_ctrl_c = True
                print("\n[Quit requested]")
                
        except queue.Empty:
            break
    
    return show_detailed, commands_processed

def format_uptime(uptime_us):
    """Format uptime from microseconds to human readable format."""
    uptime_seconds = uptime_us // 1_000_000
    
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    if days > 0:
        return f"{days}d {hours:02d}h {minutes:02d}m {seconds:02d}s"
    elif hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    elif minutes > 0:
        return f"{minutes}m {seconds:02d}s"
    else:
        return f"{seconds}s"

def format_feature_bitmaps(hw_features, sensing_features, sw_features):
    """Format feature bitmaps into readable strings."""
    from slamtec_aurora_sdk.data_types import (
        SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_LIDAR,
        SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_IMU,
        SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_STEREO_CAMERA,
        SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_VSLAM,
        SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_COMAP,
        SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_STEREO_DENSE_DISPARITY,
        SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_SEMANTIC_SEGMENTATION,
        SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_CAMERA_PREVIEW_STREAM,
        SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_ENHANCED_IMAGING
    )
    
    feature_info = []
    
    # Hardware features
    if hw_features & SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_STEREO_CAMERA:
        feature_info.append("Stereo Camera")
    if hw_features & SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_LIDAR:
        feature_info.append("LiDAR")
    if hw_features & SLAMTEC_AURORA_SDK_HW_FEATURE_BIT_IMU:
        feature_info.append("IMU")
    
    # Sensing features
    if sensing_features & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_VSLAM:
        feature_info.append("VSLAM")
    if sensing_features & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_COMAP:
        feature_info.append("CoMap")
    if sensing_features & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_STEREO_DENSE_DISPARITY:
        feature_info.append("Depth Camera")
    if sensing_features & SLAMTEC_AURORA_SDK_SENSING_FEATURE_BIT_SEMANTIC_SEGMENTATION:
        feature_info.append("Semantic Segmentation")
    
    # Software features
    if sw_features & SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_ENHANCED_IMAGING:
        feature_info.append("Enhanced Imaging")
    if sw_features & SLAMTEC_AURORA_SDK_SW_FEATURE_BIT_CAMERA_PREVIEW_STREAM:
        feature_info.append("Camera Preview")
    
    return feature_info if feature_info else ["Standard Features"]

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

def connect_to_device(sdk, device_info):
    """Connect to Aurora device."""
    try:
        print(f"Connecting to device...")
        sdk.connect(device_info=device_info)
        print("Connected successfully!")
        return True
        
    except AuroraSDKError as e:
        print(f"Failed to connect to device: {e}")
        return False

def get_device_basic_info(sdk):
    """Get device basic information."""
    try:
        # Use the data provider to get device basic info
        device_basic_info = sdk.data_provider.get_last_device_basic_info()
        
        # Return the underlying C structure and timestamp
        return device_basic_info._c_struct, device_basic_info._timestamp_ns
        
    except AuroraSDKError as e:
        print(f"Warning: Failed to get device basic info: {e}")
        return None, 0
    except Exception as e:
        print(f"Error getting device basic info: {e}")
        return None, 0

def format_device_info(basic_info, timestamp_ns, detailed=False):
    """Format device information for display."""
    if basic_info is None:
        return "Device information not available"
    
    # Extract device name
    device_name = basic_info.device_name.decode('utf-8').rstrip('\0')
    if not device_name:
        device_name = "Unknown Device"
    
    # Extract firmware version
    firmware_version = basic_info.firmware_version_string.decode('utf-8').rstrip('\0')
    firmware_build_date = basic_info.firmware_build_date.decode('utf-8').rstrip('\0')
    firmware_build_time = basic_info.firmware_build_time.decode('utf-8').rstrip('\0')
    
    # Generate device model string
    if basic_info.model_major == 0 and basic_info.model_sub == 0:
        device_model = "A1M1"
    else:
        device_model = f"A{basic_info.model_major}M{basic_info.model_sub}"
    
    if basic_info.model_revision:
        device_model += f"-r{basic_info.model_revision}"
    
    # Generate hardware version
    hardware_version = f"{basic_info.model_major}.{basic_info.model_sub}.{basic_info.model_revision}"
    
    # Convert serial number from uint8 array to hex string
    serial_bytes = bytes(basic_info.device_sn)
    serial_number = ''.join(f'{b:02X}' for b in serial_bytes).rstrip('00')
    if not serial_number:
        serial_number = "N/A"
    
    # Format uptime
    uptime_str = format_uptime(basic_info.device_uptime_us)
    
    # Get timestamp - use current time if timestamp is device uptime rather than absolute time
    if timestamp_ns > 0 and timestamp_ns > 1_000_000_000_000_000_000:  # Check if it's a reasonable absolute timestamp
        timestamp_s = timestamp_ns / 1_000_000_000
        timestamp_str = datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    else:
        # If timestamp is not absolute, use current time
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Basic info
    info_lines = [
        f"Device Name:        {device_name}",
        f"Device Model:       {device_model}",
        f"Serial Number:      {serial_number}",
        f"Firmware Version:   {firmware_version}",
        f"Hardware Version:   {hardware_version}",
        f"Device Uptime:      {uptime_str}",
        f"Last Update:        {timestamp_str}"
    ]
    
    if detailed:
        # Detailed info
        feature_list = format_feature_bitmaps(
            basic_info.hwfeature_bitmaps,
            basic_info.sensing_feature_bitmaps,
            basic_info.swfeature_bitmaps
        )
        
        info_lines.extend([
            f"",
            f"Detailed Information:",
            f"  Model Numbers:    {basic_info.model_major}.{basic_info.model_sub}.{basic_info.model_revision}",
            f"  Build Date:       {firmware_build_date}",
            f"  Build Time:       {firmware_build_time}",
            f"  HW Features:      0x{basic_info.hwfeature_bitmaps:016X}",
            f"  Sensing Features: 0x{basic_info.sensing_feature_bitmaps:016X}",
            f"  SW Features:      0x{basic_info.swfeature_bitmaps:016X}",
            f"  Features:         {', '.join(feature_list)}",
            f"  Uptime (μs):      {basic_info.device_uptime_us}",
            f"  Timestamp (ns):   {timestamp_ns}"
        ])
    
    return "\n".join(info_lines)

def export_device_info_json(basic_info, timestamp_ns, filepath):
    """Export device information to JSON file."""
    if basic_info is None:
        return False
    
    try:
        # Prepare data for JSON export
        data = {
            "device_info": {
                "device_name": basic_info.device_name.decode('utf-8').rstrip('\0'),
                "serial_number": ''.join(f'{b:02X}' for b in bytes(basic_info.device_sn)).rstrip('00'),
                "firmware_version": basic_info.firmware_version_string.decode('utf-8').rstrip('\0'),
                "firmware_build_date": basic_info.firmware_build_date.decode('utf-8').rstrip('\0'),
                "firmware_build_time": basic_info.firmware_build_time.decode('utf-8').rstrip('\0'),
                "model": {
                    "major": basic_info.model_major,
                    "sub": basic_info.model_sub,
                    "revision": basic_info.model_revision,
                    "string": ("A1M1" if basic_info.model_major == 0 and basic_info.model_sub == 0 
                              else f"A{basic_info.model_major}M{basic_info.model_sub}") + 
                             (f"-r{basic_info.model_revision}" if basic_info.model_revision else "")
                },
                "hardware_version": f"{basic_info.model_major}.{basic_info.model_sub}.{basic_info.model_revision}",
                "features": {
                    "hardware_bitmask": f"0x{basic_info.hwfeature_bitmaps:016X}",
                    "sensing_bitmask": f"0x{basic_info.sensing_feature_bitmaps:016X}",
                    "software_bitmask": f"0x{basic_info.swfeature_bitmaps:016X}",
                    "feature_list": format_feature_bitmaps(
                        basic_info.hwfeature_bitmaps,
                        basic_info.sensing_feature_bitmaps,
                        basic_info.swfeature_bitmaps
                    )
                },
                "uptime": {
                    "microseconds": basic_info.device_uptime_us,
                    "formatted": format_uptime(basic_info.device_uptime_us)
                },
                "timestamp": {
                    "nanoseconds": timestamp_ns,
                    "iso_string": datetime.fromtimestamp(timestamp_ns / 1_000_000_000).isoformat()
                }
            },
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "sdk_version": "2.0.0"
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False

def display_help():
    """Display help information."""
    help_text = """
Device Information Monitor Controls:
====================================
CTRL+C    - Quit application
Q         - Quit application
D         - Toggle detailed information
S         - Save current info to JSON file
H         - Show this help
R         - Reset/clear display

Information Displayed:
- Device name and model
- Serial number
- Firmware and hardware versions
- Device uptime
- Feature bitmasks (detailed mode)
- Real-time timestamps

The display updates continuously. Press keys for commands.
"""
    print(help_text)

def main():
    """Main function."""
    global is_ctrl_c
    
    parser = argparse.ArgumentParser(description='Aurora Device Information Monitor Demo')
    parser.add_argument('--device', '-d', type=str, 
                       help='Device IP address (default: auto-discover)', default=None)
    parser.add_argument('--interval', '-i', type=float, 
                       help='Update interval in seconds (default: 2.0)', default=2.0)
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed information by default')
    parser.add_argument('--export', '-e', type=str,
                       help='Export device info to JSON file on startup')
    parser.add_argument('--once', action='store_true',
                       help='Show information once and exit')
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize SDK
    print("Initializing Aurora SDK...")
    sdk = AuroraSDK()
    
    try:
        
        # Connect to device
        if args.device:
            # Connect to specific device IP
            print(f"Connecting to device at {args.device}...")
            sdk.connect(connection_string=args.device)
            print("Connected successfully!")
        else:
            # Discover and connect to first available device
            device_info = discover_and_select_device(sdk)
            if not device_info:
                return 1
            
            if not connect_to_device(sdk, device_info):
                return 1
        
        # Display help if not running once
        if not args.once:
            display_help()
        
        # Start keyboard input thread for interactive commands (only in continuous mode and if terminal)
        input_thread = None
        is_interactive = not args.once and sys.stdin.isatty()
        if is_interactive:
            input_thread = threading.Thread(target=keyboard_input_thread, daemon=True)
            input_thread.start()
        
        # Main monitoring loop
        show_detailed = args.detailed
        update_count = 0
        
        print(f"\nStarting device information monitoring (interval: {args.interval}s)...")
        if is_interactive:
            print("Press 'H' for help, 'D' for detailed toggle, 'S' to save, 'Q' or 'CTRL+C' to quit...\n")
        elif not args.once:
            print("Running in non-interactive mode. Use CTRL+C to quit...\n")
        
        while not is_ctrl_c:
            # Get device basic info
            basic_info, timestamp_ns = get_device_basic_info(sdk)
            
            if basic_info:
                # Clear screen for clean display (only in continuous mode)
                if not args.once and update_count > 0:
                    print("\033[2J\033[H", end="")  # Clear screen and move cursor to top
                
                # Format and display info
                info_text = format_device_info(basic_info, timestamp_ns, show_detailed)
                print("=" * 60)
                print(f"Aurora Device Information Monitor (Update #{update_count + 1})")
                print("=" * 60)
                print(info_text)
                print("=" * 60)
                
                # Export to JSON if requested on startup
                if args.export and update_count == 0:
                    if export_device_info_json(basic_info, timestamp_ns, args.export):
                        print(f"Device information exported to: {args.export}")
                    else:
                        print(f"Failed to export device information to: {args.export}")
                
                update_count += 1
                
                # Exit if running once
                if args.once:
                    break
            else:
                print("Failed to retrieve device information")
                if args.once:
                    return 1
            
            # Process keyboard input and sleep with interruption check
            if not args.once:
                try:
                    # Process any pending keyboard input (only in interactive mode)
                    if is_interactive:
                        show_detailed, commands = process_user_input(show_detailed, basic_info, timestamp_ns, update_count)
                    
                    # Sleep with interruption check
                    sleep_time = 0.1
                    for _ in range(int(args.interval / sleep_time)):
                        if is_ctrl_c:
                            break
                        time.sleep(sleep_time)
                        
                        # Check for more input during sleep (only in interactive mode)
                        if is_interactive and not input_queue.empty():
                            show_detailed, _ = process_user_input(show_detailed, basic_info, timestamp_ns, update_count)
                        
                except KeyboardInterrupt:
                    break
        
        print(f"\nMonitoring completed. Total updates: {update_count}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Cleanup
        try:
            sdk.disconnect()
            sdk.release()
            print("Disconnected from device")
        except:
            pass
    
    print("Device information monitor demo completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())