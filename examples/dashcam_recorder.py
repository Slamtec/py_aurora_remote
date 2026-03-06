#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/dashcam_recorder.py
#  *
#  */
"""
Dashcam recorder example for Aurora SDK 2.1.1.
"""

import argparse
import sys
import time

from _demo_common import connect_sdk, load_sdk_module

sdk_module = load_sdk_module()


def print_status(manager):
    status = manager.get_status()
    print(
        "enabled={} recording={} state={} size_limit_gb={:.2f} current_size_bytes={} message={}".format(
            bool(status.enabled),
            bool(status.recording),
            int(status.working_state),
            float(status.size_limit_gb),
            int(status.current_size_bytes),
            status.message,
        )
    )

    storage_info = manager.get_storage_info()
    try:
        print("storage_path={}".format(storage_info.path))
        if storage_info.has_storage_status():
            storage_status = storage_info.get_storage_status()
            print(
                "storage total={} free={} used_by_dashcam={}".format(
                    int(storage_status.total_space_bytes),
                    int(storage_status.free_space_bytes),
                    int(storage_status.used_by_dashcam_bytes),
                )
            )
        print("session_count={}".format(storage_info.get_session_count()))
        for session in storage_info.sessions:
            print(
                "  session id={} size={} blobs={} start={} end={}".format(
                    int(session.session_id),
                    int(session.size),
                    int(session.blob_idx_count),
                    int(session.start_time),
                    int(session.end_time),
                )
            )
    finally:
        storage_info.close()


def main():
    parser = argparse.ArgumentParser(description="Monitor and control the Aurora dashcam recorder")
    parser.add_argument("connection_string", nargs="?", help="Aurora device address, for example 192.168.11.1")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Show status once")
    watch_parser = subparsers.add_parser("watch", help="Continuously print status")
    watch_parser.add_argument("--interval", type=float, default=2.0)
    subparsers.add_parser("enable", help="Enable dashcam recording")
    subparsers.add_parser("disable", help="Disable dashcam recording")
    limit_parser = subparsers.add_parser("set-limit", help="Set dashcam size limit in GB")
    limit_parser.add_argument("size_limit_gb", type=float)
    subparsers.add_parser("invalidate", help="Delete all dashcam sessions")
    args = parser.parse_args()

    with sdk_module.AuroraSDK() as sdk:
        server_address, _ = connect_sdk(sdk, device=args.connection_string)
        print("Connected to {}".format(server_address or "<discovered>"))
        manager = sdk.dashcam_recorder

        if args.command == "status":
            print_status(manager)
            return 0

        if args.command == "watch":
            try:
                while True:
                    print_status(manager)
                    print("-" * 60)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                return 0

        if args.command == "enable":
            manager.set_enable(True)
            print("Dashcam recorder enabled")
            return 0

        if args.command == "disable":
            manager.set_enable(False)
            print("Dashcam recorder disabled")
            return 0

        if args.command == "set-limit":
            manager.set_size_limit(args.size_limit_gb)
            print("Dashcam size limit set to {:.2f} GB".format(args.size_limit_gb))
            return 0

        if args.command == "invalidate":
            manager.invalidate_sessions()
            print("Dashcam sessions invalidated")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
