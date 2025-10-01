#!/usr/bin/env python3

import sys
import os
import time
import json

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, GridMapGenerationOptions, Rect)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.data_types import GridMapGenerationOptions, Rect
        return AuroraSDK, GridMapGenerationOptions, Rect
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.data_types import GridMapGenerationOptions, Rect
        return AuroraSDK, GridMapGenerationOptions, Rect

# Setup SDK import
AuroraSDK, GridMapGenerationOptions, Rect = setup_sdk_import()

def run_snapshot_test(connection_string=None):
    """Run map snapshot test with specified or auto-discovered connection.

    Args:
        connection_string: IP address or connection string. If None, auto-discover.
    """
    print("=== Simple Map Snapshot Test ===")
    print("Using corrected delayed map data syncing")

    try:
        # Setup with corrected approach
        sdk = AuroraSDK()

        # Connect to device
        if connection_string:
            print(f"Connecting to device at {connection_string}...")
            sdk.connect(connection_string=connection_string)
        else:
            print("Discovering devices...")
            devices = sdk.discover_devices(timeout=5.0)
            if not devices:
                print("No devices found!")
                return 1
            print(f"Found device: {devices[0].device_address}")
            sdk.connect(device_info=devices[0])
        print("✓ Connected")

        # Start background syncing
        sdk.controller.start_background_map_data_syncing()
        print("✓ Background syncing started")

        # Start 2D map operations first
        options = GridMapGenerationOptions()
        options.resolution = 0.05
        options.map_canvas_width = 150.0
        options.map_canvas_height = 150.0
        options.active_map_only = 1

        sdk.lidar_2d_map_builder.start_preview_map_background_update(options)
        sdk.lidar_2d_map_builder.set_preview_map_auto_floor_detection(True)
        print("✓ 2D map operations started")

        # Brief pause then enable map data syncing
        time.sleep(2)
        sdk.enable_map_data_syncing(True)
        print("✓ Map data syncing enabled (delayed)")

        # Wait for map to build
        print("\nWaiting 10 seconds for map to build...")
        time.sleep(10)

        # Take ONE snapshot
        print("\nTaking map snapshot...")
        preview_map = sdk.lidar_2d_map_builder.get_preview_map()
        dimension = preview_map.get_map_dimension()

        map_width = dimension.max_x - dimension.min_x
        map_height = dimension.max_y - dimension.min_y

        print(f"Map size: {map_width:.1f}x{map_height:.1f}m")

        # Single cell data read
        fetch_rect = Rect()
        fetch_rect.x = dimension.min_x
        fetch_rect.y = dimension.min_y
        fetch_rect.width = map_width
        fetch_rect.height = map_height

        if fetch_rect.width > 0 and fetch_rect.height > 0:
            cell_data, fetch_info = preview_map.read_cell_data(fetch_rect)

            total_cells = len(cell_data)
            occupied_cells = sum(1 for cell in cell_data if cell != 0)

            snapshot = {
                'timestamp': time.time(),
                'map_size_m': f"{map_width:.1f}x{map_height:.1f}",
                'total_cells': total_cells,
                'occupied_cells': occupied_cells,
                'occupancy_ratio': occupied_cells / total_cells if total_cells > 0 else 0,
                'grid_size': f"{fetch_info.cell_width}x{fetch_info.cell_height}",
                'success': map_width > 50 and map_height > 40,
                'note': 'Single snapshot with corrected delayed map data syncing'
            }

            # Save snapshot
            with open('map_snapshot.json', 'w') as f:
                json.dump(snapshot, f, indent=2)

            print(f"📸 Snapshot saved:")
            print(f"   Map: {map_width:.1f}x{map_height:.1f}m")
            print(f"   Cells: {total_cells} total, {occupied_cells} occupied")
            print(f"   Grid: {fetch_info.cell_width}x{fetch_info.cell_height}")

            if map_width > 50 and map_height > 40:
                print("🎯 SUCCESS: Map size matches expected dimensions!")
            else:
                print("📐 Map size is not as expected")

            if occupied_cells > 0:
                print(f"🎉 Found {occupied_cells} occupied cells!")
            else:
                print("⚠ No occupied cells (may need device movement)")

        else:
            print("❌ Invalid map dimensions")

        print("\n✓ Test completed successfully without crash")
        return 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        try:
            sdk.disconnect()
            print("✓ Disconnected")
        except:
            pass

if __name__ == "__main__":
    # Get connection string from command line argument
    connection_string = sys.argv[1] if len(sys.argv) > 1 else None

    if connection_string:
        print(f"Using specified connection: {connection_string}")
    else:
        print("No connection specified, will auto-discover device")

    sys.exit(run_snapshot_test(connection_string))