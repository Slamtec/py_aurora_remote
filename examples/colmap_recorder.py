#!/usr/bin/env python3
"""
COLMAP Dataset Recorder Example

This example demonstrates how to use the DataRecorder to record COLMAP-compatible
datasets from an Aurora device. It's the Python equivalent of the colmap_recorder C++ demo.

The recorded dataset can be used with COLMAP for 3D reconstruction and structure-from-motion.

Usage:
    python colmap_recorder.py --output <folder> [OPTIONS]

Required Arguments:
    --output <folder>       Folder path to store the recorded dataset

Optional Arguments:
    --device <ip>           Device IP address (auto-discover if not specified)
    --timeout <seconds>     Timeout in seconds (0 = no timeout, default)

Common Options:
    --image-quality <type>  Image stream type: preview (default), raw

COLMAP Recorder Options:
    --stereo-recording      Enable stereo image recording (default: False)
    --undistort             Enable image undistortion (default: True)
    --no-undistort          Disable image undistortion
    --force-focal-center    Force focal center to image center (default: True)
    --no-force-focal-center Do not force focal center to image center
    --keep-unused-points    Keep unused map points (default: False)
    --multi-mapper          Store data in sparse/n/ folder (default: False)
    --file-format <format>  Output format: binary (default), text, all

Example:
    python colmap_recorder.py --output /data/colmap_dataset_001 --stereo-recording --image-quality raw
    python colmap_recorder.py --output /data/colmap_dataset_002 --device 192.168.1.212 --timeout 60
"""

import sys
import time
import argparse
import signal
import os

def setup_sdk_import():
    """
    Import the Aurora SDK, trying installed package first, then falling back to source.

    Returns:
        tuple: (AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, DATARECORDER_TYPE_COLMAP_DATASET)
    """
    try:
        # Try to import from installed package first
        from slamtec_aurora_sdk import (
            AuroraSDK,
            AuroraSDKError,
            ConnectionError,
            DataNotReadyError,
            DATARECORDER_TYPE_COLMAP_DATASET
        )
        return AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, DATARECORDER_TYPE_COLMAP_DATASET
    except ImportError:
        # Fall back to source code in parent directory
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python_bindings'))
        from slamtec_aurora_sdk import (
            AuroraSDK,
            AuroraSDKError,
            ConnectionError,
            DataNotReadyError,
            DATARECORDER_TYPE_COLMAP_DATASET
        )
        return AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, DATARECORDER_TYPE_COLMAP_DATASET

# Setup SDK import
AuroraSDK, AuroraSDKError, ConnectionError, DataNotReadyError, DATARECORDER_TYPE_COLMAP_DATASET = setup_sdk_import()


class ColmapRecorderDemo:
    """COLMAP dataset recorder demonstration class."""

    def __init__(self):
        self.sdk = None
        self.running = True

        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C signal for graceful exit."""
        print("\nCtrl-C pressed, stopping recording...")
        self.running = False

    def run(self, args):
        """
        Run the COLMAP recorder demo.

        Args:
            args: Parsed command-line arguments
        """
        try:
            # Print recording configuration
            print("\nDataset will be stored in:", args.output)
            print("\nRecording options:")
            print(f"  Image quality: {args.image_quality}", end="")
            if args.image_quality == "preview":
                print(" (WARNING: Preview image will reduce image quality)")
            else:
                print()
            print(f"  Stereo recording: {'enabled' if args.stereo_recording else 'disabled'}")
            print(f"  Undistort images: {'enabled' if args.undistort else 'disabled'}")
            print(f"  Force focal center: {'enabled' if args.force_focal_center else 'disabled'}")
            print(f"  Keep unused map points: {'enabled' if args.keep_unused_points else 'disabled'}")
            print(f"  Multi-mapper: {'enabled' if args.multi_mapper else 'disabled'}")
            print(f"  File format: {args.file_format}")
            print()

            # Create SDK instance
            print("Creating Aurora SDK instance...")
            self.sdk = AuroraSDK()

            # Print version info
            version_info = self.sdk.get_version_info()
            print(f"Aurora SDK Version: {version_info['version_string']}")

            # Connect to device
            if args.device:
                print(f"Connecting to device at: {args.device}")
                self.sdk.controller.connect(connection_string=args.device)
            else:
                print("Device connection string not provided, discovering Aurora devices...")
                print("Waiting for Aurora devices...")
                time.sleep(5)

                devices = self.sdk.discover_devices()
                if not devices:
                    print("No Aurora devices found")
                    return 1

                print(f"Found {len(devices)} Aurora device(s)")
                for i, device in enumerate(devices):
                    print(f"Device {i}: {device}")

                # Select first device
                print("Selected first device")
                self.sdk.connect(device_info=devices[0])

            print("Connected to device")

            # Enable background map data syncing (required for COLMAP recording)
            print("Starting background map data syncing...")
            self.sdk.controller.enable_map_data_syncing(True)

            # Configure recorder options before starting recording
            print("Configuring recording options...")

            # Common options
            try:
                self.sdk.data_recorder.set_option_string(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "image_quality",
                    args.image_quality
                )
            except Exception as e:
                print(f"Warning: Failed to set image_quality option: {e}")

            # COLMAP specific options
            try:
                self.sdk.data_recorder.set_option_bool(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "stereo_recording",
                    args.stereo_recording
                )
            except Exception as e:
                print(f"Warning: Failed to set stereo_recording option: {e}")

            try:
                self.sdk.data_recorder.set_option_bool(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "undistort",
                    args.undistort
                )
            except Exception as e:
                print(f"Warning: Failed to set undistort option: {e}")

            try:
                self.sdk.data_recorder.set_option_bool(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "undistort_force_focal_center",
                    args.force_focal_center
                )
            except Exception as e:
                print(f"Warning: Failed to set undistort_force_focal_center option: {e}")

            try:
                self.sdk.data_recorder.set_option_bool(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "keep_unused_map_points",
                    args.keep_unused_points
                )
            except Exception as e:
                print(f"Warning: Failed to set keep_unused_map_points option: {e}")

            try:
                self.sdk.data_recorder.set_option_bool(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "multi_mapper",
                    args.multi_mapper
                )
            except Exception as e:
                print(f"Warning: Failed to set multi_mapper option: {e}")

            try:
                self.sdk.data_recorder.set_option_string(
                    DATARECORDER_TYPE_COLMAP_DATASET,
                    "file_format",
                    args.file_format
                )
            except Exception as e:
                print(f"Warning: Failed to set file_format option: {e}")

            # Start recording
            print("Starting COLMAP dataset recording...")
            self.sdk.data_recorder.start_recording(
                DATARECORDER_TYPE_COLMAP_DATASET,
                args.output
            )

            # Check if recording is actually running
            if not self.sdk.data_recorder.is_recording(DATARECORDER_TYPE_COLMAP_DATASET):
                print("Recording failed to start properly")
                self.sdk.controller.stop_background_map_data_syncing()
                return 1

            print("Recording started successfully")
            if args.timeout > 0:
                print(f"Recording will stop automatically after {args.timeout} seconds")
            print("Press Ctrl+C to stop recording")

            # Recording loop
            start_time = time.time()
            last_kf_count = 0

            while self.running and self.sdk.data_recorder.is_recording(DATARECORDER_TYPE_COLMAP_DATASET):
                # Check timeout
                if args.timeout > 0:
                    elapsed = time.time() - start_time
                    if elapsed >= args.timeout:
                        print(f"Timeout reached, stopping recording...")
                        break

                # Query and print current status (keyframe count)
                try:
                    kf_count = self.sdk.data_recorder.query_status_int(
                        DATARECORDER_TYPE_COLMAP_DATASET,
                        "kf_count"
                    )
                    if kf_count != last_kf_count:
                        print(f"Current keyframe count: {kf_count}")
                        last_kf_count = kf_count
                except Exception as e:
                    # Status query may fail if not available yet
                    pass

                time.sleep(1)

            # Stop recording
            print("Stopping recording...")
            self.sdk.data_recorder.stop_recording(DATARECORDER_TYPE_COLMAP_DATASET)

            print("Recording stopped successfully")

            # Cleanup
            self.sdk.controller.disconnect()

            print(f"Dataset saved to: {args.output}")
            return 0

        except KeyboardInterrupt:
            print("\nInterrupted by user")
            return 1
        except ConnectionError as e:
            print(f"Connection error: {e}")
            return 1
        except AuroraSDKError as e:
            print(f"Aurora SDK error: {e}")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            if self.sdk:
                # Ensure cleanup happens
                try:
                    if self.sdk.controller.is_connected():
                        self.sdk.controller.disconnect()
                except:
                    pass


def main():
    parser = argparse.ArgumentParser(
        description="Record COLMAP-compatible dataset from Aurora device",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Required arguments
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Folder path to store the recorded dataset"
    )

    # Optional arguments
    parser.add_argument(
        "--device",
        type=str,
        help="Device IP address (auto-discover if not specified)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Timeout in seconds (0 = no timeout, default)"
    )

    # Common options
    parser.add_argument(
        "--image-quality",
        type=str,
        choices=["raw", "preview"],
        default="preview",
        help="Image stream type: preview (default), raw"
    )

    # COLMAP recorder options
    parser.add_argument(
        "--stereo-recording",
        action="store_true",
        help="Enable stereo image recording (default: False)"
    )

    parser.add_argument(
        "--undistort",
        action="store_true",
        default=True,
        help="Enable image undistortion (default: True)"
    )

    parser.add_argument(
        "--no-undistort",
        action="store_false",
        dest="undistort",
        help="Disable image undistortion"
    )

    parser.add_argument(
        "--force-focal-center",
        action="store_true",
        default=True,
        help="Force focal center to image center (default: True)"
    )

    parser.add_argument(
        "--no-force-focal-center",
        action="store_false",
        dest="force_focal_center",
        help="Do not force focal center to image center"
    )

    parser.add_argument(
        "--keep-unused-points",
        action="store_true",
        help="Keep unused map points (default: False)"
    )

    parser.add_argument(
        "--multi-mapper",
        action="store_true",
        help="Store data in sparse/n/ folder (default: False)"
    )

    parser.add_argument(
        "--file-format",
        type=str,
        choices=["binary", "text", "all"],
        default="binary",
        help="Output format: binary (default), text, all"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.timeout < 0:
        print("Error: --timeout must be >= 0")
        return 1

    # Run demo
    demo = ColmapRecorderDemo()
    return demo.run(args)


if __name__ == "__main__":
    sys.exit(main())
