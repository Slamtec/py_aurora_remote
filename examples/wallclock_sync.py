#!/usr/bin/env python3
# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: examples/wallclock_sync.py
#  *
#  */
"""
Wall clock synchronization demo for Aurora SDK 2.1.1.

This example demonstrates the wall clock specific time sync APIs:
- get_wallclock_offset()
- sync_server_wallclock()
- evaluate_wallclock_accuracy()

Usage:
    python wallclock_sync.py
    python wallclock_sync.py 192.168.11.1
    python wallclock_sync.py 192.168.11.1 --force-sync --samples 10
"""

import argparse
import statistics
import sys
import time

from _demo_common import extract_server_address, load_sdk_module

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


def ns_to_ms(value_ns):
    return float(value_ns) / 1_000_000.0


def describe_offset(offset_ns):
    abs_offset_ms = abs(ns_to_ms(offset_ns))
    if abs_offset_ms > 10.0:
        return "large offset detected - sync recommended"
    if abs_offset_ms > 1.0:
        return "small offset detected - sync optional"
    return "clocks already well synchronized"


def main():
    parser = argparse.ArgumentParser(description="Aurora wall clock synchronization demo")
    parser.add_argument(
        "connection_string",
        nargs="?",
        help="Aurora device address, for example 192.168.11.1",
    )
    parser.add_argument("--port", type=int, default=sdk_module.TIMESYNC_DEFAULT_PORT)
    parser.add_argument("--timeout-ms", type=int, default=1000, help="Timeout for sync RPCs")
    parser.add_argument("--sync-threshold-ms", type=float, default=1.0, help="Auto-sync threshold in milliseconds")
    parser.add_argument("--samples", type=int, default=10, help="Number of accuracy samples to collect")
    parser.add_argument("--sample-interval-ms", type=int, default=50, help="Delay between accuracy samples")
    parser.add_argument("--force-sync", action="store_true", help="Run sync even if the offset is below threshold")
    args = parser.parse_args()

    server_address = resolve_server_address(args.connection_string)

    print("Aurora wall clock sync demo")
    print("  server: {}:{}".format(server_address, args.port))
    print("  samples: {}".format(args.samples))

    with sdk_module.TimeSyncClient(sdk_module.TIMESYNC_DOMAIN_WALL_CLOCK) as client:
        client.connect(server_address, args.port)
        client.set_options(sdk_module.TimeSyncClient.get_default_options())
        client.initialize()
        wait_for_sync(client)

        quality = client.get_quality().as_dict()
        print("  sync quality:", quality)

        print("\nStep 1: Query current wall clock offset")
        offset = client.get_wallclock_offset(timeout_ms=args.timeout_ms)
        print("  success: {}".format(bool(offset.success)))
        print("  offset:  {:.3f} ms".format(ns_to_ms(offset.offset_ns)))
        print("  rtt:     {:.3f} ms".format(ns_to_ms(offset.rtt_ns)))
        print("  status:  {}".format(describe_offset(offset.offset_ns)))

        should_sync = args.force_sync or abs(ns_to_ms(offset.offset_ns)) > args.sync_threshold_ms
        if should_sync:
            print("\nStep 2: Synchronize device wall clock")
            sync_result = client.sync_server_wallclock(timeout_ms=args.timeout_ms)
            print("  success:         {}".format(bool(sync_result.success)))
            print("  applied offset:  {:.3f} ms".format(ns_to_ms(sync_result.applied_offset_ns)))
            print("  server utc time: {}".format(int(sync_result.server_utc_ns)))
        else:
            print("\nStep 2: Skip synchronization")
            print("  offset is within threshold {:.3f} ms".format(args.sync_threshold_ms))

        print("\nStep 3: Evaluate wall clock synchronization accuracy")
        accuracy_errors_ms = []
        for index in range(args.samples):
            accuracy = client.evaluate_wallclock_accuracy(timeout_ms=args.timeout_ms)
            error_ms = abs(ns_to_ms(accuracy.offset_error_ns))
            accuracy_errors_ms.append(error_ms)
            print(
                "  sample {:02d}: success={} error={:.3f} ms rtt={:.3f} ms server_utc_ns={}".format(
                    index + 1,
                    bool(accuracy.success),
                    error_ms,
                    ns_to_ms(accuracy.rtt_ns),
                    int(accuracy.server_utc_ns),
                )
            )
            if index + 1 < args.samples:
                time.sleep(max(args.sample_interval_ms, 0) / 1000.0)

        if accuracy_errors_ms:
            mean_error = statistics.mean(accuracy_errors_ms)
            max_error = max(accuracy_errors_ms)
            min_error = min(accuracy_errors_ms)
            print("\nAccuracy summary")
            print("  mean error: {:.3f} ms".format(mean_error))
            print("  min error:  {:.3f} ms".format(min_error))
            print("  max error:  {:.3f} ms".format(max_error))

            if max_error < 1.0:
                verdict = "EXCELLENT (< 1 ms)"
            elif max_error < 5.0:
                verdict = "GOOD (< 5 ms)"
            else:
                verdict = "POOR (>= 5 ms)"
            print("  verdict:    {}".format(verdict))

    return 0


if __name__ == "__main__":
    sys.exit(main())
