# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/timesync.py
#  *
#  */
"""
Standalone time synchronization client for Aurora SDK 2.1.1.
"""

import ctypes

from .c_bindings import get_c_bindings
from .data_types import (
    ERRORCODE_OK,
    TIMESYNC_DEFAULT_PORT,
    TimeSyncOptions,
    TimeSyncQuality,
    WallclockAccuracyResult,
    WallclockOffsetResult,
    WallclockSyncResult,
)
from .exceptions import AuroraSDKError


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


class TimeSyncClient:
    """Standalone Aurora time synchronization client."""

    def __init__(self, domain, c_bindings=None):
        self._c_bindings = c_bindings or get_c_bindings()
        self._handle = None

        error_code = ctypes.c_int()
        self._handle = self._c_bindings.lib.slamtec_aurora_sdk_timesync_create_instance(
            int(domain), ctypes.byref(error_code)
        )
        if error_code.value != ERRORCODE_OK or not self._handle:
            raise AuroraSDKError(
                "Failed to create time sync client (error code: {})".format(error_code.value)
            )

    @classmethod
    def get_default_options(cls, c_bindings=None):
        c_bindings = c_bindings or get_c_bindings()
        options = TimeSyncOptions()
        c_bindings.lib.slamtec_aurora_sdk_timesync_get_default_options(ctypes.byref(options))
        return options

    def close(self):
        if self._handle:
            self._c_bindings.lib.slamtec_aurora_sdk_timesync_destroy_instance(self._handle)
            self._handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def connect(self, server_address, server_port=TIMESYNC_DEFAULT_PORT):
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_connect(
            self._handle, _as_bytes(server_address), server_port
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to connect time sync client (error code: {})".format(error_code))

    def set_options(self, options):
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_set_options(
            self._handle, ctypes.byref(options)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set time sync options (error code: {})".format(error_code))

    def initialize(self):
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_initialize(self._handle)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to initialize time sync client (error code: {})".format(error_code))

    def is_synchronized(self):
        return bool(self._c_bindings.lib.slamtec_aurora_sdk_timesync_is_synchronized(self._handle))

    def is_running(self):
        return bool(self._c_bindings.lib.slamtec_aurora_sdk_timesync_is_running(self._handle))

    def translate_timestamp(self, aurora_timestamp_ns):
        translated = ctypes.c_uint64()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_translate_timestamp(
            self._handle, aurora_timestamp_ns, ctypes.byref(translated)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to translate timestamp (error code: {})".format(error_code))
        return translated.value

    def get_quality(self):
        quality = TimeSyncQuality()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_get_quality(
            self._handle, ctypes.byref(quality)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get time sync quality (error code: {})".format(error_code))
        return quality

    def get_current_server_timestamp(self, timeout_ms=1000):
        server_timestamp = ctypes.c_uint64()
        client_timestamp = ctypes.c_uint64()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_get_current_server_timestamp(
            self._handle, timeout_ms, ctypes.byref(server_timestamp), ctypes.byref(client_timestamp)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError(
                "Failed to query current server timestamp (error code: {})".format(error_code)
            )
        return server_timestamp.value, client_timestamp.value

    def stop(self):
        self._c_bindings.lib.slamtec_aurora_sdk_timesync_stop(self._handle)

    def get_wallclock_offset(self, timeout_ms=1000):
        result = WallclockOffsetResult()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_get_wallclock_offset(
            self._handle, timeout_ms, ctypes.byref(result)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get wall clock offset (error code: {})".format(error_code))
        return result

    def sync_server_wallclock(self, timeout_ms=1000):
        result = WallclockSyncResult()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_sync_server_wallclock(
            self._handle, timeout_ms, ctypes.byref(result)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to sync server wall clock (error code: {})".format(error_code))
        return result

    def evaluate_wallclock_accuracy(self, timeout_ms=1000):
        result = WallclockAccuracyResult()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_timesync_evaluate_wallclock_accuracy(
            self._handle, timeout_ms, ctypes.byref(result)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError(
                "Failed to evaluate wall clock accuracy (error code: {})".format(error_code)
            )
        return result
