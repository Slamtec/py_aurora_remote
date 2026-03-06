#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/_demo_common.py
#  *
#  */
"""
Shared helpers for Aurora Python SDK examples.
"""

import ipaddress
import os
import sys


def load_sdk_module():
    """Import the Aurora SDK package, falling back to the local source tree."""
    try:
        import slamtec_aurora_sdk as sdk_module
        return sdk_module
    except ImportError:
        print("Warning: Aurora SDK package not found, using source code from parent directory")
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "python_bindings",
            ),
        )
        import slamtec_aurora_sdk as sdk_module
        return sdk_module


def _normalize_ip_address(address):
    if not address:
        return None
    if address.startswith("[") and address.endswith("]"):
        return address[1:-1]
    return address


def _score_discovered_address(address):
    """
    Score a discovered address for standalone client usage.

    Prefer IPv4 and routable IPv6 addresses. De-prioritize IPv6 link-local
    addresses because they require an interface scope that discovery does not
    provide.
    """
    normalized = _normalize_ip_address(address)
    if not normalized:
        return (-1, "")

    try:
        ip = ipaddress.ip_address(normalized)
    except ValueError:
        return (10, normalized)

    if isinstance(ip, ipaddress.IPv4Address):
        return (100, normalized)
    if ip.is_link_local:
        return (20, normalized)
    return (80, normalized)


def extract_server_address(device_info):
    """Extract the most usable server address from discovery results."""
    options = device_info.get("options", []) if isinstance(device_info, dict) else []
    best_address = None
    best_score = (-1, "")
    seen = set()
    for option in options:
        address = option.get("address")
        if not address or address in seen:
            continue
        seen.add(address)
        score = _score_discovered_address(address)
        if score > best_score:
            best_score = score
            best_address = address
    return best_address


def connect_sdk(sdk, device=None, timeout=5.0):
    """
    Connect to a device by explicit address or auto-discovery.

    Returns:
        tuple: `(server_address, discovery_info)`
    """
    if device:
        sdk.connect(connection_string=device)
        return device, None

    devices = sdk.discover_devices(timeout=timeout)
    if not devices:
        raise RuntimeError("No Aurora devices found")

    sdk.connect(device_info=devices[0])
    return extract_server_address(devices[0]), devices[0]


def confirm(prompt):
    """Prompt for interactive confirmation."""
    return input("{} [y/N]: ".format(prompt)).strip().lower() in ("y", "yes")


def format_pose(pose):
    """Format a PoseSE3 or pose tuple for console output."""
    if hasattr(pose, "translation") and hasattr(pose, "quaternion"):
        position = pose.translation.to_tuple()
        rotation = pose.quaternion.to_tuple()
    else:
        position, rotation = pose
    return (
        "pos=({:.3f}, {:.3f}, {:.3f}) quat=({:.4f}, {:.4f}, {:.4f}, {:.4f})".format(
            position[0], position[1], position[2], rotation[0], rotation[1], rotation[2], rotation[3]
        )
    )
