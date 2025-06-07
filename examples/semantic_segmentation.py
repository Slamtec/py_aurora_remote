#!/usr/bin/env python3
"""
SLAMTEC Aurora Python SDK Demo - Semantic Segmentation

This demo shows how to capture and visualize semantic segmentation data using Enhanced Imaging API.
Features (matching C++ implementation exactly):
- Real-time segmentation map display with colorization
- Camera image overlay functionality (60% camera + 40% segmentation) with timestamp correlation
- Mouse hover object contour detection and label display
- Depth camera aligned segmentation map display
- Working colors with manual fallback for broken C API

Requirements:
- numpy
- opencv-python
- Aurora device with semantic segmentation support and SDK 2.0
"""

import sys
import os
import time
import signal
import argparse

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, AuroraSDKError, to_numpy_segmentation_map, to_colorized_segmentation_map, generate_class_colors, get_colorized_segmentation, manual_colorize_segmentation, get_class_at_position)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION
        from slamtec_aurora_sdk.exceptions import AuroraSDKError
        from slamtec_aurora_sdk.utils import (to_numpy_segmentation_map, to_colorized_segmentation_map, 
                                              generate_class_colors, get_colorized_segmentation, 
                                              manual_colorize_segmentation, get_class_at_position)
        return AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, AuroraSDKError, to_numpy_segmentation_map, to_colorized_segmentation_map, generate_class_colors, get_colorized_segmentation, manual_colorize_segmentation, get_class_at_position
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION
        from slamtec_aurora_sdk.exceptions import AuroraSDKError
        from slamtec_aurora_sdk.utils import (to_numpy_segmentation_map, to_colorized_segmentation_map, 
                                              generate_class_colors, get_colorized_segmentation, 
                                              manual_colorize_segmentation, get_class_at_position)
        return AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, AuroraSDKError, to_numpy_segmentation_map, to_colorized_segmentation_map, generate_class_colors, get_colorized_segmentation, manual_colorize_segmentation, get_class_at_position

# Setup SDK import
AuroraSDK, ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, AuroraSDKError, to_numpy_segmentation_map, to_colorized_segmentation_map, generate_class_colors, get_colorized_segmentation, manual_colorize_segmentation, get_class_at_position = setup_sdk_import()

try:
    import cv2
    import numpy as np
except ImportError as e:
    print("Error: Required dependencies not found.")
    print("Please install: pip install opencv-python numpy")
    sys.exit(1)

# Global variables for mouse interaction (like C++)
is_ctrl_c = False
current_seg_frame = None
current_camera_image = None
current_colorized_seg_map = None
current_seg_map = None
current_overlay_base = None
current_label_info = None
has_valid_frames = False
last_mouse_pos = (-1, -1)

# Model switching state (like C++)
is_model_switching = False
model_switch_status = ""
is_using_alternative_model = False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    global is_ctrl_c
    print("\nCtrl-C pressed, exiting...")
    is_ctrl_c = True

def print_label_info(label_set_name, label_info):
    """Print label information exactly like C++ printLabelInfo function."""
    print("\n=== Semantic Segmentation Label Information ===")
    print(f"Label Set: {label_set_name}")
    print(f"Total Classes: {label_info.label_count}")
    print("Classes:")
    
    for i in range(label_info.label_count):
        try:
            label_obj = label_info.label_names[i]
            if hasattr(label_obj, 'name'):
                label_name = label_obj.name.decode('utf-8') if isinstance(label_obj.name, bytes) else str(label_obj.name)
            else:
                label_name = str(label_obj)
            
            if label_name == "(null)" or not label_name:
                label_name = "Background"
            
            print(f"  [{i:2d}] {label_name}")
        except Exception:
            print(f"  [{i:2d}] <error accessing label>")
    
    print("================================================\n")

# Note: manual_colorize_segmentation and get_colorized_segmentation are now in utils.py

def create_camera_overlay(camera_image, colorized_seg_map):
    """Create camera overlay exactly like C++ createCameraOverlay function."""
    if camera_image is None or colorized_seg_map is None:
        return colorized_seg_map.copy() if colorized_seg_map is not None else None
    
    # Resize camera image to match segmentation size
    camera_resized = cv2.resize(camera_image, (colorized_seg_map.shape[1], colorized_seg_map.shape[0]))
    
    # Start with camera image as base (like C++)
    overlay = camera_resized.copy()
    
    # Create mask for non-black pixels in segmentation (like C++)
    mask = cv2.inRange(colorized_seg_map, (1, 1, 1), (255, 255, 255))
    
    # Blend camera and segmentation (60% camera, 40% segmentation like C++)
    blended_seg = cv2.addWeighted(camera_resized, 0.6, colorized_seg_map, 0.4, 0)
    
    # Apply blended segmentation only where mask is non-zero (like C++)
    overlay[mask > 0] = blended_seg[mask > 0]
    
    return overlay

def get_camera_preview_for_overlay(sdk, timestamp_ns):
    """Get camera preview image for overlay with timestamp correlation (matching C++ demo exactly)."""
    try:
        # Use the updated get_camera_preview method with timestamp support
        left_img, right_img = sdk.data_provider.get_camera_preview(timestamp_ns, allow_nearest_frame=False)
        
        if left_img and left_img.has_image_data():
            camera_image = left_img.to_opencv_image()
            # Convert grayscale to BGR if needed (like C++ demo)
            if camera_image is not None:
                if len(camera_image.shape) == 2:
                    camera_image = cv2.cvtColor(camera_image, cv2.COLOR_GRAY2BGR)
                elif len(camera_image.shape) == 3 and camera_image.shape[2] == 1:
                    camera_image = cv2.cvtColor(camera_image, cv2.COLOR_GRAY2BGR)
            return camera_image
    except Exception as e:
        # Silent fallback - this is expected behavior when camera data isn't available
        pass
    
    return None

def find_contours_at_position(seg_map, mouse_pos, output, label_info):
    """Find and draw contours for a specific class at mouse position (matching C++)."""
    if mouse_pos[0] < 0 or mouse_pos[1] < 0 or mouse_pos[0] >= seg_map.shape[1] or mouse_pos[1] >= seg_map.shape[0]:
        return False, "Out of bounds"
    
    class_id = seg_map[mouse_pos[1], mouse_pos[0]]
    
    # Get class label from label_info
    if class_id < label_info.label_count:
        try:
            label_obj = label_info.label_names[class_id]
            if hasattr(label_obj, 'name'):
                label_name = label_obj.name.decode('utf-8') if isinstance(label_obj.name, bytes) else str(label_obj.name)
            else:
                label_name = str(label_obj)
            
            if label_name == "(null)" or not label_name:
                label_name = "Background"
                return False, label_name  # Don't draw contours for background
        except Exception:
            label_name = "Background"
            return False, label_name
    else:
        label_name = "Unknown"
    
    # Create mask for the specific class
    mask = (seg_map == class_id).astype(np.uint8) * 255
    
    # Find contours with full chain representation (like C++)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # Draw contours
    cv2.drawContours(output, contours, -1, (255, 255, 255), 2)
    
    return True, f"Class {class_id}: {label_name}"

def mouse_callback(event, x, y, flags, param):
    """Mouse callback for object inspection and contour display (matching C++)."""
    global last_mouse_pos, current_seg_frame, current_seg_map, current_overlay_base, current_label_info, has_valid_frames
    global is_model_switching, model_switch_status
    
    if event == cv2.EVENT_MOUSEMOVE and has_valid_frames:
        last_mouse_pos = (x, y)
        
        if current_seg_frame is None or current_seg_map is None or current_overlay_base is None or current_label_info is None:
            return
        
        # Immediate update for responsive feedback (like C++)
        display_map = current_overlay_base.copy()
        
        has_contours, label_text = find_contours_at_position(current_seg_map, last_mouse_pos, display_map, current_label_info)
        
        # Display hovered label (like C++)
        if label_text:
            if has_contours:
                color = (0, 255, 255)  # Cyan for objects with contours
            else:
                color = (128, 128, 128)  # Gray for background
            cv2.putText(display_map, label_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        # Display model switching status if active (like C++)
        if is_model_switching and model_switch_status:
            cv2.putText(display_map, model_switch_status, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        cv2.imshow('Segmentation & Camera Overlay', display_map)

def get_depth_aligned_segmentation_map(sdk, seg_frame, colors):
    """Get depth camera aligned segmentation map (matching C++ exactly but with safety)."""
    try:
        if seg_frame and sdk.enhanced_imaging.is_depth_camera_supported():
            try:
                # Use calcDepthCameraAlignedSegmentationMap like C++ demo (now with ImageFrame)
                result = sdk.enhanced_imaging.calc_depth_camera_aligned_segmentation_map(seg_frame)
                if result:
                    aligned_data, aligned_width, aligned_height = result
                    if aligned_data and aligned_width > 0 and aligned_height > 0:
                        # Convert aligned data to numpy array
                        aligned_seg_map = np.frombuffer(aligned_data, dtype=np.uint8).reshape((aligned_height, aligned_width))
                        
                        # Colorize the aligned segmentation map (like C++ demo) using utils function
                        aligned_colorized = manual_colorize_segmentation(aligned_seg_map, colors)
                        return aligned_colorized
            except Exception as align_error:
                print(f"Aligned segmentation C API failed: {align_error}")
                return None
    except Exception as e:
        print(f"Error getting aligned segmentation: {e}")
    
    return None

# Note: generate_class_colors is now in utils.py

def main():
    """Main function."""
    global is_ctrl_c, current_seg_frame, current_camera_image, current_colorized_seg_map
    global current_seg_map, current_overlay_base, current_label_info, has_valid_frames
    global is_using_alternative_model, is_model_switching, model_switch_status
    
    parser = argparse.ArgumentParser(description='Aurora Semantic Segmentation Demo')
    parser.add_argument('--device', '-d', type=str, help='Device IP address', default='192.168.1.212')
    parser.add_argument('--headless', action='store_true', help='Run without GUI')
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=== Aurora Semantic Segmentation Demo ===")
    print("Features:")
    print("1. Camera overlay: Camera background + segmentation overlay (60%/40%) with timestamp correlation")
    print("2. Mouse hover: Object contour detection and label display")
    print("3. Aligned window: Depth camera aligned segmentation")
    print("4. Working colors with manual fallback")
    
    sdk = AuroraSDK()
    try:
        print("1. Connecting...")
        sdk.connect(connection_string=args.device)
        
        print("2. Subscribing...")
        sdk.controller.set_enhanced_imaging_subscription(ENHANCED_IMAGE_TYPE_SEMANTIC_SEGMENTATION, True)
        
        print("3. Getting configuration...")
        config = sdk.enhanced_imaging.get_semantic_segmentation_config()
        label_info = sdk.enhanced_imaging.get_semantic_segmentation_labels()
        current_label_info = label_info  # Store globally for mouse callback
        
        # Get label set name as model identifier (like C++ demo)
        try:
            label_set_name = sdk.enhanced_imaging.get_semantic_segmentation_label_set_name()
        except:
            label_set_name = "Unknown"
        
        # Use actual label count, not config class count (like C++ demo)
        actual_class_count = label_info.label_count
        print(f"   Model: {label_set_name}, Classes: {actual_class_count}")
        colors = generate_class_colors(actual_class_count)
        print(f"   Generated {len(colors)} colors")
        
        # Print label information (like C++ demo)
        print_label_info(label_set_name, label_info)
        
        # Check current model (like C++)
        try:
            is_using_alternative_model = sdk.enhanced_imaging.is_semantic_segmentation_alternative_model()
        except:
            is_using_alternative_model = False
        print(f"Current model: {'Alternative' if is_using_alternative_model else 'Default'}")
        
        # Check depth camera support (like C++)
        is_depth_supported = sdk.enhanced_imaging.is_depth_camera_supported()
        print(f"   Depth camera supported: {is_depth_supported}")
        
        if not args.headless:
            print("4. Creating windows...")
            # Main window for camera overlay + segmentation (like C++)
            cv2.namedWindow('Segmentation & Camera Overlay', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Segmentation & Camera Overlay', 800, 600)
            
            # Set mouse callback for hover functionality (like C++)
            cv2.setMouseCallback('Segmentation & Camera Overlay', mouse_callback, None)
            
            # Aligned window only if depth camera is supported (like C++)
            if is_depth_supported:
                cv2.namedWindow('Depth Aligned Segmentation', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Depth Aligned Segmentation', 400, 300)
                print("   ✅ Both windows created with mouse hover support")
            else:
                print("   ✅ Main window created with mouse hover support (no depth camera for alignment)")
        
        # Print controls (like C++)
        if not args.headless:
            print("\nControls:")
            print("  ESC - Exit")
            print("  'm' - Switch between default and alternative model")
            print("  Mouse hover - Show object contours and labels (in merged segmentation & camera overlay)")
        
        print("5. Main loop...")
        frame_count = 0
        success_count = 0
        aligned_success_count = 0
        
        while not is_ctrl_c and frame_count < 10000:
            try:
                # Wait for frame
                if not sdk.enhanced_imaging.wait_semantic_segmentation_next_frame(1000):
                    continue
                
                # Get segmentation frame
                current_seg_frame = sdk.enhanced_imaging.peek_semantic_segmentation_frame()
                if not current_seg_frame:
                    continue
                
                frame_count += 1
                
                # Get camera preview for overlay with timestamp correlation (like C++)
                current_camera_image = get_camera_preview_for_overlay(sdk, current_seg_frame.timestamp_ns)
                
                # Get segmentation map for mouse inspection (using utils function)
                current_seg_map = to_numpy_segmentation_map(current_seg_frame)
                
                # Get colorized segmentation
                current_colorized_seg_map = get_colorized_segmentation(current_seg_frame, colors)
                
                if current_colorized_seg_map is not None:
                    success_count += 1
                    has_valid_frames = True
                    
                    # Create camera overlay (like C++)
                    if current_camera_image is not None:
                        current_overlay_base = create_camera_overlay(current_camera_image, current_colorized_seg_map)
                    else:
                        current_overlay_base = current_colorized_seg_map.copy()
                    
                    if not args.headless and current_overlay_base is not None:
                        try:
                            # Add frame info (like C++)
                            display_map = current_overlay_base.copy()
                            frame_info = f"Frame: {frame_count} | Model: {'Alt' if is_using_alternative_model else 'Default'}"
                            cv2.putText(display_map, frame_info, (10, display_map.shape[0] - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                            
                            # Add control instructions (like C++)
                            control_text = "'m' - Switch between default and alternative model"
                            cv2.putText(display_map, control_text, (10, display_map.shape[0] - 30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                            
                            # Handle current mouse position if valid (like C++)
                            if last_mouse_pos != (-1, -1) and current_seg_map is not None and current_label_info is not None:
                                has_contours, label_text = find_contours_at_position(current_seg_map, last_mouse_pos, display_map, current_label_info)
                                if label_text:
                                    if has_contours:
                                        color = (0, 255, 255)  # Cyan for objects with contours
                                    else:
                                        color = (128, 128, 128)  # Gray for background
                                    cv2.putText(display_map, label_text, (10, 30), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
                            
                            # Display model switching status if active (like C++)
                            if is_model_switching and model_switch_status:
                                cv2.putText(display_map, model_switch_status, (10, 70), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                            
                            # Show main window (like C++)
                            cv2.imshow('Segmentation & Camera Overlay', display_map)
                            
                            # Depth aligned segmentation (like C++)
                            if is_depth_supported:
                                aligned_colorized = get_depth_aligned_segmentation_map(sdk, current_seg_frame, colors)
                                if aligned_colorized is not None:
                                    aligned_success_count += 1
                                    cv2.imshow('Depth Aligned Segmentation', aligned_colorized)
                                    if frame_count % 30 == 1:
                                        print(f"   ✅ Aligned segmentation working: {aligned_colorized.shape}")
                                else:
                                    if frame_count % 30 == 1:
                                        print(f"   ⚠️ Aligned segmentation unavailable")
                            
                            # Handle keyboard
                            key = cv2.waitKey(1) & 0xFF
                            if key == 27:  # ESC
                                break
                            elif key == ord('m') or key == ord('M'):  # Model switching
                                try:
                                    new_model = not is_using_alternative_model
                                    print(f"Switching to {'Alternative' if new_model else 'Default'} model...")
                                    
                                    # Set model switching status for display
                                    is_model_switching = True
                                    model_switch_status = f"Switching to {'Alternative' if new_model else 'Default'} model..."
                                    
                                    try:
                                        sdk.controller.require_semantic_segmentation_alternative_model(new_model)
                                        
                                        # Wait for model switch to complete (like C++ demo)
                                        import time
                                        timeout_count = 0
                                        max_timeout = 50  # 5 seconds max
                                        
                                        while sdk.enhanced_imaging.is_semantic_segmentation_alternative_model() != new_model and timeout_count < max_timeout:
                                            time.sleep(0.1)
                                            timeout_count += 1
                                            
                                            # Update display during waiting (like C++)
                                            if has_valid_frames:
                                                display_map = current_overlay_base.copy()
                                                cv2.putText(display_map, model_switch_status, (10, 70), 
                                                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                                                cv2.imshow('Segmentation & Camera Overlay', display_map)
                                                cv2.waitKey(1)  # Allow OpenCV to update display
                                        
                                        if timeout_count >= max_timeout:
                                            raise Exception("Model switch timeout")
                                        
                                        is_using_alternative_model = new_model
                                        
                                        # Update status message
                                        model_switch_status = f"Model switched to {'Alternative' if new_model else 'Default'} - Updating labels..."
                                        
                                        # Update label information after model switch
                                        try:
                                            label_set_name = sdk.enhanced_imaging.get_semantic_segmentation_label_set_name()
                                            label_info = sdk.enhanced_imaging.get_semantic_segmentation_labels()
                                            current_label_info = label_info  # Update global for mouse callback
                                            print_label_info(label_set_name, label_info)
                                            colors = generate_class_colors(label_info.label_count)
                                        except Exception as e:
                                            print(f"Failed to update labels: {e}")
                                        
                                        # Show success message briefly
                                        model_switch_status = "Model switch completed successfully!"
                                        if has_valid_frames:
                                            display_map = current_overlay_base.copy()
                                            cv2.putText(display_map, model_switch_status, (10, 70), 
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                            cv2.imshow('Segmentation & Camera Overlay', display_map)
                                            cv2.waitKey(1000)  # Show success message for 1 second
                                        
                                        print("Model switched successfully")
                                    except Exception as switch_e:
                                        model_switch_status = "Failed to switch model!"
                                        if has_valid_frames:
                                            display_map = current_overlay_base.copy()
                                            cv2.putText(display_map, model_switch_status, (10, 70), 
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                                            cv2.imshow('Segmentation & Camera Overlay', display_map)
                                            cv2.waitKey(1000)  # Show error message for 1 second
                                        print(f"Failed to switch model: {switch_e}")
                                    
                                    # Clear model switching status
                                    is_model_switching = False
                                    model_switch_status = ""
                                except Exception as e:
                                    print(f"Model switching error: {e}")
                                    is_model_switching = False
                                    model_switch_status = ""
                        except Exception as display_e:
                            print(f"Display error: {display_e}")
                    
                    # Progress
                    if frame_count % 30 == 0:
                        success_rate = success_count / frame_count * 100
                        non_black = np.sum(~np.all(current_colorized_seg_map == [0, 0, 0], axis=2))
                        total = current_colorized_seg_map.shape[0] * current_colorized_seg_map.shape[1]
                        color_rate = non_black / total * 100
                        
                        camera_status = "with camera" if current_camera_image is not None else "segmentation only"
                        
                        if is_depth_supported:
                            aligned_rate = aligned_success_count / frame_count * 100 if frame_count > 0 else 0
                            print(f"   Frame {frame_count}: {success_rate:.1f}% success, {color_rate:.1f}% colored, {aligned_rate:.1f}% aligned, {camera_status}")
                        else:
                            print(f"   Frame {frame_count}: {success_rate:.1f}% success, {color_rate:.1f}% colored, {camera_status}")
                
            except Exception as loop_e:
                print(f"Frame error: {loop_e}")
                time.sleep(0.1)
        
        print(f"\n=== Results ===")
        print(f"Total frames: {frame_count}")
        print(f"Successful frames: {success_count}")
        if is_depth_supported:
            print(f"Aligned frames: {aligned_success_count}")
        print("✅ Demo completed successfully")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        try:
            if not args.headless:
                cv2.destroyAllWindows()
            sdk.disconnect()
            sdk.release()
            print("✅ Disconnected safely")
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())