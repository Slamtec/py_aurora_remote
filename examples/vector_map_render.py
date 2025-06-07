#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Map Render Example

This example demonstrates advanced map visualization using matplotlib vector graphics.
It provides interactive pan/zoom, real-time updates, and high-quality vector rendering
of VSLAM map data including map points, keyframe trajectories, and current pose.

Features:
- Interactive matplotlib interface with pan/zoom
- Vector-based rendering for high quality visualization
- Real-time map data updates
- 2D and optional 3D visualization modes
- Trajectory analysis and statistics
- Export capabilities (PNG, PDF, SVG)

Usage:
    python vector_map_render.py [connection_string]
    
Example:
    python vector_map_render.py 192.168.1.212
"""

import sys
import time
import argparse
import signal
import math
import threading
from typing import Optional, List, Tuple, Dict
from collections import deque

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

try:
    import matplotlib
    # Set interactive backend before importing pyplot
    import os
    import platform
    
    backend_set = False
    system = platform.system().lower()
    
    # Check for GUI environment: X11 display (Linux), Windows, or macOS
    if 'DISPLAY' in os.environ or os.name == 'nt' or system == 'darwin':
        # Try different backends in order of preference based on platform
        if system == 'darwin':  # macOS
            backends_to_try = [
                ('macosx', 'Native macOS backend (built-in)'),
                ('Qt5Agg', 'PyQt5'),
                ('QtAgg', 'PyQt6 or PyQt5'),
                ('TkAgg', 'brew install python-tk')
            ]
        elif system == 'linux':
            backends_to_try = [
                ('Qt5Agg', 'PyQt5'),
                ('QtAgg', 'PyQt6 or PyQt5'),
                ('TkAgg', 'tkinter (python3-tk)'),
                ('GTK3Agg', 'PyGObject'),
                ('GTKAgg', 'PyGTK')
            ]
        else:  # Windows or other
            backends_to_try = [
                ('Qt5Agg', 'PyQt5'),
                ('QtAgg', 'PyQt6 or PyQt5'),
                ('TkAgg', 'tkinter (usually included)'),
                ('GTK3Agg', 'PyGObject'),
                ('GTKAgg', 'PyGTK')
            ]
        
        for backend_name, install_hint in backends_to_try:
            try:
                matplotlib.use(backend_name, force=True)
                # Test if the backend actually works by importing pyplot
                import matplotlib.pyplot as plt_test
                backend_set = True
                print("Using matplotlib backend: {}".format(backend_name))
                break
            except (ImportError, ModuleNotFoundError) as e:
                # This backend is not available, try the next one
                continue
        
        if not backend_set:
            print("Warning: No interactive matplotlib backend available")
            print("To enable interactive display, install one of:")
            print("  macOS: Built-in macosx backend should work by default")
            print("  Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  Windows/Linux: pip install PyQt5")
            print("  Or: pip install PyGObject (Linux)")
            matplotlib.use('Agg')
    else:
        print("Info: No display detected, using non-interactive backend")
        matplotlib.use('Agg')
    
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Circle, Polygon
    from matplotlib.collections import LineCollection
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
    MATPLOTLIB_INTERACTIVE = matplotlib.get_backend() not in ['Agg', 'svg', 'pdf', 'ps']
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    MATPLOTLIB_INTERACTIVE = False
    print("Warning: matplotlib not available: {}".format(e))
    print("Install with: pip install matplotlib numpy")

try:
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_3D_AVAILABLE = True
except ImportError:
    MATPLOTLIB_3D_AVAILABLE = False

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError = setup_sdk_import()


class VectorMapRenderer:
    """Advanced vector-based map visualization using matplotlib."""
    
    def __init__(self, enable_3d=False, max_history=1000):
        self.sdk = None
        self.running = True
        self.enable_3d = enable_3d and MATPLOTLIB_3D_AVAILABLE
        self.max_history = max_history
        
        # Data storage
        self.map_points = []
        self.keyframes = []
        self.loop_closures = []
        self.current_pose = None
        self.pose_history = deque(maxlen=max_history)
        self.timestamp_history = deque(maxlen=max_history)
        
        # Matplotlib setup
        self.fig = None
        self.ax = None
        self.scatter_points = None
        self.trajectory_line = None
        self.pose_history_line = None
        self.current_pose_marker = None
        
        # Animation and threading
        self.ani = None
        self.data_lock = threading.Lock()
        self.last_update_time = 0
        
        # Statistics
        self.stats = {
            'total_points': 0,
            'total_keyframes': 0,
            'map_bounds': None,
            'trajectory_length': 0.0
        }
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C signal for graceful exit."""
        print("\nCtrl-C pressed, exiting...")
        self.running = False
        if self.ani:
            self.ani.event_source.stop()
        plt.close('all')
    
    def setup_matplotlib(self):
        """Initialize matplotlib figure and axes with enhanced interactive features."""
        if self.enable_3d:
            self.fig = plt.figure(figsize=(12, 9))
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.set_title('Aurora VSLAM Map - 3D Vector Visualization (Interactive)')
            self.ax.set_xlabel('X (meters)')
            self.ax.set_ylabel('Y (meters)')
            self.ax.set_zlabel('Z (meters)')
        else:
            self.fig, self.ax = plt.subplots(figsize=(12, 9))
            self.ax.set_title('Aurora VSLAM Map - Vector Visualization (Interactive)')
            self.ax.set_xlabel('X (meters)')
            self.ax.set_ylabel('Y (meters)')
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal')
        
        # Enable enhanced interactive features
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
        self.fig.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)
        
        # Pan/zoom state variables
        self.pan_active = False
        self.zoom_active = False
        self.last_mouse_pos = None
        self.zoom_factor = 1.1
        self.auto_scale = True
        
        # Enable matplotlib's built-in navigation toolbar
        self.fig.canvas.toolbar_visible = True
        
        # Initialize empty plots
        if self.enable_3d:
            # 3D plots
            self.scatter_points = self.ax.scatter([], [], [], s=1, c='green', alpha=0.6, label='Map Points')
            self.trajectory_line, = self.ax.plot([], [], [], 'r-', linewidth=2, label='Keyframe Trajectory')
            self.pose_history_line, = self.ax.plot([], [], [], 'b-', linewidth=1, alpha=0.7, label='Pose History')
            self.current_pose_marker, = self.ax.plot([], [], [], 'ro', markersize=8, label='Current Pose')
        else:
            # 2D plots
            self.scatter_points = self.ax.scatter([], [], s=2, c='green', alpha=0.6, label='Map Points')
            self.trajectory_line, = self.ax.plot([], [], 'r-', linewidth=2, label='Keyframe Trajectory')
            self.pose_history_line, = self.ax.plot([], [], 'b-', linewidth=1, alpha=0.7, label='Pose History')
            self.current_pose_marker, = self.ax.plot([], [], 'ro', markersize=8, label='Current Pose')
        
        self.ax.legend()
        
        # Add text for statistics
        self.stats_text = self.fig.text(0.02, 0.98, '', transform=self.fig.transFigure,
                                       verticalalignment='top', fontsize=10,
                                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
    
    def _on_key_press(self, event):
        """Handle keyboard events with enhanced controls."""
        if event.key == 'q' or event.key == 'escape':
            self.running = False
            if self.ani:
                self.ani.event_source.stop()
            plt.close('all')
        elif event.key == 'r':
            # Reset view
            self._reset_view()
        elif event.key == 's':
            # Save current visualization
            self._save_visualization()
        elif event.key == 'c':
            # Clear data
            self._clear_data()
        elif event.key == '3':
            # Toggle 3D mode (if available)
            if MATPLOTLIB_3D_AVAILABLE:
                self._toggle_3d_mode()
        elif event.key == ' ':
            # Print statistics
            self._print_statistics()
        elif event.key == 'a':
            # Toggle auto-scale
            self.auto_scale = not self.auto_scale
            print("Auto-scale: {}".format('ON' if self.auto_scale else 'OFF'))
        elif event.key == 'h':
            # Show help
            self._show_help()
    
    def _on_mouse_press(self, event):
        """Handle mouse press events."""
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:  # Left mouse button - pan
            self.pan_active = True
            self.last_mouse_pos = (event.xdata, event.ydata)
            self.fig.canvas.set_cursor(1)  # Hand cursor
        elif event.button == 3:  # Right mouse button - zoom
            self.zoom_active = True
            self.last_mouse_pos = (event.xdata, event.ydata)
            self.fig.canvas.set_cursor(2)  # Cross cursor
    
    def _on_mouse_release(self, event):
        """Handle mouse release events."""
        if event.button == 1:
            self.pan_active = False
        elif event.button == 3:
            self.zoom_active = False
        
        self.fig.canvas.set_cursor(0)  # Normal cursor
        self.last_mouse_pos = None
    
    def _on_mouse_move(self, event):
        """Handle mouse movement for pan and zoom."""
        if event.inaxes != self.ax or self.last_mouse_pos is None:
            return
        
        if self.pan_active and event.xdata is not None and event.ydata is not None:
            # Pan functionality
            dx = event.xdata - self.last_mouse_pos[0]
            dy = event.ydata - self.last_mouse_pos[1]
            
            # Get current axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # Update limits
            self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            
            # Disable auto-scale during manual pan
            self.auto_scale = False
            
            self.fig.canvas.draw_idle()
        
        elif self.zoom_active and event.xdata is not None and event.ydata is not None:
            # Zoom functionality
            dy = event.ydata - self.last_mouse_pos[1]
            zoom_scale = 1.0 + dy * 0.01  # Zoom sensitivity
            
            # Get current center and range
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            center_x = (xlim[0] + xlim[1]) / 2
            center_y = (ylim[0] + ylim[1]) / 2
            range_x = (xlim[1] - xlim[0]) / 2
            range_y = (ylim[1] - ylim[0]) / 2
            
            # Apply zoom
            new_range_x = range_x * zoom_scale
            new_range_y = range_y * zoom_scale
            
            self.ax.set_xlim(center_x - new_range_x, center_x + new_range_x)
            self.ax.set_ylim(center_y - new_range_y, center_y + new_range_y)
            
            # Disable auto-scale during manual zoom
            self.auto_scale = False
            
            self.fig.canvas.draw_idle()
            self.last_mouse_pos = (event.xdata, event.ydata)
    
    def _on_scroll(self, event):
        """Handle mouse scroll wheel for zooming."""
        if event.inaxes != self.ax:
            return
        
        # Determine zoom direction
        if event.step > 0:
            zoom_scale = 1.0 / self.zoom_factor  # Zoom in
        else:
            zoom_scale = self.zoom_factor  # Zoom out
        
        # Get current axis limits and mouse position
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        if event.xdata is not None and event.ydata is not None:
            # Zoom towards mouse cursor
            mouse_x = event.xdata
            mouse_y = event.ydata
        else:
            # Zoom towards center if mouse is outside plot
            mouse_x = (xlim[0] + xlim[1]) / 2
            mouse_y = (ylim[0] + ylim[1]) / 2
        
        # Calculate new limits
        x_range = (xlim[1] - xlim[0]) * zoom_scale
        y_range = (ylim[1] - ylim[0]) * zoom_scale
        
        # Keep mouse position fixed during zoom
        x_ratio = (mouse_x - xlim[0]) / (xlim[1] - xlim[0])
        y_ratio = (mouse_y - ylim[0]) / (ylim[1] - ylim[0])
        
        new_xlim = [mouse_x - x_range * x_ratio, mouse_x + x_range * (1 - x_ratio)]
        new_ylim = [mouse_y - y_range * y_ratio, mouse_y + y_range * (1 - y_ratio)]
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        
        # Disable auto-scale during manual zoom
        self.auto_scale = False
        
        self.fig.canvas.draw_idle()
    
    def _show_help(self):
        """Display help information."""
        help_text = """
=== Aurora Vector Map Render - Interactive Controls ===

Mouse Controls:
  • Left Click + Drag: Pan the view
  • Right Click + Drag: Zoom (drag up/down)
  • Scroll Wheel: Zoom in/out towards cursor

Keyboard Controls:
  • 'r': Reset view to fit all data
  • 'a': Toggle auto-scale ON/OFF
  • 's': Save visualization to file
  • 'c': Clear all data
  • '3': Toggle 3D mode (if available)
  • 'h': Show this help
  • 'q'/'Escape': Quit

Statistics:
  • Spacebar: Print current statistics

Toolbar:
  • Use matplotlib toolbar for additional tools
  • Pan, zoom, configure subplots, save options
        """
        print(help_text)
    
    def _reset_view(self):
        """Reset the view to fit all data."""
        with self.data_lock:
            if self.map_points or self.keyframes or self.pose_history:
                self._update_view_bounds()
    
    def _save_visualization(self):
        """Save the current visualization to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = "aurora_map_{}".format(timestamp)
        
        # Save as high-quality PNG
        self.fig.savefig("{}.png".format(filename), dpi=300, bbox_inches='tight')
        
        # Save as vector PDF
        self.fig.savefig("{}.pdf".format(filename), bbox_inches='tight')
        
        print("Visualization saved as {}.png and {}.pdf".format(filename, filename))
    
    def _clear_data(self):
        """Clear all map data."""
        with self.data_lock:
            self.map_points.clear()
            self.keyframes.clear()
            self.pose_history.clear()
            self.timestamp_history.clear()
            self.current_pose = None
            print("Map data cleared")
    
    def _toggle_3d_mode(self):
        """Toggle between 2D and 3D visualization."""
        # This would require recreating the plot - for now just print message
        mode = "3D" if not self.enable_3d else "2D"
        print("3D mode toggle not implemented in real-time. Restart with --3d for {} mode.".format(mode))
    
    def _print_statistics(self):
        """Print current map statistics."""
        with self.data_lock:
            print("\n=== Map Statistics ===")
            print("Map Points: {}".format(len(self.map_points)))
            print("Keyframes: {}".format(len(self.keyframes)))
            print("Pose History: {}".format(len(self.pose_history)))
            if self.stats['map_bounds']:
                bounds = self.stats['map_bounds']
                print("Map Bounds: X=[{:.2f}, {:.2f}], Y=[{:.2f}, {:.2f}]".format(bounds[0], bounds[1], bounds[2], bounds[3]))
            print("Trajectory Length: {:.2f}m".format(self.stats['trajectory_length']))
            if self.current_pose:
                print("Current Pose: ({:.3f}, {:.3f}, {:.3f})".format(self.current_pose[0], self.current_pose[1], self.current_pose[2]))
    
    def update_data(self, new_map_points, new_keyframes, new_current_pose, new_loop_closures=None):
        """Update map data thread-safely."""
        with self.data_lock:
            # Update map points
            if new_map_points:
                self.map_points = new_map_points
            
            # Update keyframes
            if new_keyframes:
                self.keyframes = new_keyframes
                # Calculate trajectory length
                if len(self.keyframes) > 1:
                    total_length = 0.0
                    for i in range(1, len(self.keyframes)):
                        dx = self.keyframes[i][0] - self.keyframes[i-1][0]
                        dy = self.keyframes[i][1] - self.keyframes[i-1][1]
                        dz = self.keyframes[i][2] - self.keyframes[i-1][2] if len(self.keyframes[i]) > 2 else 0
                        total_length += math.sqrt(dx*dx + dy*dy + dz*dz)
                    self.stats['trajectory_length'] = total_length
            
            # Update loop closures
            if new_loop_closures is not None:
                self.loop_closures = new_loop_closures
                if len(new_loop_closures) > 0:
                    print(f"DEBUG: Updated loop closures: {new_loop_closures[:5]}...")  # Show first 5
            
            # Update current pose
            if new_current_pose:
                self.current_pose = new_current_pose
                current_time = time.time()
                self.pose_history.append((new_current_pose[0], new_current_pose[1], new_current_pose[2]))
                self.timestamp_history.append(current_time)
            
            # Update statistics
            self.stats['total_points'] = len(self.map_points)
            self.stats['total_keyframes'] = len(self.keyframes)
            
            self.last_update_time = time.time()
    
    def _calculate_bounds(self):
        """Calculate bounds for all data."""
        all_x, all_y, all_z = [], [], []
        
        # Add map points
        if self.map_points:
            all_x.extend([p['position'][0] for p in self.map_points])
            all_y.extend([p['position'][1] for p in self.map_points])
            all_z.extend([p['position'][2] for p in self.map_points])
        
        # Add keyframes
        if self.keyframes:
            all_x.extend([k['position'][0] for k in self.keyframes])
            all_y.extend([k['position'][1] for k in self.keyframes])
            all_z.extend([k['position'][2] for k in self.keyframes])
        
        # Add pose history
        if self.pose_history:
            all_x.extend([p[0] for p in self.pose_history])
            all_y.extend([p[1] for p in self.pose_history])
            all_z.extend([p[2] for p in self.pose_history])
        
        if all_x and all_y:
            margin = 2.0  # 2 meter margin
            bounds = [
                min(all_x) - margin, max(all_x) + margin,
                min(all_y) - margin, max(all_y) + margin
            ]
            if all_z and self.enable_3d:
                bounds.extend([min(all_z) - margin, max(all_z) + margin])
            return bounds
        return None
    
    def _update_view_bounds(self):
        """Update the view to show all data."""
        bounds = self._calculate_bounds()
        if bounds:
            self.stats['map_bounds'] = bounds
            if self.enable_3d:
                self.ax.set_xlim(bounds[0], bounds[1])
                self.ax.set_ylim(bounds[2], bounds[3])
                if len(bounds) > 4:
                    self.ax.set_zlim(bounds[4], bounds[5])
            else:
                self.ax.set_xlim(bounds[0], bounds[1])
                self.ax.set_ylim(bounds[2], bounds[3])
    
    def animate_frame(self, frame):
        """Animation frame update function."""
        with self.data_lock:
            # Update map points
            if self.map_points:
                if self.enable_3d:
                    self.scatter_points._offsets3d = (
                        [p['position'][0] for p in self.map_points],
                        [p['position'][1] for p in self.map_points],
                        [p['position'][2] for p in self.map_points]
                    )
                else:
                    if len(self.map_points) > 0:
                        points = np.array([[p['position'][0], p['position'][1]] for p in self.map_points])
                        self.scatter_points.set_offsets(points)
            
            # Update keyframe trajectory
            if self.keyframes and len(self.keyframes) > 1:
                if self.enable_3d:
                    self.trajectory_line.set_data_3d(
                        [k['position'][0] for k in self.keyframes],
                        [k['position'][1] for k in self.keyframes],
                        [k['position'][2] for k in self.keyframes]
                    )
                else:
                    self.trajectory_line.set_data(
                        [k['position'][0] for k in self.keyframes],
                        [k['position'][1] for k in self.keyframes]
                    )
            
            # Update pose history
            if self.pose_history and len(self.pose_history) > 1:
                if self.enable_3d:
                    self.pose_history_line.set_data_3d(
                        [p[0] for p in self.pose_history],
                        [p[1] for p in self.pose_history],
                        [p[2] for p in self.pose_history]
                    )
                else:
                    self.pose_history_line.set_data(
                        [p[0] for p in self.pose_history],
                        [p[1] for p in self.pose_history]
                    )
            
            # Update current pose marker
            if self.current_pose:
                if self.enable_3d:
                    self.current_pose_marker.set_data_3d(
                        [self.current_pose[0]],
                        [self.current_pose[1]],
                        [self.current_pose[2]]
                    )
                else:
                    self.current_pose_marker.set_data(
                        [self.current_pose[0]],
                        [self.current_pose[1]]
                    )
            
            # Update statistics text
            auto_scale_status = "ON" if self.auto_scale else "OFF"
            stats_text = ("Map Points: {}\n"
                         "Keyframes: {}\n"
                         "Pose History: {}\n"
                         "Trajectory: {:.1f}m\n"
                         "Auto-scale: {}\n"
                         "Last Update: {}\n"
                         "Press 'h' for help").format(
                             len(self.map_points),
                             len(self.keyframes),
                             len(self.pose_history),
                             self.stats['trajectory_length'],
                             auto_scale_status,
                             time.strftime('%H:%M:%S', time.localtime(self.last_update_time))
                         )
            self.stats_text.set_text(stats_text)
            
            # Auto-adjust view bounds periodically (only if auto-scale is enabled)
            if self.auto_scale and frame % 30 == 0:  # Every 30 frames (~1 second at 30fps)
                self._update_view_bounds()
        
        # Return all artists that were modified
        artists = [self.scatter_points, self.trajectory_line, self.pose_history_line, 
                  self.current_pose_marker, self.stats_text]
        return artists
    
    def data_acquisition_thread(self, connection_string):
        """Background thread for data acquisition from Aurora SDK."""
        try:
            # SDK setup
            print("Creating Aurora SDK instance...")
            self.sdk = AuroraSDK()
            
            try:
                version_info = self.sdk.get_version_info()
                print("Aurora SDK Version: {}".format(version_info['version_string']))
            except Exception as e:
                print("Warning: Could not get SDK version: {}".format(e))
            
            print("SDK session created automatically...")
            
            # Connect to device
            if connection_string:
                print("Connecting to device at: {}".format(connection_string))
                self.sdk.connect(connection_string=connection_string)
            else:
                print("Discovering Aurora devices...")
                devices = self.sdk.discover_devices(timeout=5.0)
                
                if not devices:
                    print("No Aurora devices found!")
                    return
                
                print("Found {} Aurora device(s)".format(len(devices)))
                print("Connecting to first device...")
                self.sdk.connect(device_info=devices[0])
            
            print("Connected to Aurora device!")
            
            # Enable map data syncing (using same pattern as working map_render.py)
            try:
                print("Enabling map data syncing...")
                self.sdk.enable_map_data_syncing(True)
                print("Map data syncing enabled")
            except Exception as e:
                print("Warning: Could not enable map data syncing: {}".format(e))
            
            # Sync map data using the same approach as working map_render.py
            try:
                print("Syncing map data...")
                self.sdk.controller.resync_map_data()
                print("Map data sync requested")
            except Exception as e:
                print("Warning: Could not sync map data: {}".format(e))
            
            # Data acquisition loop
            last_map_refresh = 0
            while self.running:
                try:
                    current_time = time.time()
                    
                    # Get current pose
                    try:
                        position, rotation, timestamp = self.sdk.get_current_pose(use_se3=True)
                        current_pose = position + rotation
                    except DataNotReadyError:
                        current_pose = None
                    
                    # Get map data periodically
                    map_points, keyframes = None, None
                    if current_time - last_map_refresh > 2.0:
                        try:
                            map_data = self.sdk.get_map_data()
                            if map_data:
                                map_points = map_data.get('map_points', [])
                                keyframes = map_data.get('keyframes', [])
                                loop_closures = map_data.get('loop_closures', [])
                                if map_points or keyframes:
                                    print("Updated: {} map points, {} keyframes, {} loop closures".format(len(map_points), len(keyframes), len(loop_closures)))
                                last_map_refresh = current_time
                        except DataNotReadyError:
                            pass
                        except Exception as e:
                            if "not implemented" not in str(e).lower():
                                print("Map data error: {}".format(e))
                    
                    # Update visualization data
                    self.update_data(map_points, keyframes, current_pose, loop_closures)
                    
                    time.sleep(0.1)  # 10Hz update rate
                    
                except Exception as e:
                    print("Error in data acquisition: {}".format(e))
                    time.sleep(1.0)
        
        except Exception as e:
            print("Data acquisition thread error: {}".format(e))
        finally:
            if self.sdk:
                try:
                    self.sdk.enable_map_data_syncing(False)
                    self.sdk.disconnect()
                    self.sdk.release()
                except:
                    pass
    
    def run(self, connection_string=None):
        """Run the vector map renderer."""
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib is required for this demo.")
            print("Install with: pip install matplotlib")
            return 1
        
        if not MATPLOTLIB_INTERACTIVE:
            print("Warning: matplotlib is using a non-interactive backend.")
            print("The visualization window may not display properly.")
            print("To fix this, install one of the following:")
            print("  - tkinter: sudo apt-get install python3-tk (Ubuntu/Debian)")
            print("  - PyQt5: pip install PyQt5")
            print("  - For headless systems, the script will save images instead.")
            
            # For non-interactive mode, we'll run a simplified version
            return self._run_headless(connection_string)
        
        # For interactive mode, use enhanced approach with zoom/pan
        print("\nUsing {} backend...".format(matplotlib.get_backend()))
        print("Creating enhanced interactive visualization with zoom/pan support")
        print("\n=== ENHANCED INTERACTIVE FEATURES ===")
        print("Mouse Controls:")
        print("  • Left Click + Drag: Pan the view")
        print("  • Right Click + Drag: Zoom (drag up/down)")
        print("  • Scroll Wheel: Zoom in/out towards cursor")
        print("Keyboard Controls:")
        print("  • 'h': Show full help")
        print("  • 'r': Reset view to fit all data")
        print("  • 'a': Toggle auto-scale ON/OFF")
        print("  • 'q': Quit")
        print("🎯 NEW Features:")
        print("  • View Persistence: Zoom/pan preserved during refresh")
        print("  • Loop Closure Detection: Special color for loop connections")
        print("  • Smart trajectory visualization with loop highlighting")
        print("=======================================\n")
        return self._run_interactive_simple(connection_string)
    
    def _run_interactive_simple(self, connection_string=None):
        """Run interactive mode with slow refresh - safer approach."""
        sdk = None
        
        try:
            print("Connecting to Aurora device...")
            sdk = AuroraSDK()
            # Session created automatically
            
            # Connect to device (with discovery if no connection string provided)
            if connection_string:
                print("Connecting to device at: {}".format(connection_string))
                sdk.connect(connection_string=connection_string)
            else:
                print("Discovering Aurora devices...")
                devices = sdk.discover_devices(timeout=5.0)
                
                if not devices:
                    print("No Aurora devices found!")
                    return 1
                
                print("Found {} Aurora device(s)".format(len(devices)))
                print("Connecting to first device...")
                sdk.connect(device_info=devices[0])
            
            print("✓ Connected!")
            
            # Enable map data syncing (same pattern as working map_render.py)
            print("Enabling map data syncing...")
            sdk.enable_map_data_syncing(True)
            print("✓ Map data syncing enabled")
            
            # Sync map data
            print("Syncing map data...")
            sdk.controller.resync_map_data()
            print("✓ Map data sync requested")
            
            print("\nStarting interactive visualization with live updates...")
            print("Refreshing every 2 seconds - Close window to exit")
            
            # Create enhanced interactive figure and axes
            plt.ion()  # Turn on interactive mode
            fig, ax = plt.subplots(figsize=(12, 9))
            ax.set_title('Aurora VSLAM Map - Vector Visualization (Interactive)')
            ax.set_xlabel('X (meters)')
            ax.set_ylabel('Y (meters)')
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
            
            # Enhanced interactive features setup
            pan_active = False
            zoom_active = False
            last_mouse_pos = None
            zoom_factor = 1.1
            auto_scale = True
            
            # View state preservation
            saved_xlim = None
            saved_ylim = None
            view_manually_set = False
            
            # Loop closure detection settings
            loop_closure_threshold = 2.0  # Distance threshold for detecting loops (meters)
            loop_closure_color = 'cyan'   # Special color for loop connections
            show_loop_closures = True     # Enable/disable loop closure visualization
            
            # Enable matplotlib's built-in navigation toolbar
            fig.canvas.toolbar_visible = True
            
            # Loop closure detection is now handled by the Aurora SDK directly
            # Real loop closure data is provided via the looped_frame_ids in the C SDK callback
            
            def on_key_press(event):
                nonlocal auto_scale, saved_xlim, saved_ylim, view_manually_set, show_loop_closures
                if event.key == 'q' or event.key == 'escape':
                    plt.close('all')
                elif event.key == 'r':
                    # Reset view to fit all data
                    auto_scale = True
                    view_manually_set = False
                    saved_xlim = None
                    saved_ylim = None
                    ax.relim()
                    ax.autoscale()
                    fig.canvas.draw()
                    print("View reset - Auto-scale: ON")
                elif event.key == 'a':
                    auto_scale = not auto_scale
                    if auto_scale:
                        # When enabling auto-scale, clear saved view
                        saved_xlim = None
                        saved_ylim = None
                        view_manually_set = False
                    else:
                        # When disabling auto-scale, save current view
                        saved_xlim = ax.get_xlim()
                        saved_ylim = ax.get_ylim()
                        view_manually_set = True
                    print("Auto-scale: {}".format('ON' if auto_scale else 'OFF'))
                elif event.key == 'l':
                    # Toggle loop closure visualization
                    show_loop_closures = not show_loop_closures
                    print("Loop closures: {}".format('ON' if show_loop_closures else 'OFF'))
                elif event.key == 'h':
                    print("""
=== Aurora Vector Map Render - Interactive Controls ===

Mouse Controls:
  • Left Click + Drag: Pan the view (preserves zoom/pan on refresh)
  • Right Click + Drag: Zoom (drag up/down, preserves on refresh)
  • Scroll Wheel: Zoom in/out towards cursor (preserves on refresh)

Keyboard Controls:
  • 'r': Reset view to fit all data and enable auto-scale
  • 'a': Toggle auto-scale ON/OFF
  • 'l': Toggle loop closure visualization ON/OFF
  • 'h': Show this help
  • 'q'/'Escape': Quit

View Persistence:
  • Manual zoom/pan is preserved between map refreshes
  • Auto-scale automatically disabled when manually zooming/panning
  • View status shown in statistics (Auto/Manual)

Loop Closure Detection:
  • Cyan lines show detected loop closures in trajectory
  • Helps identify when robot revisits previous locations
  • Threshold: 2.0 meters for loop detection

Toolbar:
  • Use matplotlib toolbar for additional tools
                    """)
            
            def on_mouse_press(event):
                nonlocal pan_active, zoom_active, last_mouse_pos
                if event.inaxes != ax:
                    return
                if event.button == 1:  # Left mouse button - pan
                    pan_active = True
                    last_mouse_pos = (event.xdata, event.ydata)
                elif event.button == 3:  # Right mouse button - zoom
                    zoom_active = True
                    last_mouse_pos = (event.xdata, event.ydata)
            
            def on_mouse_release(event):
                nonlocal pan_active, zoom_active, last_mouse_pos
                pan_active = False
                zoom_active = False
                last_mouse_pos = None
            
            def on_mouse_move(event):
                nonlocal pan_active, zoom_active, last_mouse_pos, auto_scale, saved_xlim, saved_ylim, view_manually_set
                if event.inaxes != ax or last_mouse_pos is None:
                    return
                
                if pan_active and event.xdata is not None and event.ydata is not None:
                    # Pan functionality
                    dx = event.xdata - last_mouse_pos[0]
                    dy = event.ydata - last_mouse_pos[1]
                    xlim = ax.get_xlim()
                    ylim = ax.get_ylim()
                    new_xlim = (xlim[0] - dx, xlim[1] - dx)
                    new_ylim = (ylim[0] - dy, ylim[1] - dy)
                    ax.set_xlim(new_xlim)
                    ax.set_ylim(new_ylim)
                    
                    # Save view state
                    auto_scale = False
                    saved_xlim = new_xlim
                    saved_ylim = new_ylim
                    view_manually_set = True
                    fig.canvas.draw_idle()
                
                elif zoom_active and event.xdata is not None and event.ydata is not None:
                    # Zoom functionality
                    dy = event.ydata - last_mouse_pos[1]
                    zoom_scale = 1.0 + dy * 0.01
                    xlim = ax.get_xlim()
                    ylim = ax.get_ylim()
                    center_x = (xlim[0] + xlim[1]) / 2
                    center_y = (ylim[0] + ylim[1]) / 2
                    range_x = (xlim[1] - xlim[0]) / 2 * zoom_scale
                    range_y = (ylim[1] - ylim[0]) / 2 * zoom_scale
                    new_xlim = (center_x - range_x, center_x + range_x)
                    new_ylim = (center_y - range_y, center_y + range_y)
                    ax.set_xlim(new_xlim)
                    ax.set_ylim(new_ylim)
                    
                    # Save view state
                    auto_scale = False
                    saved_xlim = new_xlim
                    saved_ylim = new_ylim
                    view_manually_set = True
                    fig.canvas.draw_idle()
                    last_mouse_pos = (event.xdata, event.ydata)
            
            def on_scroll(event):
                nonlocal auto_scale, saved_xlim, saved_ylim, view_manually_set
                if event.inaxes != ax:
                    return
                
                # Determine zoom direction
                zoom_scale = 1.0 / zoom_factor if event.step > 0 else zoom_factor
                
                # Get current axis limits and mouse position
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                
                if event.xdata is not None and event.ydata is not None:
                    mouse_x, mouse_y = event.xdata, event.ydata
                else:
                    mouse_x = (xlim[0] + xlim[1]) / 2
                    mouse_y = (ylim[0] + ylim[1]) / 2
                
                # Calculate new limits
                x_range = (xlim[1] - xlim[0]) * zoom_scale
                y_range = (ylim[1] - ylim[0]) * zoom_scale
                x_ratio = (mouse_x - xlim[0]) / (xlim[1] - xlim[0])
                y_ratio = (mouse_y - ylim[0]) / (ylim[1] - ylim[0])
                
                new_xlim = [mouse_x - x_range * x_ratio, mouse_x + x_range * (1 - x_ratio)]
                new_ylim = [mouse_y - y_range * y_ratio, mouse_y + y_range * (1 - y_ratio)]
                
                ax.set_xlim(new_xlim)
                ax.set_ylim(new_ylim)
                
                # Save view state
                auto_scale = False
                saved_xlim = tuple(new_xlim)
                saved_ylim = tuple(new_ylim)
                view_manually_set = True
                fig.canvas.draw_idle()
            
            # Connect event handlers
            fig.canvas.mpl_connect('key_press_event', on_key_press)
            fig.canvas.mpl_connect('button_press_event', on_mouse_press)
            fig.canvas.mpl_connect('button_release_event', on_mouse_release)
            fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
            fig.canvas.mpl_connect('scroll_event', on_scroll)
            
            # Initialize plots (will be updated in loop)
            map_points_plot = None
            keyframe_line = None
            keyframe_points = None
            current_pose_plot = None
            stats_text = None
            
            last_update_time = 0
            
            # Keep the plot alive and refresh data
            while True:
                current_time = time.time()
                
                # Update data every 2 seconds
                if current_time - last_update_time >= 2.0:
                    #try:
                        # Get fresh map data
                        map_data = sdk.get_map_data()
                        if map_data:
                            map_points = map_data.get('map_points', [])
                            keyframes = map_data.get('keyframes', [])
                            loop_closures = map_data.get('loop_closures', [])
                        else:
                            map_points, keyframes, loop_closures = [], [], []
                        
                        # Get current pose
                        try:
                            position, rotation, timestamp = sdk.get_current_pose(use_se3=True)
                            current_pose = position
                        except DataNotReadyError:
                            current_pose = None
                        
                        # Clear the axes
                        ax.clear()
                        ax.set_title('Aurora VSLAM Map - Live Interactive Visualization')
                        ax.set_xlabel('X (meters)')
                        ax.set_ylabel('Y (meters)')
                        ax.grid(True, alpha=0.3)
                        ax.set_aspect('equal')
                        
                        # Plot map points
                        if map_points:
                            x_coords = [p['position'][0] for p in map_points]
                            y_coords = [p['position'][1] for p in map_points]
                            ax.scatter(x_coords, y_coords, s=2, c='green', alpha=0.6, 
                                     label='Map Points ({})'.format(len(map_points)))
                        
                        # Plot keyframe trajectory
                        loop_count = 0
                        if keyframes and len(keyframes) > 1:
                            x_coords = [k['position'][0] for k in keyframes]
                            y_coords = [k['position'][1] for k in keyframes]
                            ax.plot(x_coords, y_coords, 'r-', linewidth=2, 
                                   label='Keyframe Trajectory ({})'.format(len(keyframes)))
                            ax.scatter(x_coords, y_coords, c='red', s=20, zorder=5)
                            
                            # Plot loop closures using real loop closure data from SDK
                            if show_loop_closures and loop_closures:
                                loop_count = len(loop_closures)
                                
                                # Create a mapping from keyframe ID to keyframe position
                                kf_id_to_pos = {}
                                for i, kf in enumerate(keyframes):
                                    # Keyframe dict format with id, position, etc.
                                    kf_id_to_pos[kf['id']] = (kf['position'][0], kf['position'][1])  # Map ID to (x, y)
                                
                                # Draw loop closure connections using real loop closure data
                                actual_connections_drawn = 0
                                missing_keyframes = []
                                for from_kf_id, to_kf_id in loop_closures:
                                    if from_kf_id in kf_id_to_pos and to_kf_id in kf_id_to_pos:
                                        pos1 = kf_id_to_pos[from_kf_id]
                                        pos2 = kf_id_to_pos[to_kf_id]
                                        
                                        # Draw loop closure connection
                                        ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                                               color=loop_closure_color, linewidth=3, alpha=0.7, 
                                               zorder=6, linestyle='--')
                                        
                                        # Add small markers at loop closure points
                                        ax.scatter([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                                                 c=loop_closure_color, s=50, marker='o', 
                                                 edgecolors='black', linewidth=1, zorder=7)
                                        actual_connections_drawn += 1
                                    else:
                                        # Track missing keyframes for debugging
                                        if from_kf_id not in kf_id_to_pos:
                                            missing_keyframes.append(from_kf_id)
                                        if to_kf_id not in kf_id_to_pos:
                                            missing_keyframes.append(to_kf_id)
                                
                                # Debug info for missing keyframes
                                if missing_keyframes and len(missing_keyframes) < 10:  # Don't spam too much
                                    print(f"Warning: Loop closures reference missing keyframes: {set(missing_keyframes)}")
                                    print(f"Available keyframe IDs: {sorted(list(kf_id_to_pos.keys())[:10])}...")  # Show first 10
                                
                                # Add loop closures to legend if any found
                                if actual_connections_drawn > 0:
                                    ax.plot([], [], color=loop_closure_color, linewidth=3, 
                                           linestyle='--', alpha=0.7, label='Loop Closures ({})'.format(actual_connections_drawn))
                        
                        # Plot current pose
                        if current_pose:
                            ax.scatter([current_pose[0]], [current_pose[1]], c='blue', s=100, 
                                     marker='o', zorder=10, label='Current Pose')
                        
                        ax.legend()
                        
                        # Restore view state or auto-adjust view
                        if view_manually_set and saved_xlim is not None and saved_ylim is not None:
                            # Restore manually set view
                            ax.set_xlim(saved_xlim)
                            ax.set_ylim(saved_ylim)
                        elif auto_scale and (map_points or keyframes):
                            # Auto-adjust view to fit all data
                            all_x = []
                            all_y = []
                            if map_points:
                                all_x.extend([p['position'][0] for p in map_points])
                                all_y.extend([p['position'][1] for p in map_points])
                            if keyframes:
                                all_x.extend([k['position'][0] for k in keyframes])
                                all_y.extend([k['position'][1] for k in keyframes])
                            
                            if all_x and all_y:
                                margin = max(2.0, (max(all_x) - min(all_x)) * 0.1)
                                new_xlim = (min(all_x) - margin, max(all_x) + margin)
                                new_ylim = (min(all_y) - margin, max(all_y) + margin)
                                ax.set_xlim(new_xlim)
                                ax.set_ylim(new_ylim)
                                # Update saved limits for auto-scale mode
                                if not view_manually_set:
                                    saved_xlim = new_xlim
                                    saved_ylim = new_ylim
                        
                        # Add statistics text
                        auto_scale_status = "ON" if auto_scale else "OFF"
                        view_status = "Manual" if view_manually_set else "Auto"
                        loop_status = "ON" if show_loop_closures else "OFF"
                        stats_info = "Map Points: {}\nKeyframes: {}".format(len(map_points), len(keyframes))
                        # Show actual loop closures from SDK data
                        actual_loop_count = len(loop_closures) if loop_closures else 0
                        if actual_loop_count > 0:
                            # Show both total and successfully drawn connections
                            drawn_count = actual_connections_drawn if 'actual_connections_drawn' in locals() else 0
                            stats_info += "\nLoop Closures: {} (drawn: {})".format(actual_loop_count, drawn_count)
                        if current_pose:
                            stats_info += "\nCurrent Pose: ({:.2f}, {:.2f}, {:.2f})".format(current_pose[0], current_pose[1], current_pose[2])
                        stats_info += "\nAuto-scale: {}".format(auto_scale_status)
                        stats_info += "\nView: {}".format(view_status)
                        stats_info += "\nLoops: {}".format(loop_status)
                        stats_info += "\nLast Update: {}".format(time.strftime('%H:%M:%S'))
                        stats_info += "\nPress 'h' for help"
                        
                        ax.text(0.02, 0.98, stats_info, transform=ax.transAxes, 
                               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                        
                        # Refresh the display
                        plt.draw()
                        plt.pause(0.01)  # Small pause to allow GUI to update
                        
                        last_update_time = current_time
                        print("Updated: {} points, {} keyframes".format(len(map_points), len(keyframes)))
                        
                    #except Exception as e:
                    #    print("Update error: {}".format(e))
                
                # Check if window is still open
                if not plt.fignum_exists(fig.number):
                    print("Window closed by user")
                    break
                
                # Small sleep to prevent excessive CPU usage
                plt.pause(0.1)
            
        except KeyboardInterrupt:
            print("\nCtrl+C pressed, exiting...")
        except Exception as e:
            print("Error in interactive mode: {}".format(e))
            import traceback
            traceback.print_exc()
            return 1
        finally:
            plt.ioff()  # Turn off interactive mode
            if sdk:
                try:
                    sdk.enable_map_data_syncing(False)
                    sdk.disconnect()
                    sdk.release()
                except:
                    pass
        
        return 0
    
    def _run_headless(self, connection_string=None):
        """Run in headless mode, saving images periodically."""
        print("\nRunning in headless mode - will save images instead of displaying.")
        
        # Setup matplotlib for headless operation
        matplotlib.use('Agg')
        
        # Use simplified approach without threading to avoid crashes
        sdk = None
        
        try:
            # Direct SDK connection (no threading)
            print("Connecting to Aurora device...")
            sdk = AuroraSDK()
            # Session created automatically
            
            # Connect to device (with discovery if no connection string provided)
            if connection_string:
                print("Connecting to device at: {}".format(connection_string))
                sdk.connect(connection_string=connection_string)
            else:
                print("Discovering Aurora devices...")
                devices = sdk.discover_devices(timeout=5.0)
                
                if not devices:
                    print("No Aurora devices found!")
                    return 1
                
                print("Found {} Aurora device(s)".format(len(devices)))
                print("Connecting to first device...")
                sdk.connect(device_info=devices[0])
            
            print("✓ Connected!")
            
            # Enable map data syncing
            print("Enabling map data syncing...")
            sdk.enable_map_data_syncing(True)
            print("✓ Map data syncing enabled")
            
            print("Collecting data and saving visualizations every 10 seconds...")
            print("Press Ctrl+C to exit")
            
            save_counter = 0
            last_save_time = 0
            
            while self.running:
                current_time = time.time()
                
                # Get fresh data
                try:
                    map_data = sdk.get_map_data()
                    if map_data:
                        map_points = map_data.get('map_points', [])
                        keyframes = map_data.get('keyframes', [])
                        loop_closures = map_data.get('loop_closures', [])
                    else:
                        map_points, keyframes, loop_closures = [], [], []
                    
                    try:
                        position, rotation, timestamp = sdk.get_current_pose(use_se3=True)
                        current_pose = position + rotation
                    except DataNotReadyError:
                        current_pose = None
                        
                    # Update data
                    self.update_data(map_points, keyframes, current_pose, loop_closures)
                    
                except Exception as e:
                    print("Data access error: {}".format(e))
                
                # Save image every 10 seconds
                if current_time - last_save_time > 10.0:
                    try:
                        self.setup_matplotlib()  # Create fresh figure
                        self.animate_frame(0)   # Update visualization
                        
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = "aurora_map_headless_{:03d}_{}.png".format(save_counter, timestamp)
                        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
                        print("Saved: {} ({} points, {} keyframes)".format(filename, len(self.map_points), len(self.keyframes)))
                        save_counter += 1
                        last_save_time = current_time
                        
                        plt.close(self.fig)  # Clean up
                    except Exception as e:
                        print("Save error: {}".format(e))
                
                time.sleep(1)  # Update every second
                
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print("Headless mode error: {}".format(e))
        finally:
            self.running = False
            
            # Save final image
            if save_counter == 0:  # Save at least one image
                try:
                    self.setup_matplotlib()
                    self.animate_frame(0)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = "aurora_map_final_{}.png".format(timestamp)
                    self.fig.savefig(filename, dpi=150, bbox_inches='tight')
                    print("Final image saved: {}".format(filename))
                    plt.close(self.fig)
                except Exception as e:
                    print("Final save error: {}".format(e))
            
            # Cleanup SDK
            if sdk:
                try:
                    sdk.enable_map_data_syncing(False)
                    sdk.disconnect()
                    sdk.release()
                except:
                    pass
        
        return 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Vector Map Render Demo - Advanced matplotlib visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python vector_map_render.py                    # Auto-discover and connect
    python vector_map_render.py 192.168.1.212     # Connect to specific IP
    python vector_map_render.py --3d               # Enable 3D visualization

Features:
    - Interactive matplotlib interface with pan/zoom
    - Vector-based rendering for publication-quality output
    - Real-time map data updates and pose tracking
    - Export to PNG, PDF formats
    - Advanced trajectory analysis
    - Optional 3D visualization mode

This demo visualizes VSLAM map data with:
    - Map points (green scatter plot)
    - Keyframe trajectory (red line)
    - Pose history (blue line)
    - Current pose (red marker)
    - Real-time statistics display
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    parser.add_argument(
        '--3d', action='store_true',
        help='Enable 3D visualization mode'
    )
    parser.add_argument(
        '--max-history', type=int, default=1000,
        help='Maximum number of pose history points to keep (default: 1000)'
    )
    
    args = parser.parse_args()
    
    renderer = VectorMapRenderer(enable_3d=args.__dict__['3d'], max_history=args.max_history)
    return renderer.run(args.connection_string)


if __name__ == "__main__":
    sys.exit(main())