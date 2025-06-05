#!/usr/bin/env python3
"""
Vector-based LiDAR Scan Plot Example

This example demonstrates how to retrieve and visualize 2D LiDAR scan data from Aurora device
using matplotlib for vector-based rendering with interactive zoom and pan capabilities.

Features:
- Real-time LiDAR scan visualization
- Interactive zoom and pan
- Distance rings for reference
- Point quality color coding
- Coordinate system display
- Statistics overlay

Usage:
    python lidar_scan_plot_vector.py [device_ip]
    
Example:
    python lidar_scan_plot_vector.py 192.168.1.212
"""

import sys
import os
import time
import math
import argparse
import threading
import signal
import warnings
from typing import Optional, List, Tuple

# Suppress numpy warnings about longdouble
warnings.filterwarnings("ignore", message=".*does not match any known type.*")

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

try:
    import matplotlib
    
    # Choose appropriate backend based on platform
    import platform
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        # Use native macOS backend for best performance and compatibility
        try:
            matplotlib.use('macosx')
        except ImportError:
            # Fallback to Qt if available
            try:
                matplotlib.use('Qt5Agg')
            except ImportError:
                try:
                    matplotlib.use('QtAgg')
                except ImportError:
                    # Use Agg backend as last resort (no GUI)
                    matplotlib.use('Agg')
                    print("Warning: No GUI backend available, using non-interactive Agg backend")
    elif system == 'linux':
        # Try Qt backends first, then Tk
        try:
            matplotlib.use('Qt5Agg')
        except ImportError:
            try:
                matplotlib.use('QtAgg')
            except ImportError:
                try:
                    matplotlib.use('TkAgg')
                except ImportError:
                    matplotlib.use('Agg')
                    print("Warning: No GUI backend available, using non-interactive Agg backend")
    elif system == 'windows':
        # Try Qt backends first, then Tk
        try:
            matplotlib.use('Qt5Agg')
        except ImportError:
            try:
                matplotlib.use('QtAgg')
            except ImportError:
                try:
                    matplotlib.use('TkAgg')
                except ImportError:
                    matplotlib.use('Agg')
                    print("Warning: No GUI backend available, using non-interactive Agg backend")
    else:
        # For other platforms, let matplotlib choose the default
        pass
    
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Circle
    import numpy as np
    
    print(f"Using matplotlib backend: {matplotlib.get_backend()}")
    
except ImportError:
    print("Error: matplotlib not available. Install with: pip install matplotlib")
    print()
    print("GUI Backend Requirements:")
    print("  macOS: Built-in macosx backend should work by default")
    print("  Linux: pip install PyQt5 (recommended) or sudo apt-get install python3-tk")
    print("  Windows: pip install PyQt5 (recommended) or use built-in Tkinter")
    sys.exit(1)

# Setup SDK import
AuroraSDK, AuroraSDKError, DataNotReadyError = setup_sdk_import()


class VectorLidarPlotter:
    """Interactive vector-based LiDAR scan plotter using matplotlib."""
    
    def __init__(self, device_ip: str, max_range: float = 10.0, update_interval: int = 100):
        """
        Initialize the LiDAR plotter.
        
        Args:
            device_ip: IP address of Aurora device
            max_range: Maximum display range in meters
            update_interval: Update interval in milliseconds
        """
        self.device_ip = device_ip
        self.max_range = max_range
        self.update_interval = update_interval
        
        # Aurora SDK
        self.sdk = None
        self.connected = False
        self.running = False
        
        # Plotting
        self.fig = None
        self.ax = None
        self.scan_scatter = None
        self.stats_text = None
        self.animation = None
        
        # Data
        self.scan_data = None
        self.last_update_time = 0
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\nShutting down...")
        self.stop()
        sys.exit(0)
    
    def setup_plot(self):
        """Setup the matplotlib figure and axes."""
        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.suptitle('Aurora LiDAR Scan Visualization (Vector)', fontsize=14)
        
        # Set up the plot
        self.ax.set_xlim(-self.max_range, self.max_range)
        self.ax.set_ylim(-self.max_range, self.max_range)
        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
        # Add distance rings for reference
        for radius in [1, 2, 5, 10]:
            if radius <= self.max_range:
                circle = Circle((0, 0), radius, fill=False, color='gray', alpha=0.3, linestyle='--')
                self.ax.add_patch(circle)
                # Add radius labels
                self.ax.text(radius * 0.707, radius * 0.707, f'{radius}m', 
                           fontsize=8, alpha=0.7, ha='center', va='center')
        
        # Add coordinate system
        self.ax.arrow(0, 0, 0.5, 0, head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.7)
        self.ax.arrow(0, 0, 0, 0.5, head_width=0.1, head_length=0.1, fc='green', ec='green', alpha=0.7)
        self.ax.text(0.6, 0, 'X', fontsize=10, color='red', fontweight='bold')
        self.ax.text(0, 0.6, 'Y', fontsize=10, color='green', fontweight='bold')
        
        # Initialize empty scatter plot for scan points
        self.scan_scatter = self.ax.scatter([], [], s=[], c=[], cmap='viridis', alpha=0.8)
        
        # Add statistics text
        self.stats_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes, 
                                     fontsize=10, verticalalignment='top',
                                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add colorbar for quality
        cbar = plt.colorbar(self.scan_scatter, ax=self.ax, shrink=0.8)
        cbar.set_label('Point Quality (RSSI)', rotation=270, labelpad=15)
        
        # Enable interactive navigation
        self.fig.canvas.toolbar_visible = True
        
        # Add instructions
        instruction_text = ("Instructions:\n"
                          "- Use mouse wheel to zoom\n"
                          "- Drag to pan\n"
                          "- Toolbar for additional tools\n"
                          "- Press Ctrl+C to exit")
        self.ax.text(0.02, 0.02, instruction_text, transform=self.ax.transAxes,
                    fontsize=8, verticalalignment='bottom',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    def connect_to_device(self) -> bool:
        """Connect to Aurora device."""
        try:
            print("Creating Aurora SDK instance...")
            self.sdk = AuroraSDK()
            
            # Get version info
            version_info = self.sdk.get_version_info()
            print("Aurora SDK Version: {}".format(version_info.get('version_string', 'Unknown')))
            
            print("SDK session created automatically...")
            
            print("Connecting to device at: {}".format(self.device_ip))
            try:
                self.sdk.connect(connection_string=self.device_ip)
            except Exception as e:
                print("Failed to connect to device: {}".format(e))
                return False
            
            print("Connected to Aurora device!")
            
            # Get device info
            try:
                device_info = self.sdk.get_device_info()
                if device_info:
                    print("Device Name: {}".format(device_info.device_name))
                    print("Device Model: {}".format(device_info.device_model_string))
            except Exception as e:
                print("Could not get device info: {}".format(e))
            
            # Wait for device to be ready
            print("Waiting for device to be ready...")
            ready_timeout = 10
            start_time = time.time()
            device_ready = False
            while time.time() - start_time < ready_timeout:
                try:
                    if self.sdk.is_connected():
                        # Try to get a scan to verify LiDAR is working
                        test_scan = self.sdk.get_recent_lidar_scan()
                        device_ready = True
                        break
                except:
                    pass
                time.sleep(0.5)
            
            if not device_ready:
                print("Warning: Device may not be fully ready, but proceeding anyway...")
            
            self.connected = True
            return True
            
        except Exception as e:
            print("Failed to connect to device: {}".format(e))
            return False
    
    def get_scan_data(self):
        """Get latest LiDAR scan data."""
        if not self.connected or not self.sdk:
            return None
        
        try:
            scan_data = self.sdk.get_recent_lidar_scan(max_points=8192)
            return scan_data
        except DataNotReadyError:
            # No scan data available yet
            return None
        except Exception as e:
            print("Error getting scan data: {}".format(e))
            return None
    
    def update_plot(self, frame):
        """Update the plot with new scan data."""
        # Get new scan data
        self.scan_data = self.get_scan_data()
        
        if self.scan_data is None:
            # Update stats to show no data
            stats_text = ("Status: No LiDAR data\n"
                         "Time: {:.1f}s".format(time.time() - self.last_update_time))
            self.stats_text.set_text(stats_text)
            return [self.scan_scatter, self.stats_text]
        
        # Convert scan data to cartesian coordinates (optimized)
        try:
            cartesian_points = self.scan_data.to_cartesian()
            valid_points = self.scan_data.get_valid_points()
            
            if not cartesian_points:
                # No valid points
                self.scan_scatter.set_offsets(np.empty((0, 2)))
                self.scan_scatter.set_sizes([])
                self.scan_scatter.set_array([])
            else:
                # Extract coordinates and quality using numpy for better performance
                cart_array = np.array(cartesian_points)
                valid_array = np.array(valid_points)
                
                if len(cart_array) > 0 and len(valid_array) > 0:
                    x_coords = cart_array[:, 0]
                    y_coords = cart_array[:, 1]
                    qualities = valid_array[:, 2]  # quality from valid_points
                    
                    # Filter points within display range using numpy vectorization
                    in_range_mask = (np.abs(x_coords) <= self.max_range) & (np.abs(y_coords) <= self.max_range)
                    
                    if np.any(in_range_mask):
                        filtered_points = cart_array[in_range_mask][:, :2]  # x, y only
                        filtered_qualities = qualities[in_range_mask]
                
                        # Update scatter plot
                        self.scan_scatter.set_offsets(filtered_points)
                        
                        # Set point sizes based on quality (vectorized)
                        sizes = np.clip(filtered_qualities * 2, 10, 50)
                        self.scan_scatter.set_sizes(sizes)
                        
                        # Set colors based on quality
                        self.scan_scatter.set_array(filtered_qualities)
                    else:
                        # No points in range
                        self.scan_scatter.set_offsets(np.empty((0, 2)))
                        self.scan_scatter.set_sizes([])
                        self.scan_scatter.set_array([])
                else:
                    # No valid data
                    self.scan_scatter.set_offsets(np.empty((0, 2)))
                    self.scan_scatter.set_sizes([])
                    self.scan_scatter.set_array([])
            
            # Update statistics (optimized)
            total_points = self.scan_data.get_scan_count()
            valid_count = len(valid_points)
            in_range_count = len(filtered_points) if 'filtered_points' in locals() and len(filtered_points) > 0 else 0
            
            # Calculate distance statistics using numpy
            if valid_points and len(valid_points) > 0:
                distances = valid_array[:, 0]  # distance is first element
                min_dist = np.min(distances)
                max_dist = np.max(distances)
                avg_dist = np.mean(distances)
                dist_stats = "Min: {:.2f}m, Max: {:.2f}m, Avg: {:.2f}m".format(min_dist, max_dist, avg_dist)
            else:
                dist_stats = "No distance data"
            
            stats_text = ("Scan Points: {} / {} valid / {} in range\n"
                         "Distance: {}\n"
                         "Update Rate: {:.1f} Hz\n"
                         "Zoom: Use mouse wheel | Pan: Drag".format(
                             total_points, valid_count, in_range_count, dist_stats,
                             1.0 / max(0.001, time.time() - self.last_update_time)))
            
            self.stats_text.set_text(stats_text)
            self.last_update_time = time.time()
            
        except Exception as e:
            error_stats = "Error processing scan data: {}".format(str(e)[:50])
            self.stats_text.set_text(error_stats)
        
        return [self.scan_scatter, self.stats_text]
    
    def start(self):
        """Start the visualization."""
        if not self.connect_to_device():
            return False
        
        print("Setting up plot...")
        self.setup_plot()
        
        print("Starting LiDAR scan visualization...")
        print("Use mouse wheel to zoom, drag to pan. Press Ctrl+C to exit.")
        
        self.running = True
        self.last_update_time = time.time()
        
        # Start animation with optimized settings
        self.animation = animation.FuncAnimation(
            self.fig, self.update_plot, interval=self.update_interval,
            blit=True, cache_frame_data=False, repeat=True)
        
        try:
            # Check if we're using a non-interactive backend
            if matplotlib.get_backend() == 'Agg':
                print("Error: No interactive GUI backend available.")
                print("The visualization requires a GUI backend to display plots.")
                print("Please install one of the following:")
                print("  macOS: Use the built-in macosx backend (should work by default)")
                print("  Linux/Windows: pip install PyQt5 or pip install tkinter")
                return False
            
            plt.show()
        except KeyboardInterrupt:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the visualization and cleanup."""
        print("Stopping visualization...")
        self.running = False
        
        if self.animation:
            try:
                self.animation.event_source.stop()
            except:
                pass
        
        if self.sdk and self.connected:
            try:
                self.sdk.disconnect()
                print("Disconnected from device")
            except Exception as e:
                print("Error disconnecting: {}".format(e))
        
        if self.fig:
            try:
                plt.close(self.fig)
            except:
                pass


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Vector-based LiDAR Scan Visualization')
    parser.add_argument('device_ip', nargs='?', default='192.168.1.212',
                       help='IP address of Aurora device (default: 192.168.1.212)')
    parser.add_argument('--max-range', type=float, default=10.0,
                       help='Maximum display range in meters (default: 10.0)')
    parser.add_argument('--update-rate', type=int, default=20,
                       help='Update rate in Hz (default: 20)')
    
    args = parser.parse_args()
    
    update_interval = int(1000 / args.update_rate)  # Convert Hz to milliseconds
    
    print("Aurora LiDAR Vector Visualization")
    print("Device IP: {}".format(args.device_ip))
    print("Max Range: {}m".format(args.max_range))
    print("Update Rate: {}Hz".format(args.update_rate))
    print()
    
    plotter = VectorLidarPlotter(args.device_ip, args.max_range, update_interval)
    
    try:
        if not plotter.start():
            print("Failed to start visualization")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)
    finally:
        plotter.stop()


if __name__ == "__main__":
    main()