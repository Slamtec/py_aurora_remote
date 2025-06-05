#!/usr/bin/env python3

"""
LiDAR 2D Map Save Demo

This demo builds a 2D occupancy grid map using proper on-demand map building
via slamtec_aurora_sdk_lidar2dmap_generate_fullmap and saves it to an external 
image file. Users can specify cell resolution and map size parameters.

Key differences from lidar_2dmap_render:
- Uses slamtec_aurora_sdk_lidar2dmap_generate_fullmap (true on-demand) 
- Not start_preview_map_background_update (background/preview mode)
- Checks map sync status before generation
- No build time parameter needed (generates instantly when data is ready)
- Focused on map generation and saving rather than real-time visualization
"""

import sys
import os
import time
import argparse
import numpy as np
from PIL import Image

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, GridMapGenerationOptions, Rect, get_map_sync_status, wait_for_map_data, format_map_sync_status)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.data_types import GridMapGenerationOptions, Rect
        from slamtec_aurora_sdk.utils import get_map_sync_status, wait_for_map_data, format_map_sync_status
        return AuroraSDK, GridMapGenerationOptions, Rect, get_map_sync_status, wait_for_map_data, format_map_sync_status
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.data_types import GridMapGenerationOptions, Rect
        from slamtec_aurora_sdk.utils import get_map_sync_status, wait_for_map_data, format_map_sync_status
        return AuroraSDK, GridMapGenerationOptions, Rect, get_map_sync_status, wait_for_map_data, format_map_sync_status

# Setup SDK import
AuroraSDK, GridMapGenerationOptions, Rect, get_map_sync_status, wait_for_map_data, format_map_sync_status = setup_sdk_import()


class LiDAR2DMapSaver:
    def __init__(self, device_address, resolution=0.05, map_width=200.0, map_height=200.0, 
                 height_min=-0.5, height_max=2.0, active_map_only=True, l2p_mapping=True):
        """
        Initialize LiDAR 2D Map Saver for on-demand map generation.
        
        Uses slamtec_aurora_sdk_lidar2dmap_generate_fullmap for proper on-demand
        map building (not preview/background mode).
        
        Args:
            device_address: Aurora device IP address
            resolution: Cell resolution in meters (default: 0.05m = 5cm)
            map_width: Map canvas width in meters (default: 200m)
            map_height: Map canvas height in meters (default: 200m)
            height_min: Minimum height filter in meters (default: -0.5m)
            height_max: Maximum height filter in meters (default: 2.0m)
            active_map_only: Use only active map area (default: True)
            l2p_mapping: Use log-odd to linear mapping for visualization (default: True)
        """
        self.device_address = device_address
        self.resolution = resolution
        self.map_width = map_width
        self.map_height = map_height
        self.height_min = height_min
        self.height_max = height_max
        self.active_map_only = active_map_only
        self.l2p_mapping = l2p_mapping
        
        # Initialize SDK
        self.sdk = AuroraSDK()
        
        
        print("Connecting to Aurora device at {}...".format(device_address))
        self.sdk.connect(connection_string=device_address)
        print("Connected successfully!")
        
        # Configure 2D map generation options
        self.setup_map_generation()
        
    def setup_map_generation(self):
        """Configure and check map data syncing for on-demand generation."""
        print("Configuring on-demand 2D map generation...")
        print("  Resolution: {:.3f}m ({:.1f}cm)".format(self.resolution, self.resolution * 100))
        print("  Map size: {:.1f}m x {:.1f}m".format(self.map_width, self.map_height))
        print("  Height range: {:.1f}m to {:.1f}m".format(self.height_min, self.height_max))
        print("  Active map only: {}".format(self.active_map_only))
        print("  L2P mapping: {}".format("enabled" if self.l2p_mapping else "disabled (raw log-odd)"))
        
        # Enable map data syncing FIRST (required before on-demand generation)
        print("Enabling map data syncing...")
        self.sdk.enable_map_data_syncing(True)
        
        # Create generation options for later use
        self.options = GridMapGenerationOptions()
        self.options.resolution = self.resolution
        self.options.map_canvas_width = self.map_width
        self.options.map_canvas_height = self.map_height
        self.options.active_map_only = 1 if self.active_map_only else 0
        self.options.height_range_specified = 1
        self.options.min_height = self.height_min
        self.options.max_height = self.height_max
        
        print("✓ Map data syncing enabled, ready for on-demand generation")
        
    def build_and_save_map(self, output_filename, max_wait_time=30.0):
        """
        Build the 2D map on-demand and save to image file.
        
        Args:
            output_filename: Output image filename (e.g., "map.png")
            max_wait_time: Maximum time to wait for map data (default: 30s)
        """
        print("\nWaiting for sufficient map data...")
        
        # Use utility function to wait for map data with progress reporting
        def progress_callback(elapsed, sync_status):
            if elapsed % 5.0 < 0.5:  # Print every 5 seconds
                status_str = format_map_sync_status(sync_status, verbose=True)
                print("  {} - {:.1f}s elapsed".format(status_str, elapsed))
        
        try:
            sync_status = wait_for_map_data(
                self.sdk.data_provider,
                min_keyframes=10,
                min_sync_ratio=0.8,
                max_wait_time=max_wait_time,
                progress_callback=progress_callback
            )
            
            if sync_status['is_sufficient']:
                print("  ✓ Sufficient map data available ({} keyframes, {:.1f}% synced)".format(
                    sync_status['total_kf_count'], sync_status['sync_ratio']*100))
            else:
                print("  Warning: Using available data ({} keyframes, {:.1f}% synced)".format(
                    sync_status['total_kf_count'], sync_status['sync_ratio']*100))
                
        except Exception as e:
            print("  Error: {}".format(e))
            return False
        
        print("\nGenerating full 2D map on-demand...")
        print("  Using slamtec_aurora_sdk_lidar2dmap_generate_fullmap interface")
        
        # Generate the full map using the proper on-demand interface
        try:
            generated_map = self.sdk.lidar_2d_map_builder.generate_fullmap_ondemand(
                self.options,
                wait_for_data_sync=True,
                timeout_ms=60000  # 60 second timeout
            )
            print("  ✓ Map generation completed successfully!")
            
        except Exception as e:
            print("  Error: Failed to generate map - {}".format(e))
            return False
        
        # Get the map data from the generated map
        map_data = self.get_map_data_from_generated_map(generated_map)
        
        if map_data is None:
            print("Error: Failed to retrieve generated map data")
            return False
        
        # Save map to image file
        success = self.save_map_image(map_data, output_filename)
        
        if success:
            print("Map saved successfully to: {}".format(output_filename))
            self.print_map_statistics(map_data)
        else:
            print("Error: Failed to save map image")
            
        return success
    
    def get_map_data_from_generated_map(self, generated_map):
        """Retrieve map data from the generated on-demand map."""
        try:
            # Get map dimension from the generated map
            dimension = generated_map.get_map_dimension()
            
            print("Generated map dimensions: {:.1f}m x {:.1f}m".format(
                dimension.max_x - dimension.min_x, dimension.max_y - dimension.min_y))
            
            # Fetch the FULL map extent
            fetch_rect = Rect()
            fetch_rect.x = dimension.min_x
            fetch_rect.y = dimension.min_y
            fetch_rect.width = dimension.max_x - dimension.min_x
            fetch_rect.height = dimension.max_y - dimension.min_y
            
            # Fetch map cell data from the generated map with l2p mapping control
            cell_data, fetch_info = generated_map.read_cell_data(
                fetch_rect, 
                resolution=self.resolution,
                l2p_mapping=self.l2p_mapping
            )
            
            if not cell_data:
                print("Warning: No map cell data available from generated map")
                return None
            
            return {
                'dimension': dimension,
                'fetch_info': fetch_info,
                'cell_data': cell_data,
                'fetch_rect': fetch_rect
            }
            
        except Exception as e:
            print("Error retrieving generated map data: {}".format(e))
            return None
    
    def save_map_image(self, map_data, output_filename):
        """
        Convert map data to image and save to file.
        
        Args:
            map_data: Map data dictionary from get_map_data()
            output_filename: Output image filename
        """
        try:
            fetch_info = map_data['fetch_info']
            cell_data = map_data['cell_data']
            
            # Reshape cell data to 2D grid
            grid = np.array(cell_data).reshape(fetch_info.cell_height, fetch_info.cell_width)
            
            # Convert to image format (0-255)
            # Both l2p and raw data are returned as uint8 by the SDK
            grid_uint8 = np.array(cell_data, dtype=np.uint8).reshape(fetch_info.cell_height, fetch_info.cell_width)
         
            
            # Create PIL image (flip vertically for correct orientation)
            image = Image.fromarray(np.flipud(grid_uint8), mode='L')
            
            # Save image
            image.save(output_filename)
            
            return True
            
        except Exception as e:
            print("Error saving map image: {}".format(e))
            return False
    
    def print_map_statistics(self, map_data):
        """Print detailed map statistics."""
        fetch_info = map_data['fetch_info']
        cell_data = map_data['cell_data']
        dimension = map_data['dimension']
        
        # Calculate statistics (both l2p and raw data are uint8)
        total_cells = len(cell_data)
        
        if self.l2p_mapping:
            # Linear mapping: use specific uint8 values
            occupied_cells = sum(1 for x in cell_data if x == 255)  # Occupied = 255
            free_cells = sum(1 for x in cell_data if x == 127)      # Free = 127
            unknown_cells = sum(1 for x in cell_data if x == 0)     # Unknown = 0
        else:
            # Raw log-odd data as uint8: use threshold-based approach
            occupied_cells = sum(1 for x in cell_data if x > 180)   # High values = occupied
            free_cells = sum(1 for x in cell_data if x < 75)        # Low values = free
            unknown_cells = sum(1 for x in cell_data if 75 <= x <= 180)  # Mid values = unknown
        
        map_width = dimension.max_x - dimension.min_x
        map_height = dimension.max_y - dimension.min_y
        
        print("\nMap Statistics:")
        print("  Resolution: {:.3f}m ({:.1f}cm)".format(self.resolution, self.resolution * 100))
        print("  Map size: {:.1f}m x {:.1f}m".format(map_width, map_height))
        print("  Grid size: {} x {} cells".format(fetch_info.cell_width, fetch_info.cell_height))
        print("  Total cells: {:,}".format(total_cells))
        print("  Occupied cells: {:,} ({:.1f}%)".format(occupied_cells, 100.0 * occupied_cells / total_cells))
        print("  Free cells: {:,} ({:.1f}%)".format(free_cells, 100.0 * free_cells / total_cells))
        print("  Unknown cells: {:,} ({:.1f}%)".format(unknown_cells, 100.0 * unknown_cells / total_cells))
    
    def cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        try:
            # Disable map data syncing
            self.sdk.enable_map_data_syncing(False)
            
            # Disconnect from device
            self.sdk.disconnect()
            
        except Exception as e:
            print("Error during cleanup: {}".format(e))


def main():
    parser = argparse.ArgumentParser(description='LiDAR 2D Map Save Demo')
    parser.add_argument('device_ip', help='Aurora device IP address')
    parser.add_argument('-o', '--output', default='lidar_2dmap.png', 
                       help='Output image filename (default: lidar_2dmap.png)')
    parser.add_argument('-r', '--resolution', type=float, default=0.05,
                       help='Cell resolution in meters (default: 0.05)')
    parser.add_argument('-w', '--width', type=float, default=200.0,
                       help='Map canvas width in meters (default: 200.0)')
    parser.add_argument('-h_', '--height', type=float, default=200.0,
                       help='Map canvas height in meters (default: 200.0)')
    parser.add_argument('--height-min', type=float, default=-0.5,
                       help='Minimum height filter in meters (default: -0.5)')
    parser.add_argument('--height-max', type=float, default=2.0,
                       help='Maximum height filter in meters (default: 2.0)')
    parser.add_argument('--all-map', action='store_true',
                       help='Use entire map area instead of active map only')
    parser.add_argument('--no-l2p', action='store_true',
                       help='Disable L2P mapping (use raw log-odd data instead of linear)')
    
    args = parser.parse_args()
    
    # Validate parameters
    if args.resolution <= 0:
        print("Error: Resolution must be positive")
        return 1
    
    if args.width <= 0 or args.height <= 0:
        print("Error: Map dimensions must be positive")
        return 1
    
    
    saver = None
    try:
        # Create map saver
        saver = LiDAR2DMapSaver(
            device_address=args.device_ip,
            resolution=args.resolution,
            map_width=args.width,
            map_height=args.height,
            height_min=args.height_min,
            height_max=args.height_max,
            active_map_only=not args.all_map,
            l2p_mapping=not args.no_l2p  # Default True, disabled with --no-l2p
        )
        
        # Build and save map
        success = saver.build_and_save_map(args.output)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
        
    except Exception as e:
        print("Error: {}".format(e))
        return 1
        
    finally:
        if saver:
            saver.cleanup()


if __name__ == '__main__':
    exit(main())