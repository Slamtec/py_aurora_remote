#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/transform_manager.py
#  *
#  */
"""
Transform manager example for Aurora SDK 2.1.1.
"""

import argparse
import sys

from _demo_common import connect_sdk, format_pose, load_sdk_module

sdk_module = load_sdk_module()


def main():
    parser = argparse.ArgumentParser(description="Manage Aurora device transforms")
    parser.add_argument("connection_string", nargs="?", help="Aurora device address, for example 192.168.11.1")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List all transforms")

    get_parser = subparsers.add_parser("get", help="Get a transform by name")
    get_parser.add_argument("name")

    set_parser = subparsers.add_parser("set", help="Set a transform")
    set_parser.add_argument("name")
    set_parser.add_argument("tx", type=float)
    set_parser.add_argument("ty", type=float)
    set_parser.add_argument("tz", type=float)
    set_parser.add_argument("qx", type=float)
    set_parser.add_argument("qy", type=float)
    set_parser.add_argument("qz", type=float)
    set_parser.add_argument("qw", type=float)

    reset_parser = subparsers.add_parser("reset", help="Reset a transform to identity")
    reset_parser.add_argument("name")

    subparsers.add_parser("refresh", help="Refresh the manager cache")
    args = parser.parse_args()

    with sdk_module.AuroraSDK() as sdk:
        server_address, _ = connect_sdk(sdk, device=args.connection_string)
        print("Connected to {}".format(server_address or "<discovered>"))
        manager = sdk.transform_manager

        if args.command == "list":
            for name in manager.get_all_transform_names():
                pose = manager.get_transform(name)
                print("{} {}".format(name, format_pose(pose)))
            return 0

        if args.command == "get":
            pose = manager.get_transform(args.name)
            print("{} {}".format(args.name, format_pose(pose)))
            return 0

        if args.command == "set":
            manager.set_transform(
                args.name,
                ((args.tx, args.ty, args.tz), (args.qx, args.qy, args.qz, args.qw)),
            )
            print("Updated transform '{}'".format(args.name))
            return 0

        if args.command == "reset":
            manager.reset_transform(args.name)
            print("Reset transform '{}'".format(args.name))
            return 0

        if args.command == "refresh":
            manager.refresh()
            print("Refreshed transform manager")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
