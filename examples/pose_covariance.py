#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/pose_covariance.py
#  *
#  */
"""
Pose covariance example for Aurora SDK 2.1.1.

Usage:
    python pose_covariance.py
    python pose_covariance.py 192.168.11.1
"""

import argparse
import signal
import sys
import time

from _demo_common import connect_sdk, load_sdk_module

sdk_module = load_sdk_module()


class CovarianceListener(sdk_module.SDKListener):
    def __init__(self):
        super().__init__()
        self.latest = None
        self.update_count = 0

    def on_pose_covariance(self, timestamp_ns, covariance):
        self.latest = (timestamp_ns, covariance.copy() if covariance is not None else None)
        self.update_count += 1


def describe_covariance(covariance):
    readable = covariance.to_readable()
    return (
        "xy95={:.3f} m ellipsoid95={} rot1sigma={} deg".format(
            readable.position_radius_95_xy,
            [round(value, 4) for value in readable.position_ellipsoid_95_xyz],
            [round(value, 3) for value in readable.rotation_1sigma_rpy_deg],
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Monitor Aurora pose covariance updates")
    parser.add_argument("connection_string", nargs="?", help="Aurora device address, for example 192.168.11.1")
    parser.add_argument("--duration", type=float, default=0.0, help="Optional run duration in seconds")
    args = parser.parse_args()

    listener = CovarianceListener()
    running = True

    def handle_signal(_sig, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    with sdk_module.AuroraSDK(listener=listener) as sdk:
        server_address, _ = connect_sdk(sdk, device=args.connection_string)
        version = sdk.get_version_info()
        print("Connected to {} using SDK {}".format(server_address or "<discovered>", version["version_string"]))

        for _ in range(50):
            try:
                covariance, timestamp_ns = sdk.data_provider.get_recent_pose_covariance()
                print("Initial covariance @ {} ns: {}".format(timestamp_ns, describe_covariance(covariance)))
                break
            except sdk_module.DataNotReadyError:
                time.sleep(0.2)
        else:
            print("Pose covariance data not ready yet; waiting for callbacks...")

        start_time = time.time()
        last_update_count = -1
        while running:
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                break

            if listener.update_count != last_update_count and listener.latest is not None:
                last_update_count = listener.update_count
                timestamp_ns, covariance = listener.latest
                if covariance is not None:
                    print(
                        "[callback #{:04d}] {} ns {}".format(
                            listener.update_count, timestamp_ns, describe_covariance(covariance)
                        )
                    )
            time.sleep(0.1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
