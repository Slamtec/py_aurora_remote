#!/usr/bin/env python3
"""
Selective Map Data Fetch Example

This example demonstrates selective map data fetching with the enhanced get_map_data interface.
It shows how to use the new parameters to fetch only specific parts of map data,
which can significantly improve performance when you don't need all data types.

Usage:
    python selective_map_data_fetch.py [connection_string] [options]
    
Example:
    python selective_map_data_fetch.py 192.168.1.212 --fetch-kf --fetch-mp
"""

import sys
import time
import argparse

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.
    
    Returns:
        tuple: (AuroraSDK, wait_for_map_data)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.utils import wait_for_map_data
        return AuroraSDK, wait_for_map_data
    except ImportError:
        # Fall back to source code in parent directory
        import os
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import AuroraSDK
        from slamtec_aurora_sdk.utils import wait_for_map_data
        return AuroraSDK, wait_for_map_data

# Setup SDK import
AuroraSDK, wait_for_map_data = setup_sdk_import()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Selective Map Data Fetch Demo - Demonstrate selective fetching of map data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python selective_map_data_fetch.py                           # Auto-discover, fetch all data
    python selective_map_data_fetch.py 192.168.1.212            # Connect to specific IP
    python selective_map_data_fetch.py --fetch-kf               # Fetch only keyframes
    python selective_map_data_fetch.py --fetch-mp               # Fetch only map points
    python selective_map_data_fetch.py --fetch-mapinfo          # Fetch only map info
    python selective_map_data_fetch.py --fetch-kf --fetch-mp    # Fetch keyframes and map points
    python selective_map_data_fetch.py --all-maps               # Fetch from all maps

This demo shows how to selectively fetch map data components:
    - Keyframes only (trajectory data)
    - Map points only (3D point cloud)
    - Map info only (metadata without actual data)
    - Any combination of the above
        """
    )
    parser.add_argument(
        'connection_string',
        nargs='?',
        help='Aurora device connection string (e.g., 192.168.1.212)'
    )
    parser.add_argument('--fetch-kf', action='store_true', default=False, 
                       help='Fetch keyframes')
    parser.add_argument('--fetch-mp', action='store_true', default=False,
                       help='Fetch map points')
    parser.add_argument('--fetch-mapinfo', action='store_true', default=False,
                       help='Fetch map info')
    parser.add_argument('--all-maps', action='store_true', default=False,
                       help='Fetch from all maps instead of just active map')
    args = parser.parse_args()
    
    # If no specific fetch flags are set, fetch everything except map info (default behavior)
    if not (args.fetch_kf or args.fetch_mp or args.fetch_mapinfo):
        args.fetch_kf = True
        args.fetch_mp = True
    
    sdk = AuroraSDK()
    
    try:
        # Connect to device
        print("Connecting to Aurora device...")
        if args.connection_string:
            sdk.connect(connection_string=args.connection_string)
            print(f"Connected to {args.connection_string}")
        else:
            # Auto-discover and connect with retry logic
            max_discovery_attempts = 3
            devices = []
            
            for attempt in range(max_discovery_attempts):
                print(f"Discovering Aurora devices... (attempt {attempt + 1}/{max_discovery_attempts})")
                devices = sdk.discover_devices(timeout=5.0)
                
                if devices:
                    print(f"Found {len(devices)} device(s)")
                    break
                    
                if attempt < max_discovery_attempts - 1:
                    print("No devices found, retrying...")
                    time.sleep(2)
            
            if not devices:
                print("No Aurora devices found after multiple attempts")
                return 1
            
            # Connect to first device
            print(f"Connecting to first device: {devices[0]['device_name']}...")
            sdk.connect(device_info=devices[0])
            print(f"Connected successfully!")
        
        # Enable map data syncing
        print("\nEnabling map data syncing...")
        sdk.controller.enable_map_data_syncing(True)
        
        # Wait for map data to be available using wait_for_map_data
        print("Waiting for map data to sync...")
        try:
            sync_status = wait_for_map_data(
                sdk.data_provider,
                min_keyframes=10,
                min_sync_ratio=0.8,
                max_wait_time=30.0,
                progress_callback=lambda elapsed, status: print(
                    f"  {elapsed:.1f}s: Sync {status['sync_ratio']*100:.0f}% "
                    f"({status['total_kf_count_fetched']}/{status['total_kf_count']} keyframes)"
                )
            )
            print(f"\nMap data synced successfully!")
        except Exception as e:
            print(f"Warning: {e}")
            print("Proceeding with available data...")
        
        # Determine which maps to fetch
        map_ids = [] if args.all_maps else None
        
        print(f"\nFetching map data with parameters:")
        print(f"  - Keyframes: {args.fetch_kf}")
        print(f"  - Map points: {args.fetch_mp}")
        print(f"  - Map info: {args.fetch_mapinfo}")
        print(f"  - Map selection: {'All maps' if args.all_maps else 'Active map only'}")
        
        # Measure fetch time
        start_time = time.time()
        
        # Fetch map data with selective parameters
        data = sdk.get_map_data(
            map_ids=map_ids,
            fetch_kf=args.fetch_kf,
            fetch_mp=args.fetch_mp,
            fetch_mapinfo=args.fetch_mapinfo
        )
        
        fetch_time = time.time() - start_time
        
        print(f"\nFetch completed in {fetch_time:.3f} seconds")
        print(f"\nResults:")
        print(f"  - Keyframes fetched: {len(data['keyframes'])}")
        print(f"  - Map points fetched: {len(data['map_points'])}")
        print(f"  - Loop closures: {len(data['loop_closures'])}")
        print(f"  - Map info entries: {len(data['map_info'])}")
        
        # Display map info if fetched
        if data['map_info']:
            print("\nMap Information:")
            for map_id, info in data['map_info'].items():
                print(f"  Map {map_id}:")
                print(f"    - Keyframes: {info['keyframe_count']}")
                print(f"    - Map points: {info['point_count']}")
                print(f"    - Map flags: {info['map_flags']}")
                print(f"    - Keyframe ID range: {info['keyframe_id_start']} - {info['keyframe_id_end']}")
                print(f"    - Map point ID range: {info['map_point_id_start']} - {info['map_point_id_end']}")
        
        # Display sample data if available
        if data['keyframes'] and len(data['keyframes']) > 0:
            print(f"\nSample keyframe data (first keyframe):")
            kf = data['keyframes'][0]
            print(f"  - ID: {kf['id']}")
            print(f"  - Map ID: {kf['map_id']}")
            print(f"  - Position: ({kf['position'][0]:.3f}, {kf['position'][1]:.3f}, {kf['position'][2]:.3f})")
            print(f"  - Fixed: {kf['fixed']}")
        
        if data['map_points'] and len(data['map_points']) > 0:
            print(f"\nSample map point data (first 5 points):")
            for i, mp in enumerate(data['map_points'][:5]):
                print(f"  Point {i}: pos=({mp['position'][0]:.3f}, {mp['position'][1]:.3f}, {mp['position'][2]:.3f}), id={mp['id']}")
        
        # Demonstrate performance comparison
        print("\n--- Performance Comparison ---")
        
        # Fetch everything
        start_time = time.time()
        full_data = sdk.get_map_data(fetch_kf=True, fetch_mp=True, fetch_mapinfo=True)
        full_fetch_time = time.time() - start_time
        
        # Fetch only keyframes
        start_time = time.time()
        kf_only_data = sdk.get_map_data(fetch_kf=True, fetch_mp=False, fetch_mapinfo=False)
        kf_only_time = time.time() - start_time
        
        print(f"Full data fetch: {full_fetch_time:.3f}s")
        print(f"Keyframes only: {kf_only_time:.3f}s (speedup: {full_fetch_time/kf_only_time:.1f}x)")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        print("\nDisconnecting...")
        if sdk:
            sdk.disconnect()
            sdk.release()

if __name__ == "__main__":
    sys.exit(main())