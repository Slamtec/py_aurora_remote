#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/persistent_config.py
#  *
#  */
"""
Persistent configuration example for Aurora SDK 2.1.1.
"""

import argparse
import os
import sys

from _demo_common import connect_sdk, load_sdk_module

sdk_module = load_sdk_module()


def load_config_value(value):
    if os.path.exists(value):
        with open(value, "r", encoding="utf-8") as handle:
            return handle.read()
    return value


def main():
    parser = argparse.ArgumentParser(description="Manage Aurora persistent configuration")
    parser.add_argument("connection_string", nargs="?", help="Aurora device address, for example 192.168.11.1")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("enum", help="Enumerate all config entry paths")

    get_parser = subparsers.add_parser("get", help="Read a config entry as JSON")
    get_parser.add_argument("filter_path")
    get_parser.add_argument("-o", "--output", help="Optional output file path")

    set_parser = subparsers.add_parser("set", help="Set a config entry from JSON text or file")
    set_parser.add_argument("filter_path")
    set_parser.add_argument("key")
    set_parser.add_argument("value", help="JSON string or a path to a JSON file")

    reset_parser = subparsers.add_parser("reset", help="Reset a config entry to its default")
    reset_parser.add_argument("filter_path")

    subparsers.add_parser("reset-all", help="Reset all config entries")
    args = parser.parse_args()

    with sdk_module.AuroraSDK() as sdk:
        server_address, _ = connect_sdk(sdk, device=args.connection_string)
        print("Connected to {}".format(server_address or "<discovered>"))

        manager = sdk.persistent_config

        if args.command == "enum":
            for entry in manager.enum_all_entries():
                print(entry)
            return 0

        if args.command == "get":
            payload = manager.get_config(args.filter_path)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                print("Saved config to {}".format(args.output))
            else:
                print(payload)
            return 0

        if args.command == "set":
            manager.set_config(args.filter_path, args.key, load_config_value(args.value))
            print("Updated config '{}' using key '{}'".format(args.filter_path, args.key))
            return 0

        if args.command == "reset":
            manager.reset_config(args.filter_path)
            print("Reset config '{}'".format(args.filter_path))
            return 0

        if args.command == "reset-all":
            manager.reset_all_config()
            print("Reset all config entries")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
