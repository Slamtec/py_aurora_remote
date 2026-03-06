#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/pose_augmentation.py
#  *
#  */
"""
Pose augmentation example for Aurora SDK 2.1.1.

Usage:
    python pose_augmentation.py
    python pose_augmentation.py 192.168.11.1 --frequency 200
"""

import argparse
import signal
import sys
import time

from _demo_common import connect_sdk, format_pose, load_sdk_module

sdk_module = load_sdk_module()


FREQUENCY_MAP = {
    "highest": sdk_module.POSE_OUTPUT_FREQ_HIGHEST_POSSIBLE,
    "50": sdk_module.POSE_OUTPUT_FREQ_50HZ,
    "100": sdk_module.POSE_OUTPUT_FREQ_100HZ,
    "200": sdk_module.POSE_OUTPUT_FREQ_200HZ,
}

MODE_MAP = {
    "visual": sdk_module.POSE_AUGMENTATION_MODE_VISUAL_ONLY,
    "imu-vision": sdk_module.POSE_AUGMENTATION_MODE_IMU_VISION_MIXED,
}


class PoseAugmentationListener(sdk_module.SDKListener):
    def __init__(self):
        super().__init__()
        self.pose_count = 0
        self.mixed_count = 0
        self.visual_count = 0
        self.latest = None

    def on_pose_augmentation_result(self, timestamp_ns, mode, pose):
        self.pose_count += 1
        if mode == sdk_module.POSE_AUGMENTATION_MODE_IMU_VISION_MIXED:
            self.mixed_count += 1
        else:
            self.visual_count += 1
        if pose is not None:
            self.latest = (timestamp_ns, mode, pose.translation.to_tuple(), pose.quaternion.to_tuple())
        else:
            self.latest = (timestamp_ns, mode, None, None)


def main():
    parser = argparse.ArgumentParser(description="Start Aurora pose augmentation")
    parser.add_argument("connection_string", nargs="?", help="Aurora device address, for example 192.168.11.1")
    parser.add_argument("--mode", choices=sorted(MODE_MAP), default="imu-vision")
    parser.add_argument("--frequency", choices=sorted(FREQUENCY_MAP), default="200")
    parser.add_argument("--smoothing", action="store_true", help="Enable exponential smoothing")
    parser.add_argument("--smoothing-factor", type=float, default=0.2)
    parser.add_argument("--duration", type=float, default=0.0, help="Optional run duration in seconds")
    args = parser.parse_args()

    listener = PoseAugmentationListener()
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

        config = sdk_module.PoseAugmentationConfig()
        config.output_frequency = FREQUENCY_MAP[args.frequency]
        config.enable_smoothing = int(args.smoothing)
        config.smoothing_factor = float(args.smoothing_factor)

        sdk.data_provider.start_pose_augmentation(MODE_MAP[args.mode], config)
        print(
            "Pose augmentation started: mode={} frequency={}Hz smoothing={}".format(
                args.mode, args.frequency, bool(config.enable_smoothing)
            )
        )

        start_time = time.time()
        last_report = 0.0
        last_pose_count = 0
        try:
            while running:
                elapsed = time.time() - start_time
                if args.duration > 0 and elapsed >= args.duration:
                    break

                if elapsed - last_report >= 5.0:
                    delta = listener.pose_count - last_pose_count
                    last_pose_count = listener.pose_count
                    last_report = elapsed
                    rate = delta / 5.0 if elapsed >= 5.0 else 0.0
                    print(
                        "[{:5.1f}s] poses={} visual={} mixed={} rate={:.1f} Hz".format(
                            elapsed, listener.pose_count, listener.visual_count, listener.mixed_count, rate
                        )
                    )
                    if listener.latest is not None:
                        timestamp_ns, mode, position, rotation = listener.latest
                        mode_name = "IMU_MIXED" if mode == sdk_module.POSE_AUGMENTATION_MODE_IMU_VISION_MIXED else "VISUAL"
                        if position is not None and rotation is not None:
                            print("  latest {} @ {} ns {}".format(mode_name, timestamp_ns, format_pose((position, rotation))))
                        else:
                            print("  latest {} @ {} ns <no pose>".format(mode_name, timestamp_ns))

                time.sleep(0.1)
        finally:
            try:
                sdk.data_provider.stop_pose_augmentation()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
