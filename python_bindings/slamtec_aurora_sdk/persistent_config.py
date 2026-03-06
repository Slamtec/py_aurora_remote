# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/persistent_config.py
#  *
#  */
"""
Persistent configuration management for Aurora SDK 2.1.1.
"""

import json

from .c_bindings import get_c_bindings
from .data_types import ERRORCODE_OK
from .exceptions import AuroraSDKError, ConnectionError


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


class ConfigData:
    """JSON-backed config data wrapper for persistent configuration APIs."""

    def __init__(self, c_bindings=None, handle=None, owned=True):
        self._c_bindings = c_bindings or get_c_bindings()
        self._owned = owned
        self._handle = handle if handle is not None else self._c_bindings.lib.slamtec_aurora_sdk_config_data_create()
        if not self._handle:
            raise AuroraSDKError("Failed to create config data object")

    @property
    def handle(self):
        return self._handle

    def is_valid(self):
        return bool(self._handle)

    def close(self):
        if self._owned and self._handle:
            self._c_bindings.lib.slamtec_aurora_sdk_config_data_destroy(self._handle)
            self._handle = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def load_from_string(self, json_string):
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_config_data_load_from_string(
            self._handle, _as_bytes(json_string)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to load config data from string (error code: {})".format(error_code))
        return self

    def dump_to_string(self):
        import ctypes

        size_out = ctypes.c_size_t()
        dumped = self._c_bindings.lib.slamtec_aurora_sdk_config_data_create_string_dump(
            self._handle, ctypes.byref(size_out)
        )
        if dumped is None:
            raise AuroraSDKError("Failed to dump config data to string")

        try:
            return dumped.decode("utf-8") if isinstance(dumped, bytes) else dumped
        finally:
            self._c_bindings.lib.slamtec_aurora_sdk_config_data_destroy_string_dump(self._handle)

    def load_from_file(self, file_path):
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_config_data_load_from_file(
            self._handle, _as_bytes(file_path)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to load config data from file (error code: {})".format(error_code))
        return self

    def save_to_file(self, file_path):
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_config_data_save_to_file(
            self._handle, _as_bytes(file_path)
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to save config data to file (error code: {})".format(error_code))

    def to_object(self):
        return json.loads(self.dump_to_string())

    @classmethod
    def from_string(cls, json_string, c_bindings=None):
        return cls(c_bindings=c_bindings).load_from_string(json_string)

    @classmethod
    def from_object(cls, value, c_bindings=None):
        if isinstance(value, str):
            json_string = value
        else:
            json_string = json.dumps(value, indent=2, sort_keys=True)
        return cls.from_string(json_string, c_bindings=c_bindings)


class PersistentConfigManager:
    """Manager for device persistent configuration entries."""

    def __init__(self, controller, c_bindings=None):
        self._controller = controller
        self._c_bindings = c_bindings or get_c_bindings()

    def _ensure_connected(self):
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")

    def _iter_string_list_handle(self, list_handle, count_fn, entry_fn, destroy_fn):
        if not list_handle:
            raise AuroraSDKError("Received invalid handle from SDK")

        try:
            count = count_fn(list_handle)
            if count < 0:
                raise AuroraSDKError("Failed to read list handle")

            values = []
            for index in range(count):
                entry = entry_fn(list_handle, index)
                if entry:
                    values.append(entry.decode("utf-8", errors="ignore"))
            return values
        finally:
            destroy_fn(list_handle)

    def enum_all_entries(self, timeout_ms=5000):
        self._ensure_connected()
        list_handle = self._c_bindings.lib.slamtec_aurora_sdk_persistent_config_enum_all_entries(
            self._controller.session_handle, timeout_ms
        )
        return self._iter_string_list_handle(
            list_handle,
            self._c_bindings.lib.slamtec_aurora_sdk_config_entry_list_get_count,
            self._c_bindings.lib.slamtec_aurora_sdk_config_entry_list_get_entry,
            self._c_bindings.lib.slamtec_aurora_sdk_config_entry_list_destroy,
        )

    def get_config_data(self, filter_path, timeout_ms=5000):
        self._ensure_connected()
        config_data = ConfigData(c_bindings=self._c_bindings)
        try:
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_persistent_config_get_config(
                self._controller.session_handle,
                _as_bytes(filter_path),
                config_data.handle,
                timeout_ms,
            )
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to get config '{}' (error code: {})".format(filter_path, error_code))
            return config_data
        except Exception:
            config_data.close()
            raise

    def get_config(self, filter_path, timeout_ms=5000):
        config_data = self.get_config_data(filter_path, timeout_ms=timeout_ms)
        try:
            return config_data.dump_to_string()
        finally:
            config_data.close()

    def get_config_object(self, filter_path, timeout_ms=5000):
        return json.loads(self.get_config(filter_path, timeout_ms=timeout_ms))

    def set_config(self, filter_path, key, config, timeout_ms=5000):
        self._ensure_connected()

        temporary = None
        config_data = config
        if not isinstance(config, ConfigData):
            temporary = ConfigData.from_object(config, c_bindings=self._c_bindings)
            config_data = temporary

        try:
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_persistent_config_set_config(
                self._controller.session_handle,
                _as_bytes(filter_path),
                _as_bytes(key),
                config_data.handle,
                timeout_ms,
            )
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError("Failed to set config '{}' (error code: {})".format(filter_path, error_code))
        finally:
            if temporary is not None:
                temporary.close()

    def reset_config(self, filter_path, timeout_ms=5000):
        self._ensure_connected()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_persistent_config_reset_config(
            self._controller.session_handle, _as_bytes(filter_path), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to reset config '{}' (error code: {})".format(filter_path, error_code))

    def reset_all_config(self, timeout_ms=5000):
        self._ensure_connected()
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_persistent_config_reset_all_config(
            self._controller.session_handle, timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to reset all config entries (error code: {})".format(error_code))
