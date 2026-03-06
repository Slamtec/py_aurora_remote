# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/dashcam_recorder.py
#  *
#  */
"""
Dashcam recorder management for Aurora SDK 2.1.1.
"""

import ctypes

from .c_bindings import get_c_bindings
from .data_types import DashcamSessionInfo, DashcamStatus, DashcamStorageStatus, ERRORCODE_OK
from .exceptions import AuroraSDKError, ConnectionError


class DashcamStorageInfo:
    """Wrapper around a dashcam storage info handle."""

    def __init__(self, handle, c_bindings=None):
        self._handle = handle
        self._c_bindings = c_bindings or get_c_bindings()

    def is_valid(self):
        return bool(self._handle)

    def close(self):
        if self._handle:
            self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_destroy(self._handle)
            self._handle = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    @property
    def path(self):
        if not self._handle:
            return ""
        path = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_get_path(self._handle)
        if not path:
            return ""
        return path.decode("utf-8", errors="ignore")

    def has_storage_status(self):
        if not self._handle:
            return False
        return bool(self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_has_storage_status(self._handle))

    def get_storage_status(self):
        if not self._handle:
            raise AuroraSDKError("Dashcam storage info handle is invalid")

        status = DashcamStorageStatus()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_get_storage_status(
            self._handle, ctypes.byref(status)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get dashcam storage status (error code: {})".format(error_code))
        return status

    def get_session_count(self):
        if not self._handle:
            return 0
        count = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_get_session_count(self._handle)
        if count < 0:
            raise AuroraSDKError("Failed to query dashcam session count")
        return count

    def get_session(self, index):
        if not self._handle:
            raise AuroraSDKError("Dashcam storage info handle is invalid")

        session = DashcamSessionInfo()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_get_session(
            self._handle, index, ctypes.byref(session)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get dashcam session {} (error code: {})".format(index, error_code))
        return session

    @property
    def sessions(self):
        return [self.get_session(index) for index in range(self.get_session_count())]

    def has_current_session(self):
        if not self._handle:
            return False
        return bool(self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_has_current_session(self._handle))

    def get_current_session(self):
        if not self._handle:
            raise AuroraSDKError("Dashcam storage info handle is invalid")

        session = DashcamSessionInfo()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_storage_info_get_current_session(
            self._handle, ctypes.byref(session)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get current dashcam session (error code: {})".format(error_code))
        return session


class DashcamRecorderManager:
    """Monitor and control the device dashcam recorder."""

    def __init__(self, controller, c_bindings=None):
        self._controller = controller
        self._c_bindings = c_bindings or get_c_bindings()

    def _ensure_connected(self):
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")

    def get_status(self, timeout_ms=5000):
        self._ensure_connected()

        status = DashcamStatus()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_recorder_get_status(
            self._controller.session_handle, ctypes.byref(status), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get dashcam status (error code: {})".format(error_code))
        return status

    def get_storage_info(self, timeout_ms=5000):
        self._ensure_connected()

        handle = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_recorder_get_storage_info(
            self._controller.session_handle, timeout_ms
        )
        if not handle:
            raise AuroraSDKError("Failed to get dashcam storage info")
        return DashcamStorageInfo(handle, c_bindings=self._c_bindings)

    def set_enable(self, enable, timeout_ms=5000):
        self._ensure_connected()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_recorder_set_enable(
            self._controller.session_handle, int(enable), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set dashcam enable state (error code: {})".format(error_code))

    def set_size_limit(self, size_limit_gb, timeout_ms=5000):
        self._ensure_connected()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_recorder_set_size_limit(
            self._controller.session_handle, float(size_limit_gb), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set dashcam size limit (error code: {})".format(error_code))

    def invalidate_sessions(self, timeout_ms=10000):
        self._ensure_connected()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_dashcam_recorder_invalidate_sessions(
            self._controller.session_handle, timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to invalidate dashcam sessions (error code: {})".format(error_code))
