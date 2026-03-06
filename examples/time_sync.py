#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/time_sync.py
#  *
#  */
"""
Time synchronization example for Aurora SDK 2.1.1.

Usage:
    python time_sync.py
    python time_sync.py steady 192.168.11.1
    python time_sync.py wallclock 192.168.11.1 --port 9527
"""

import argparse
import sys
import time

from _demo_common import connect_sdk, extract_server_address, load_sdk_module

sdk_module = load_sdk_module()


def wait_for_sync(client, timeout_s=15.0):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if client.is_synchronized():
            return
        time.sleep(0.2)
    raise RuntimeError("Time synchronization did not converge within {:.1f} seconds".format(timeout_s))


def resolve_server_address(device):
    if device:
        return device

    with sdk_module.AuroraSDK() as sdk:
        devices = sdk.discover_devices(timeout=5.0)
        if not devices:
            raise RuntimeError("No Aurora devices found")
        address = extract_server_address(devices[0])
        if not address:
            raise RuntimeError("Failed to resolve a server address from discovery")
        return address


def run_steady(device, port):
    with sdk_module.AuroraSDK() as sdk:
        server_address, _ = connect_sdk(sdk, device=device)
        if not server_address:
            raise RuntimeError("Failed to resolve server address for time sync")

        client = sdk_module.TimeSyncClient(sdk_module.TIMESYNC_DOMAIN_STEADY_CLOCK)
        try:
            client.connect(server_address, port)
            options = sdk_module.TimeSyncClient.get_default_options()
            client.set_options(options)
            client.initialize()
            wait_for_sync(client)
            quality = client.get_quality()
            print("Steady-clock sync quality:", quality.as_dict())

            position, rotation, pose_timestamp = sdk.data_provider.get_current_pose(use_se3=True)
            translated_pose_timestamp = client.translate_timestamp(pose_timestamp)
            print(
                "Pose timestamp {} ns -> {} ns".format(pose_timestamp, translated_pose_timestamp)
            )
            print("Pose position={}, rotation={}".format(position, rotation))

            imu_samples = sdk.data_provider.peek_imu_data()
            if imu_samples:
                imu_timestamp = imu_samples[-1].timestamp_ns
                translated_imu_timestamp = client.translate_timestamp(imu_timestamp)
                print("Latest IMU timestamp {} ns -> {} ns".format(imu_timestamp, translated_imu_timestamp))
            else:
                print("No IMU samples available yet")
        finally:
            client.close()


def run_wallclock(device, port):
    server_address = resolve_server_address(device)
    client = sdk_module.TimeSyncClient(sdk_module.TIMESYNC_DOMAIN_WALL_CLOCK)
    try:
        client.connect(server_address, port)
        client.set_options(sdk_module.TimeSyncClient.get_default_options())
        client.initialize()
        wait_for_sync(client)
        offset = client.get_wallclock_offset()
        print(
            "Wall clock offset: success={} offset_ns={} rtt_ns={:.0f}".format(
                bool(offset.success), int(offset.offset_ns), float(offset.rtt_ns)
            )
        )

        if abs(int(offset.offset_ns)) > 1_000_000:
            sync_result = client.sync_server_wallclock()
            print(
                "Wall clock sync: success={} applied_offset_ns={} server_utc_ns={}".format(
                    bool(sync_result.success), int(sync_result.applied_offset_ns), int(sync_result.server_utc_ns)
                )
            )

        accuracy = client.evaluate_wallclock_accuracy()
        print(
            "Wall clock accuracy: success={} offset_error_ns={} rtt_ns={:.0f}".format(
                bool(accuracy.success), int(accuracy.offset_error_ns), float(accuracy.rtt_ns)
            )
        )
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Aurora time synchronization example")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("steady", "wallclock", "all"),
        default="all",
        help="Which demo to run",
    )
    parser.add_argument(
        "connection_string",
        nargs="?",
        help="Aurora device address, for example 192.168.11.1",
    )
    parser.add_argument("--port", type=int, default=sdk_module.TIMESYNC_DEFAULT_PORT)
    args = parser.parse_args()

    if args.command in ("steady", "all"):
        run_steady(args.connection_string, args.port)

    if args.command in ("wallclock", "all"):
        run_wallclock(args.connection_string, args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
