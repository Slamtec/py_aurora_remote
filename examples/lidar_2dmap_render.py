#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiDAR 2D Map Render Example

This example demonstrates 2D occupancy grid map visualization using the Aurora SDK.
It shows real-time 2D grid map generation from LiDAR data with auto floor detection
and interactive controls.

Features:
- Real-time 2D occupancy grid map visualization
- Auto floor detection for multi-floor environments
- Interactive controls (redraw, zoom, pan)
- Background map generation with dirty rectangle updates
- Floor detection histogram visualization

Usage:
    python lidar_2dmap_render.py [connection_string]
    
Example:
    python lidar_2dmap_render.py 192.168.1.212
"""

import sys
import time
import argparse
import signal
import threading
import warnings
# typing module not available in Python 2.7

# Suppress numpy longdouble warning
warnings.filterwarnings("ignore", message=".*does not match any known type.*")

import os

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, GridMapGenerationOptions, Rect)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError
        from slamtec_aurora_sdk.data_types import GridMapGenerationOptions, Rect
        return AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, GridMapGenerationOptions, Rect
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError
        from slamtec_aurora_sdk.data_types import GridMapGenerationOptions, Rect
        return AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, GridMapGenerationOptions, Rect

try:
    import matplotlib
    # Set backend before importing pyplot - choose platform-appropriate backend
    import platform
    system = platform.system().lower()
    
    MATPLOTLIB_INTERACTIVE = False
    
    if 'DISPLAY' in os.environ or os.name == 'nt' or system == 'darwin':
        # Try interactive backends based on platform
        interactive_backends = []
        
        if system == 'darwin':  # macOS
            interactive_backends = [
                ('macosx', 'Native macOS backend'),
                ('Qt5Agg', 'pip install PyQt5'),
                ('QtAgg', 'pip install PyQt6 or PyQt5'),
                ('TkAgg', 'brew install python-tk')
            ]
        elif system == 'linux':
            interactive_backends = [
                ('Qt5Agg', 'pip install PyQt5'),
                ('QtAgg', 'pip install PyQt6 or PyQt5'),
                ('TkAgg', 'sudo apt-get install python3-tk')
            ]
        elif system == 'windows' or os.name == 'nt':
            interactive_backends = [
                ('Qt5Agg', 'pip install PyQt5'),
                ('QtAgg', 'pip install PyQt6 or PyQt5'),
                ('TkAgg', 'Usually included with Python')
            ]
        
        # Try each backend until one works
        backend_found = False
        for backend_name, install_hint in interactive_backends:
            try:
                matplotlib.use(backend_name, force=True)
                import matplotlib.pyplot as plt
                MATPLOTLIB_INTERACTIVE = True
                backend_found = True
                print(f"Using matplotlib backend: {backend_name}")
                break
            except (ImportError, ModuleNotFoundError):
                continue
        
        if not backend_found:
            # Fall back to non-interactive backend
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            MATPLOTLIB_INTERACTIVE = False
            print("Warning: No interactive GUI backend available, using non-interactive Agg backend")
    else:
        # No display environment, use non-interactive backend
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        MATPLOTLIB_INTERACTIVE = False
    
    MATPLOTLIB_AVAILABLE = True
    
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    MATPLOTLIB_INTERACTIVE = False
    NUMPY_AVAILABLE = False
    print("Warning: matplotlib/numpy not available: {}".format(e))
    print("Install with: pip install matplotlib numpy")

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, GridMapGenerationOptions, Rect = setup_sdk_import()


class LiDAR2DMapRenderer:
    """2D occupancy grid map visualization using matplotlib."""
    
    def __init__(self):
        self.sdk = None
        self.running = True
        
        # Map rendering state
        self.current_map_data = None
        self.map_dimension = None
        self.canvas = None
        
        # Matplotlib setup
        if MATPLOTLIB_AVAILABLE:
            self.fig, (self.ax_map, self.ax_hist) = plt.subplots(1, 2, figsize=(15, 6))
            self.ax_map.set_title('LiDAR 2D Occupancy Grid Map')
            self.ax_map.set_xlabel('X (meters)')
            self.ax_map.set_ylabel('Y (meters)')
            self.ax_map.set_aspect('equal')
            
            self.ax_hist.set_title('Floor Detection Histogram')
            self.ax_hist.set_xlabel('Height Bins')
            self.ax_hist.set_ylabel('Count')
            
            # Connect keyboard events
            self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
            
            plt.tight_layout()
    
    def _on_key_press(self, event):
        """Handle keyboard events."""
        if event.key == 'q' or event.key == 'escape':
            self.running = False
            plt.close('all')
        elif event.key == 'r':
            # Request redraw and immediately update
            if self.sdk and self.sdk.lidar_2d_map_builder:
                try:
                    print("Manual redraw requested...")
                    map_data = self.get_map_data(force_redraw=True)
                    if map_data:
                        self.update_visualization(map_data)
                        print("✓ Map redrawn")
                    else:
                        print("No map data available for redraw")
                except Exception as e:
                    print("Failed to redraw: {}".format(e))
        elif event.key == 'h':
            self._show_help()
    
    def _show_help(self):
        """Show help information."""
        help_text = """
=== LiDAR 2D Map Renderer - Controls ===

Keyboard Controls:
  • 'r': Request map redraw
  • 'q' or 'Esc': Exit application
  • 'h': Show this help

Map Information:
  • White areas: Free space
  • Black areas: Occupied space  
  • Gray areas: Unknown space
  • Auto floor detection enables multi-floor mapping
        """
        print(help_text)
    
    def connect_to_device(self, connection_string=None):
        """Connect to Aurora device."""
        try:
            # Create SDK instance
            self.sdk = AuroraSDK()
            
            # Get version info
            try:
                version_info = self.sdk.get_version_info()
                print("Aurora SDK Version: {}".format(version_info['version_string']))
            except Exception as e:
                print("Warning: Could not get SDK version: {}".format(e))
            
            # Session created automatically
            print("SDK session created automatically...")
            
            # Connect to device
            if connection_string:
                print("Connecting to device at: {}".format(connection_string))
                self.sdk.connect(connection_string=connection_string)
            else:
                # Discovery mode
                print("Discovering Aurora devices...")
                devices = self.sdk.discover_devices(timeout=10.0)
                print("Found {} Aurora device(s)".format(len(devices)))
                
                if not devices:
                    raise ConnectionError("No Aurora devices found")
                
                # Connect to first device
                print("Connecting to first device...")
                self.sdk.connect(device_info=devices[0])
            
            print("✓ Connected!")
            
            # Start 2D map generation first
            if not self.start_2d_map_generation():
                return False
            
            # CRITICAL: Enable map data syncing AFTER starting 2D map operations
            # (Enabling before causes segfaults, but after works perfectly!)
            print("Enabling map data syncing (delayed approach)...")
            time.sleep(1)  # Brief pause for 2D operations to stabilize
            self.sdk.enable_map_data_syncing(True)
            print("✓ Map data syncing enabled")
            
            return True
            
        except Exception as e:
            print("Failed to connect: {}".format(e))
            return False
    
    def start_2d_map_generation(self):
        """Start 2D occupancy grid map generation."""
        try:
            # Configure generation options (following C++ demo pattern)
            options = GridMapGenerationOptions()
            options.resolution = 0.05  # 5cm resolution
            options.map_canvas_width = 150.0  # 150m x 150m map  
            options.map_canvas_height = 150.0
            options.active_map_only = 1  # Generate active map only
            options.height_range_specified = 0  # Don't specify height range, use auto detection
            options.min_height = 0.0
            options.max_height = 0.0
            
            # Start background map generation AFTER enabling map data syncing
            print("Starting 2D map generation...")
            self.sdk.lidar_2d_map_builder.start_preview_map_background_update(options)
            print("✓ 2D map generation started")
            
            # Enable auto floor detection (following C++ demo)
            print("Enabling auto floor detection...")
            self.sdk.lidar_2d_map_builder.set_preview_map_auto_floor_detection(True)
            print("✓ Auto floor detection enabled")
            
            return True
            
        except Exception as e:
            print("Failed to start 2D map generation: {}".format(e))
            return False
    
    def get_map_data(self, force_redraw=False):
        """Get current 2D map data. Following C++ demo pattern."""
        try:
            # Trigger redraw if requested (following C++ demo pattern)
            if force_redraw:
                self.sdk.lidar_2d_map_builder.require_preview_map_redraw()
            
            # Get dirty rectangle (for status info, but don't rely on it for fetching)
            dirty_rect, map_changed = self.sdk.lidar_2d_map_builder.get_and_reset_preview_map_dirty_rect()
            
            # Always try to get the preview map (following C++ demo)
            preview_map = self.sdk.lidar_2d_map_builder.get_preview_map()
            if not preview_map:
                return None
            
            # Get map dimension (following C++ demo pattern)
            dimension = preview_map.get_map_dimension()
            
            # Always fetch the FULL map extent (following C++ demo pattern)
            fetch_rect = Rect()
            fetch_rect.x = dimension.min_x
            fetch_rect.y = dimension.min_y  
            fetch_rect.width = dimension.max_x - dimension.min_x
            fetch_rect.height = dimension.max_y - dimension.min_y
            
            # Skip if fetch rectangle is invalid
            if fetch_rect.width <= 0 or fetch_rect.height <= 0:
                return None
            
            # Read cell data for the entire map
            cell_data, fetch_info = preview_map.read_cell_data(fetch_rect)
            
            # Return data even if dirty rect is empty (unlike original approach)
            return {
                'cell_data': cell_data,
                'fetch_info': fetch_info,
                'dimension': dimension,
                'dirty_rect': dirty_rect,
                'map_changed': map_changed
            }
            
        except Exception as e:
            if "not implemented" not in str(e).lower():
                print("Error getting map data: {}".format(e))
                # Add debug info for dimension/rectangle issues
                if "int expected" in str(e):
                    try:
                        dirty_rect, _ = self.sdk.lidar_2d_map_builder.get_and_reset_preview_map_dirty_rect()
                        print("Debug - dirty_rect: x={}, y={}, w={}, h={}".format(dirty_rect.x, dirty_rect.y, dirty_rect.width, dirty_rect.height))
                    except:
                        pass
            return None
    
    def update_visualization(self, map_data):
        """Update map visualization."""
        if not MATPLOTLIB_AVAILABLE or not map_data:
            return
        
        try:
            cell_data = map_data['cell_data']
            fetch_info = map_data['fetch_info']
            dimension = map_data['dimension']
            
            # Check if we have valid data
            if not cell_data or fetch_info.cell_width <= 0 or fetch_info.cell_height <= 0:
                print("Warning: Invalid or empty map data")
                return
            
            # Convert cell data to numpy array and reshape
            if NUMPY_AVAILABLE:
                map_array = np.array(cell_data, dtype=np.uint8)
                expected_size = fetch_info.cell_height * fetch_info.cell_width
                if len(map_array) != expected_size:
                    print("Warning: Map data size mismatch. Expected {}, got {}".format(expected_size, len(map_array)))
                    return
                map_array = map_array.reshape(fetch_info.cell_height, fetch_info.cell_width)
                
                # Clear previous plot
                self.ax_map.clear()
                self.ax_map.set_title('LiDAR 2D Occupancy Grid Map')
                self.ax_map.set_xlabel('X (meters)')
                self.ax_map.set_ylabel('Y (meters)')
                
                # Display map with proper extent
                extent = [dimension.min_x, dimension.max_x, dimension.min_y, dimension.max_y]
                self.ax_map.imshow(map_array, cmap='gray', origin='lower', extent=extent)
                
                # Add controls text
                self.ax_map.text(0.02, 0.98, "Press 'r' to redraw, 'q' to exit", 
                               transform=self.ax_map.transAxes, 
                               verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
                self.ax_map.set_aspect('equal')
                
                # Store current data
                self.current_map_data = map_data
                
                # Update histogram (right side) - this was missing!
                self.update_histogram()
                
                plt.draw()
                
        except Exception as e:
            print("Error updating visualization: {}".format(e))
    
    def update_histogram(self):
        """Update floor detection histogram visualization (following C++ demo pattern)."""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        try:
            # Get floor detection histogram data
            histogram_info, histogram_data = self.sdk.floor_detector.get_detection_histogram()
            
            # Get floor descriptions and current floor ID
            floor_descriptions, current_floor_id = self.sdk.floor_detector.get_all_detection_info()
            
            # Clear previous histogram plot
            self.ax_hist.clear()
            self.ax_hist.set_title('Floor Detection Histogram')
            self.ax_hist.set_xlabel('Height (meters)')
            self.ax_hist.set_ylabel('Detection Count')
            
            if len(histogram_data) > 0 and histogram_info.bin_total_count > 0:
                # Create height bins for x-axis (following C++ demo)
                bin_centers = []
                for i in range(len(histogram_data)):
                    height = histogram_info.bin_height_start + (i * histogram_info.bin_width)
                    bin_centers.append(height)
                
                # Create bar chart (following C++ demo rectangle drawing)
                bars = self.ax_hist.bar(bin_centers, histogram_data, 
                                       width=histogram_info.bin_width * 0.8,  # Slightly narrower for clarity
                                       color='green', alpha=0.7, edgecolor='darkgreen')
                
                # Add value labels on bars
                for bar, value in zip(bars, histogram_data):
                    if value > 0:
                        height = bar.get_height()
                        self.ax_hist.text(bar.get_x() + bar.get_width()/2., height + max(histogram_data) * 0.01,
                                         f'{value:.1f}', ha='center', va='bottom', fontsize=8)
                
                # Set axis limits and labels
                self.ax_hist.set_xlim(histogram_info.bin_height_start - histogram_info.bin_width/2,
                                     histogram_info.bin_height_start + len(histogram_data) * histogram_info.bin_width + histogram_info.bin_width/2)
                self.ax_hist.set_ylim(0, max(histogram_data) * 1.1)
                
                # Add grid for better readability
                self.ax_hist.grid(True, alpha=0.3)
                
                # Add floor information text (following C++ demo console output)
                info_text = f"Current Floor ID: {current_floor_id}\n"
                info_text += f"Bins: {len(histogram_data)} (width: {histogram_info.bin_width:.2f}m)\n"
                info_text += f"Height range: {histogram_info.bin_height_start:.2f}m to {histogram_info.bin_height_start + len(histogram_data) * histogram_info.bin_width:.2f}m\n"
                
                if floor_descriptions:
                    info_text += "Detected Floors:\n"
                    for desc in floor_descriptions:
                        info_text += f"  Floor {desc.floorID}: {desc.typical_height:.2f}m (conf: {desc.confidence:.2f})\n"
                else:
                    info_text += "No floors detected yet"
                
                # Add info text to plot
                self.ax_hist.text(0.02, 0.98, info_text,
                                 transform=self.ax_hist.transAxes,
                                 verticalalignment='top',
                                 fontsize=8,
                                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
                
                # Highlight current floor if detected
                if floor_descriptions and current_floor_id >= 0:
                    for desc in floor_descriptions:
                        if desc.floorID == current_floor_id:
                            # Draw vertical line at current floor height
                            self.ax_hist.axvline(x=desc.typical_height, color='red', linestyle='--', linewidth=2, 
                                               label=f'Current Floor ({desc.typical_height:.2f}m)')
                            self.ax_hist.legend()
                            break
                
            else:
                # Show empty state
                self.ax_hist.text(0.5, 0.5, 'No histogram data\n(waiting for floor detection...)',
                                 ha='center', va='center', transform=self.ax_hist.transAxes,
                                 fontsize=12, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
            
            print(f"Histogram updated: {len(histogram_data)} bins, max value: {max(histogram_data) if histogram_data else 0:.1f}")
            
        except Exception as e:
            print("Error updating histogram: {}".format(e))
            # Show error state
            self.ax_hist.clear()
            self.ax_hist.set_title('Floor Detection Histogram - Error')
            self.ax_hist.text(0.5, 0.5, f'Error loading histogram:\n{str(e)}',
                             ha='center', va='center', transform=self.ax_hist.transAxes,
                             fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    
    def run_interactive(self, connection_string=None):
        """Run interactive visualization."""
        if not MATPLOTLIB_INTERACTIVE:
            print("Interactive mode not available, running in headless mode")
            return self.run_headless(connection_string)
        
        try:
            # Connect to device (this now includes starting 2D map generation)
            if not self.connect_to_device(connection_string):
                return 1
            
            print("\n=== Interactive 2D Map Visualization ===")
            print("Press 'r' to redraw map")
            print("Press 'q' to exit")
            print("Press 'h' for help")
            
            plt.show(block=False)
            
            # Initial redraw (following C++ demo pattern)
            print("Triggering initial redraw...")
            first_update = True
            
            # Main loop following C++ demo pattern
            last_update_time = time.time()
            
            while self.running and plt.get_fignums():
                try:
                    current_time = time.time()
                    
                    # Update map data every 0.5 seconds
                    if current_time - last_update_time >= 0.5:
                        # Force redraw on first update or periodically
                        force_redraw = first_update
                        map_data = self.get_map_data(force_redraw=force_redraw)
                        if map_data:
                            self.update_visualization(map_data)
                        first_update = False
                        last_update_time = current_time
                    
                    # Handle matplotlib events
                    plt.pause(0.1)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print("Error in main loop: {}".format(e))
                    time.sleep(1)
            
            return 0
            
        except Exception as e:
            print("Error in interactive mode: {}".format(e))
            return 1
        finally:
            self._cleanup()
    
    def run_headless(self, connection_string=None):
        """Run in headless mode, saving images periodically."""
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib not available for headless mode")
            return 1
        
        try:
            # Connect to device (this now includes starting 2D map generation)
            if not self.connect_to_device(connection_string):
                return 1
            
            print("\nRunning in headless mode - will save images every 10 seconds")
            print("Press Ctrl+C to exit")
            
            last_save_time = time.time()
            save_counter = 0
            first_save = True
            
            while self.running:
                try:
                    current_time = time.time()
                    
                    # Save image every 10 seconds
                    if current_time - last_save_time > 10.0:
                        # Force redraw on first save
                        force_redraw = first_save
                        map_data = self.get_map_data(force_redraw=force_redraw)
                        if map_data:
                            self.update_visualization(map_data)
                            
                            # Save current visualization
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            filename = "lidar_2dmap_{:03d}_{}".format(save_counter, timestamp)
                            
                            plt.savefig("{}.png".format(filename), dpi=150, bbox_inches='tight')
                            print("Saved: {}.png".format(filename))
                            
                            save_counter += 1
                            first_save = False
                            last_save_time = current_time
                    
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    print("\nCtrl-C pressed, exiting...")
                    break
                except Exception as e:
                    print("Error in headless mode: {}".format(e))
                    time.sleep(5)
            
            return 0
            
        except Exception as e:
            print("Headless mode error: {}".format(e))
            return 1
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources."""
        try:
            if self.sdk:
                # Stop 2D map generation
                try:
                    self.sdk.lidar_2d_map_builder.stop_preview_map_background_update()
                    print("✓ Stopped 2D map generation")
                except:
                    pass
                
                # Disable map data syncing
                try:
                    self.sdk.enable_map_data_syncing(False)
                    print("✓ Disabled map data syncing")
                except:
                    pass
                
                # Disconnect
                try:
                    self.sdk.disconnect()
                    print("✓ Disconnected")
                except:
                    pass
        except Exception as e:
            print("Cleanup error: {}".format(e))
    
    def run(self, connection_string=None):
        """Run the renderer."""
        if MATPLOTLIB_INTERACTIVE:
            return self.run_interactive(connection_string)
        else:
            return self.run_headless(connection_string)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LiDAR 2D Map Renderer')
    parser.add_argument('connection_string', nargs='?', help='Aurora device connection string (IP address)')
    args = parser.parse_args()
    
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is required for this demo")
        print("Install with: pip install matplotlib numpy")
        return 1
    
    # Setup signal handler
    def signal_handler(sig, frame):
        print("\nSignal received, exiting...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run renderer
    renderer = LiDAR2DMapRenderer()
    return renderer.run(args.connection_string)


if __name__ == '__main__':
    sys.exit(main())