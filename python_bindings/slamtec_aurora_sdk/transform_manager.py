# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/transform_manager.py
#  *
#  */
"""
Transform manager for Aurora SDK 2.1.1.
"""

import ctypes

from .c_bindings import get_c_bindings
from .data_types import ERRORCODE_OK, PoseSE3
from .exceptions import AuroraSDKError, ConnectionError


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


def _coerce_pose_se3(pose):
    if isinstance(pose, PoseSE3):
        return pose

    if not isinstance(pose, tuple) or len(pose) != 2:
        raise AuroraSDKError("Expected PoseSE3 or ((x, y, z), (qx, qy, qz, qw)) tuple")

    position, quaternion = pose
    coerced = PoseSE3()
    coerced.translation.x, coerced.translation.y, coerced.translation.z = position
    coerced.quaternion.x, coerced.quaternion.y, coerced.quaternion.z, coerced.quaternion.w = quaternion
    return coerced


class TransformManager:
    """Manage configurable device transforms."""

    def __init__(self, controller, c_bindings=None):
        self._controller = controller
        self._c_bindings = c_bindings or get_c_bindings()
        self._handle = None

    def _ensure_session(self):
        if self._controller.session_handle is None:
            raise AuroraSDKError("Session not created")

    def _ensure_connected(self):
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")

    def _ensure_handle(self):
        self._ensure_session()
        if self._handle is None:
            self._handle = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_create(
                self._controller.session_handle
            )
            if not self._handle:
                raise AuroraSDKError("Failed to create transform manager")

    def close(self):
        if self._handle:
            self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_destroy(self._handle)
            self._handle = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def get_all_transform_names(self, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        list_handle = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_get_all_transform_names(
            self._handle, timeout_ms
        )
        if not list_handle:
            raise AuroraSDKError("Failed to enumerate transform names")

        try:
            count = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_name_list_get_count(list_handle)
            if count < 0:
                raise AuroraSDKError("Failed to read transform name list")

            names = []
            for index in range(count):
                name = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_name_list_get_entry(
                    list_handle, index
                )
                if name:
                    names.append(name.decode("utf-8", errors="ignore"))
            return names
        finally:
            self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_name_list_destroy(list_handle)

    def get_transform(self, name, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        pose = PoseSE3()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_get_transform(
            self._handle, _as_bytes(name), ctypes.byref(pose), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to get transform '{}' (error code: {})".format(name, error_code))
        return pose

    def set_transform(self, name, pose, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        pose = _coerce_pose_se3(pose)
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_set_transform(
            self._handle, _as_bytes(name), ctypes.byref(pose), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set transform '{}' (error code: {})".format(name, error_code))

    def reset_transform(self, name, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_reset_transform(
            self._handle, _as_bytes(name), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to reset transform '{}' (error code: {})".format(name, error_code))

    def has_transform(self, name, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        result = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_has_transform(
            self._handle, _as_bytes(name), timeout_ms
        )
        if result < 0:
            raise AuroraSDKError("Failed to query transform '{}'".format(name))
        return bool(result)

    def refresh(self, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_transform_manager_refresh(
            self._handle, timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to refresh transform manager (error code: {})".format(error_code))
