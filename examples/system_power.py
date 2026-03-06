#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/system_power.py
#  *
#  */
"""
System power example for Aurora SDK 2.1.1.
"""

import argparse
import sys

from _demo_common import confirm, connect_sdk, load_sdk_module

sdk_module = load_sdk_module()


def print_status(sdk):
    version = sdk.get_version_info()
    device_info = sdk.controller.get_device_info()
    print("SDK Version:", version["version_string"])
    print("Device Name:", device_info.device_name)
    print("Model:", device_info.device_model_string)
    print("Firmware:", device_info.firmware_version)
    print("Serial:", device_info.serial_number)


def main():
    parser = argparse.ArgumentParser(description="Request Aurora device power operations")
    parser.add_argument("command", choices=("status", "reboot", "shutdown"))
    parser.add_argument(
        "connection_string",
        nargs="?",
        help="Aurora device address, for example 192.168.11.1",
    )
    parser.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    args = parser.parse_args()

    if args.command in ("reboot", "shutdown") and not args.connection_string:
        raise SystemExit("Explicit device address is required for reboot/shutdown")

    with sdk_module.AuroraSDK() as sdk:
        server_address, _ = connect_sdk(sdk, device=args.connection_string)
        print("Connected to {}".format(server_address or "<discovered>"))
        print_status(sdk)

        if args.command == "status":
            return 0

        if not args.yes and not confirm("Proceed with {}?".format(args.command.upper())):
            print("Cancelled")
            return 0

        if args.command == "reboot":
            sdk.controller.reboot_device()
            print("Reboot command sent")
            return 0

        sdk.controller.shutdown_device()
        print("Shutdown command sent")
        return 0


if __name__ == "__main__":
    sys.exit(main())
