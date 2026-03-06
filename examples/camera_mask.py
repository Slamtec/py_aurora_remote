#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/camera_mask.py
#  *
#  */
"""
Camera mask example for Aurora SDK 2.1.1.
"""

import argparse
import sys

from _demo_common import connect_sdk, load_sdk_module

sdk_module = load_sdk_module()


def require_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required for camera mask image I/O: {}".format(exc))
    return cv2


def main():
    parser = argparse.ArgumentParser(description="Manage Aurora static camera masks")
    parser.add_argument("connection_string", nargs="?", help="Aurora device address, for example 192.168.11.1")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Show whether static masking is enabled")

    enable_parser = subparsers.add_parser("enable", help="Enable or disable static masking")
    enable_parser.add_argument("value", choices=("0", "1", "false", "true", "off", "on"))

    subparsers.add_parser("list", help="List camera indices that have masks configured")

    get_parser = subparsers.add_parser("get-mask", help="Download a mask image")
    get_parser.add_argument("camera_index", type=int)
    get_parser.add_argument("output")

    set_parser = subparsers.add_parser("set-mask", help="Upload a mask image")
    set_parser.add_argument("camera_index", type=int)
    set_parser.add_argument("input")

    remove_parser = subparsers.add_parser("remove-mask", help="Delete a camera mask")
    remove_parser.add_argument("camera_index", type=int)

    subparsers.add_parser("refresh", help="Refresh the manager cache")
    args = parser.parse_args()

    with sdk_module.AuroraSDK() as sdk:
        server_address, _ = connect_sdk(sdk, device=args.connection_string)
        print("Connected to {}".format(server_address or "<discovered>"))
        manager = sdk.camera_mask

        if args.command == "status":
            print("static_mask_enabled={}".format(manager.is_static_mask_enabled()))
            return 0

        if args.command == "enable":
            enabled = args.value.lower() in ("1", "true", "on")
            manager.set_static_mask_enable(enabled)
            print("static_mask_enabled={}".format(enabled))
            return 0

        if args.command == "list":
            for camera_index in manager.get_static_camera_mask_image_id_list():
                print(camera_index)
            return 0

        if args.command == "get-mask":
            cv2 = require_cv2()
            image = manager.get_static_camera_mask_image(args.camera_index)
            gray = image.to_numpy_image(color_order="gray")
            if gray is None:
                raise RuntimeError("Mask image payload is empty")
            if not cv2.imwrite(args.output, gray):
                raise RuntimeError("Failed to write {}".format(args.output))
            print("Saved mask to {}".format(args.output))
            return 0

        if args.command == "set-mask":
            cv2 = require_cv2()
            gray = cv2.imread(args.input, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                raise RuntimeError("Failed to read {}".format(args.input))
            manager.set_static_camera_mask_image(args.camera_index, gray)
            print("Uploaded mask for camera {}".format(args.camera_index))
            return 0

        if args.command == "remove-mask":
            manager.remove_static_camera_mask_image(args.camera_index)
            print("Removed mask for camera {}".format(args.camera_index))
            return 0

        if args.command == "refresh":
            manager.refresh()
            print("Refreshed camera mask manager")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
