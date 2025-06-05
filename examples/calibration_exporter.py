#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - Calibration Data Exporter

This demo shows how to retrieve and export camera and transform calibration parameters.
Features:
- Retrieve camera lens calibration parameters from device
- Retrieve transform calibration parameters from device  
- Export calibration data in multiple formats (OpenCV, YAML, JSON)
- Command line interface with usage information
- Detailed calibration parameter display

Requirements:
- Aurora device with SDK 2.0 support
- opencv-python (for OpenCV format export)
- PyYAML (for YAML format export, optional)
"""

import sys
import argparse
import os

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

def format_matrix_3x3(matrix_array, name):
    """Format 3x3 matrix for display."""
    lines = [f"{name}:"]
    for i in range(3):
        row = [f"{matrix_array[i*3 + j]:12.6f}" for j in range(3)]
        lines.append(f"  [{', '.join(row)}]")
    return lines

def format_matrix_3x4(matrix_array, name):
    """Format 3x4 matrix for display."""
    lines = [f"{name}:"]
    for i in range(3):
        row = [f"{matrix_array[i*4 + j]:12.6f}" for j in range(4)]
        lines.append(f"  [{', '.join(row)}]")
    return lines

def format_matrix_4x4(matrix_array, name):
    """Format 4x4 matrix for display."""
    lines = [f"{name}:"]
    for i in range(4):
        row = [f"{matrix_array[i*4 + j]:12.6f}" for j in range(4)]
        lines.append(f"  [{', '.join(row)}]")
    return lines

def format_vector(vector_array, name, size):
    """Format vector for display."""
    vector_str = ', '.join([f"{vector_array[i]:12.6f}" for i in range(size)])
    return [f"{name}: [{vector_str}]"]

def format_roi(roi_array, name):
    """Format ROI (Region of Interest) for display."""
    roi_str = f"x={roi_array[0]}, y={roi_array[1]}, width={roi_array[2]}, height={roi_array[3]}"
    return [f"{name}: [{roi_str}]"]

def display_camera_calibration(camera_cal):
    """Display camera calibration information."""
    print("\n" + "="*80)
    print("CAMERA CALIBRATION PARAMETERS")
    print("="*80)
    
    # Display camera type
    camera_type_str = "MONO" if camera_cal.camera_type == 0 else "STEREO" if camera_cal.camera_type == 1 else "UNKNOWN"
    print(f"Camera Type: {camera_type_str}")
    print()
    
    # Display camera 0 (left camera for stereo, main camera for mono)
    cam0 = camera_cal.camera_calibration[0]
    print("CAMERA 0:")
    lens_type_str = "PINHOLE" if cam0.len_type == 0 else "RECTIFIED" if cam0.len_type == 1 else "KANNALABRANDT" if cam0.len_type == 2 else "UNKNOWN"
    color_mode_str = "RGB" if cam0.color_mode == 0 else "MONO" if cam0.color_mode == 1 else "UNKNOWN"
    print(f"  Lens Type: {lens_type_str}")
    print(f"  Color Mode: {color_mode_str}")
    print(f"  Resolution: {cam0.width}x{cam0.height}")
    print(f"  Focal Length: fx={cam0.intrinsics[0]:.2f}, fy={cam0.intrinsics[1]:.2f}")
    print(f"  Principal Point: cx={cam0.intrinsics[2]:.2f}, cy={cam0.intrinsics[3]:.2f}")
    print(f"  Distortion: k1={cam0.distortion[0]:.6f}, k2={cam0.distortion[1]:.6f}, k3={cam0.distortion[2]:.6f}, k4={cam0.distortion[3]:.6f}")
    print(f"  FPS: {cam0.fps}")
    print()
    
    # Display camera 1 if stereo
    if camera_cal.camera_type == 1:  # STEREO
        cam1 = camera_cal.camera_calibration[1]
        print("CAMERA 1:")
        lens_type_str = "PINHOLE" if cam1.len_type == 0 else "RECTIFIED" if cam1.len_type == 1 else "KANNALABRANDT" if cam1.len_type == 2 else "UNKNOWN"
        color_mode_str = "RGB" if cam1.color_mode == 0 else "MONO" if cam1.color_mode == 1 else "UNKNOWN"
        print(f"  Lens Type: {lens_type_str}")
        print(f"  Color Mode: {color_mode_str}")
        print(f"  Resolution: {cam1.width}x{cam1.height}")
        print(f"  Focal Length: fx={cam1.intrinsics[0]:.2f}, fy={cam1.intrinsics[1]:.2f}")
        print(f"  Principal Point: cx={cam1.intrinsics[2]:.2f}, cy={cam1.intrinsics[3]:.2f}")
        print(f"  Distortion: k1={cam1.distortion[0]:.6f}, k2={cam1.distortion[1]:.6f}, k3={cam1.distortion[2]:.6f}, k4={cam1.distortion[3]:.6f}")
        print(f"  FPS: {cam1.fps}")
        print()
        
        # Display stereo parameters (from external transform)
        print("STEREO PARAMETERS:")
        ext_transform = camera_cal.ext_camera_transform[0]
        t_matrix = list(ext_transform.t_c2_c1)
        
        # Display 4x4 transformation matrix
        print("  Transformation Matrix (camera 2 to camera 1):")
        for i in range(4):
            row = [f"{t_matrix[i*4 + j]:12.6f}" for j in range(4)]
            print(f"    [{', '.join(row)}]")
        
        # Extract translation from 4x4 matrix
        tx, ty, tz = t_matrix[3], t_matrix[7], t_matrix[11]
        print(f"  Translation: [{tx:.6f}, {ty:.6f}, {tz:.6f}]")
        baseline = abs(tx)  # X-component is typically the baseline
        print(f"  Baseline: {baseline*1000:.1f} mm")

def display_transform_calibration(transform_cal):
    """Display transform calibration information."""
    print("\n" + "="*80)
    print("TRANSFORM CALIBRATION PARAMETERS")
    print("="*80)
    
    # Display base to camera transform
    print("BASE TO CAMERA TRANSFORM:")
    base_cam = transform_cal.t_base_cam
    print(f"  Translation: [{base_cam.translation.x:.6f}, {base_cam.translation.y:.6f}, {base_cam.translation.z:.6f}]")
    print(f"  Quaternion: [{base_cam.quaternion.x:.6f}, {base_cam.quaternion.y:.6f}, {base_cam.quaternion.z:.6f}, {base_cam.quaternion.w:.6f}]")
    print()
    
    # Display camera to IMU transform
    print("CAMERA TO IMU TRANSFORM:")
    cam_imu = transform_cal.t_camera_imu
    print(f"  Translation: [{cam_imu.translation.x:.6f}, {cam_imu.translation.y:.6f}, {cam_imu.translation.z:.6f}]")
    print(f"  Quaternion: [{cam_imu.quaternion.x:.6f}, {cam_imu.quaternion.y:.6f}, {cam_imu.quaternion.z:.6f}, {cam_imu.quaternion.w:.6f}]")

def export_calibration_data(camera_cal, transform_cal, output_path, format_type):
    """Export calibration data to file."""
    try:
        print(f"\nExporting calibration data to: {output_path}")
        print(f"Format: {format_type.upper()}")
        
        if format_type.lower() == 'opencv':
            export_calibration_opencv(camera_cal, transform_cal, output_path)
        elif format_type.lower() == 'yaml':
            export_calibration_yaml(camera_cal, transform_cal, output_path)
        elif format_type.lower() == 'json':
            export_calibration_json(camera_cal, transform_cal, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        print(f"Calibration data exported successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to export calibration data: {e}")
        
        # Provide help for missing dependencies
        if "OpenCV" in str(e):
            print("Install OpenCV: pip install opencv-python")
        elif "PyYAML" in str(e):
            print("Install PyYAML: pip install PyYAML")
        
        return False

def export_calibration_opencv(camera_cal, transform_cal, filepath):
    """Export calibration data in OpenCV format."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ImportError("OpenCV is required for OpenCV format export")
    
    # Create OpenCV FileStorage for writing
    fs = cv2.FileStorage(filepath, cv2.FILE_STORAGE_WRITE)
    
    # Write camera type
    fs.write('camera_type', int(camera_cal.camera_type))
    
    # Write camera 0 calibration
    cam0 = camera_cal.camera_calibration[0]
    cam0_matrix = np.array([[cam0.intrinsics[0], 0, cam0.intrinsics[2]],
                           [0, cam0.intrinsics[1], cam0.intrinsics[3]],
                           [0, 0, 1]], dtype=np.float64)
    cam0_dist = np.array(list(cam0.distortion), dtype=np.float64)
    
    fs.write('camera_0_matrix', cam0_matrix)
    fs.write('camera_0_distortion', cam0_dist)
    fs.write('camera_0_width', int(cam0.width))
    fs.write('camera_0_height', int(cam0.height))
    fs.write('camera_0_fps', float(cam0.fps))
    
    # Write camera 1 calibration if stereo
    if camera_cal.camera_type == 1:  # STEREO
        cam1 = camera_cal.camera_calibration[1]
        cam1_matrix = np.array([[cam1.intrinsics[0], 0, cam1.intrinsics[2]],
                               [0, cam1.intrinsics[1], cam1.intrinsics[3]],
                               [0, 0, 1]], dtype=np.float64)
        cam1_dist = np.array(list(cam1.distortion), dtype=np.float64)
        
        fs.write('camera_1_matrix', cam1_matrix)
        fs.write('camera_1_distortion', cam1_dist)
        fs.write('camera_1_width', int(cam1.width))
        fs.write('camera_1_height', int(cam1.height))
        fs.write('camera_1_fps', float(cam1.fps))
        
        # Write stereo transform
        ext_transform = camera_cal.ext_camera_transform[0]
        transform_4x4 = np.array(list(ext_transform.t_c2_c1)).reshape(4, 4)
        
        # Extract rotation and translation for stereo calibration
        R = transform_4x4[:3, :3]
        T = transform_4x4[:3, 3:4]
        
        fs.write('rotation_matrix', R)
        fs.write('translation_vector', T)
        fs.write('transform_4x4', transform_4x4)
    
    # Write transform calibration data
    base_cam = transform_cal.t_base_cam
    cam_imu = transform_cal.t_camera_imu
    
    base_cam_pose = np.array([base_cam.translation.x, base_cam.translation.y, base_cam.translation.z,
                             base_cam.quaternion.x, base_cam.quaternion.y, base_cam.quaternion.z, base_cam.quaternion.w])
    cam_imu_pose = np.array([cam_imu.translation.x, cam_imu.translation.y, cam_imu.translation.z,
                            cam_imu.quaternion.x, cam_imu.quaternion.y, cam_imu.quaternion.z, cam_imu.quaternion.w])
    
    fs.write('base_to_camera_pose', base_cam_pose)
    fs.write('camera_to_imu_pose', cam_imu_pose)
    
    fs.release()

def export_calibration_yaml(camera_cal, transform_cal, filepath):
    """Export calibration data in YAML format."""
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for YAML format export")
    
    # Camera calibration data
    cam0 = camera_cal.camera_calibration[0]
    camera_data = {
        'camera_type': int(camera_cal.camera_type),
        'camera_0': {
            'width': int(cam0.width),
            'height': int(cam0.height),
            'intrinsics': list(cam0.intrinsics),
            'distortion': list(cam0.distortion),
            'fps': float(cam0.fps)
        }
    }
    
    # Add camera 1 if stereo
    if camera_cal.camera_type == 1:
        cam1 = camera_cal.camera_calibration[1]
        camera_data['camera_1'] = {
            'width': int(cam1.width),
            'height': int(cam1.height),
            'intrinsics': list(cam1.intrinsics),
            'distortion': list(cam1.distortion),
            'fps': float(cam1.fps)
        }
        
        # Add stereo transform
        ext_transform = camera_cal.ext_camera_transform[0]
        camera_data['stereo_transform'] = list(ext_transform.t_c2_c1)
    
    # Transform calibration data
    base_cam = transform_cal.t_base_cam
    cam_imu = transform_cal.t_camera_imu
    
    transform_data = {
        'base_to_camera': {
            'translation': [base_cam.translation.x, base_cam.translation.y, base_cam.translation.z],
            'quaternion': [base_cam.quaternion.x, base_cam.quaternion.y, base_cam.quaternion.z, base_cam.quaternion.w]
        },
        'camera_to_imu': {
            'translation': [cam_imu.translation.x, cam_imu.translation.y, cam_imu.translation.z],
            'quaternion': [cam_imu.quaternion.x, cam_imu.quaternion.y, cam_imu.quaternion.z, cam_imu.quaternion.w]
        }
    }
    
    data = {
        'camera_calibration': camera_data,
        'transform_calibration': transform_data
    }
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def export_calibration_json(camera_cal, transform_cal, filepath):
    """Export calibration data in JSON format."""
    import json
    
    # Camera calibration data
    cam0 = camera_cal.camera_calibration[0]
    camera_data = {
        'camera_type': int(camera_cal.camera_type),
        'camera_0': {
            'width': int(cam0.width),
            'height': int(cam0.height),
            'intrinsics': list(cam0.intrinsics),
            'distortion': list(cam0.distortion),
            'fps': float(cam0.fps)
        }
    }
    
    # Add camera 1 if stereo
    if camera_cal.camera_type == 1:
        cam1 = camera_cal.camera_calibration[1]
        camera_data['camera_1'] = {
            'width': int(cam1.width),
            'height': int(cam1.height),
            'intrinsics': list(cam1.intrinsics),
            'distortion': list(cam1.distortion),
            'fps': float(cam1.fps)
        }
        
        # Add stereo transform
        ext_transform = camera_cal.ext_camera_transform[0]
        camera_data['stereo_transform'] = list(ext_transform.t_c2_c1)
    
    # Transform calibration data
    base_cam = transform_cal.t_base_cam
    cam_imu = transform_cal.t_camera_imu
    
    transform_data = {
        'base_to_camera': {
            'translation': [base_cam.translation.x, base_cam.translation.y, base_cam.translation.z],
            'quaternion': [base_cam.quaternion.x, base_cam.quaternion.y, base_cam.quaternion.z, base_cam.quaternion.w]
        },
        'camera_to_imu': {
            'translation': [cam_imu.translation.x, cam_imu.translation.y, cam_imu.translation.z],
            'quaternion': [cam_imu.quaternion.x, cam_imu.quaternion.y, cam_imu.quaternion.z, cam_imu.quaternion.w]
        }
    }
    
    data = {
        'camera_calibration': camera_data,
        'transform_calibration': transform_data
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def print_usage_help():
    """Print detailed usage information."""
    usage_text = """
Aurora Calibration Exporter Usage:
==================================

This application retrieves camera and transform calibration parameters from 
Aurora devices and exports them to various file formats.

Basic Usage:
  python calibration_exporter.py [options]

Options:
  --device, -d IP        Connect to specific device IP address
  --output, -o FILE      Output file path (default: calibration.xml)
  --format, -f FORMAT    Export format: opencv, yaml, json (default: opencv)
  --display-only         Only display calibration data, don't export
  --help, -h             Show this help message

Export Formats:
  opencv  - OpenCV XML format (requires opencv-python)
  yaml    - YAML format (requires PyYAML)
  json    - JSON format (built-in, no extra dependencies)

Examples:
  # Display calibration data only
  python calibration_exporter.py --display-only
  
  # Export to OpenCV format
  python calibration_exporter.py -o camera_calibration.xml -f opencv
  
  # Export to YAML format
  python calibration_exporter.py -o calibration.yaml -f yaml
  
  # Export to JSON format
  python calibration_exporter.py -o calibration.json -f json
  
  # Connect to specific device and export
  python calibration_exporter.py -d 192.168.1.212 -o cal.xml

Dependencies:
  Required: slamtec_aurora_sdk
  Optional: opencv-python (for OpenCV format)
  Optional: PyYAML (for YAML format)

Note: The device must support SDK 2.0 Enhanced Imaging features.
"""
    print(usage_text)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Aurora Camera and Transform Calibration Exporter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Export formats:
  opencv  - OpenCV XML format (requires opencv-python)
  yaml    - YAML format (requires PyYAML) 
  json    - JSON format (no extra dependencies)

Examples:
  %(prog)s --display-only
  %(prog)s -o calibration.xml -f opencv
  %(prog)s -d 192.168.1.212 -o cal.yaml -f yaml
        """
    )
    
    parser.add_argument('--device', '-d', type=str,
                       help='Device IP address (default: auto-discover)', default=None)
    parser.add_argument('--output', '-o', type=str,
                       help='Output file path (default: calibration.xml)', default='calibration.xml')
    parser.add_argument('--format', '-f', type=str, 
                       choices=['opencv', 'yaml', 'json'],
                       help='Export format (default: opencv)', default='opencv')
    parser.add_argument('--display-only', action='store_true',
                       help='Only display calibration data, do not export to file')
    parser.add_argument('--usage', action='store_true',
                       help='Show detailed usage information')
    
    args = parser.parse_args()
    
    # Show usage if requested
    if args.usage:
        print_usage_help()
        return 0
    
    # Validate output file extension matches format
    if not args.display_only:
        file_ext = os.path.splitext(args.output)[1].lower()
        format_extensions = {
            'opencv': ['.xml', '.yml'],
            'yaml': ['.yaml', '.yml'],
            'json': ['.json']
        }
        
        if file_ext not in format_extensions.get(args.format, []):
            print(f"Warning: File extension '{file_ext}' may not match format '{args.format}'")
            suggested_ext = format_extensions[args.format][0]
            print(f"Suggested extension for {args.format} format: {suggested_ext}")
    
    # Initialize SDK
    print("Aurora Calibration Exporter")
    print("="*40)
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
        
        # Check device info
        try:
            device_info = sdk.get_device_info()
            print(f"Connected to: {device_info.device_name} (FW: {device_info.firmware_version})")
        except Exception as e:
            print(f"Warning: Could not get device info: {e}")
            print("Continuing with calibration retrieval...")
        
        # Check if Enhanced Imaging is supported
        if not hasattr(sdk, 'enhanced_imaging'):
            print("Error: Enhanced Imaging component not available in this SDK version.")
            return 1
        
        # Retrieve camera calibration
        print("\nRetrieving camera calibration parameters...")
        try:
            camera_cal = sdk.data_provider.get_camera_calibration()
            if camera_cal:
                print("Camera calibration retrieved successfully.")
            else:
                print("Camera calibration not available.")
        except Exception as e:
            print(f"Failed to retrieve camera calibration: {e}")
            camera_cal = None
        
        # Retrieve transform calibration
        print("Retrieving transform calibration parameters...")
        try:
            transform_cal = sdk.data_provider.get_transform_calibration()
            if transform_cal:
                print("Transform calibration retrieved successfully.")
            else:
                print("Transform calibration not available.")
        except Exception as e:
            print(f"Failed to retrieve transform calibration: {e}")
            transform_cal = None
        
        # Display calibration data
        if camera_cal:
            display_camera_calibration(camera_cal)
        else:
            print("\nCamera calibration data not available.")
        
        if transform_cal:
            display_transform_calibration(transform_cal)
        else:
            print("\nTransform calibration data not available.")
        
        # Export to file if requested
        if not args.display_only:
            if camera_cal or transform_cal:
                success = export_calibration_data(camera_cal, transform_cal, args.output, args.format)
                if success:
                    file_size = os.path.getsize(args.output) if os.path.exists(args.output) else 0
                    print(f"Output file size: {file_size} bytes")
                    return 0
                else:
                    return 1
            else:
                print("No calibration data available to export.")
                return 1
        else:
            print("\nCalibration data display completed.")
        
        print("\n" + "="*80)
        print("Calibration export completed successfully.")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
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
    
    return 0

if __name__ == "__main__":
    sys.exit(main())