# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/camera_mask.py
#  *
#  */
"""
Camera mask management for Aurora SDK 2.1.1.
"""

import ctypes

from .c_bindings import get_c_bindings
from .data_types import CameraMaskImageBuffer, ERRORCODE_INSUFFICIENT_BUFFER, ERRORCODE_OK, ImageDesc, ImageFrame
from .exceptions import AuroraSDKError, ConnectionError

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency
    np = None


class CameraMaskManager:
    """Manage static camera masks on the device."""

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
            self._handle = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_create(
                self._controller.session_handle
            )
            if not self._handle:
                raise AuroraSDKError("Failed to create camera mask manager")

    def close(self):
        if self._handle:
            self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_destroy(self._handle)
            self._handle = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def is_static_mask_enabled(self, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        result = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_is_static_mask_enabled(
            self._handle, timeout_ms
        )
        if result < 0:
            raise AuroraSDKError("Failed to query static mask state")
        return bool(result)

    def set_static_mask_enable(self, enable, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_set_static_mask_enable(
            self._handle, int(enable), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to set static mask state (error code: {})".format(error_code))

    def get_static_camera_mask_image_id_list(self, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        count = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_get_static_camera_mask_image_id_count(
            self._handle, timeout_ms
        )
        if count < 0:
            raise AuroraSDKError("Failed to query camera mask image indices")
        if count == 0:
            return []

        buffer = (ctypes.c_int * count)()
        actual_count = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_get_static_camera_mask_image_indices(
            self._handle, buffer, count, timeout_ms
        )
        if actual_count < 0:
            raise AuroraSDKError("Failed to read camera mask image indices")
        return [int(buffer[index]) for index in range(actual_count)]

    def get_static_camera_mask_image(self, camera_index, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        image_desc = ImageDesc()
        image_buffer = CameraMaskImageBuffer()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_get_static_camera_mask_image(
            self._handle, camera_index, ctypes.byref(image_desc), ctypes.byref(image_buffer), timeout_ms
        )

        if error_code != ERRORCODE_INSUFFICIENT_BUFFER:
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError(
                    "Failed to query camera mask image {} (error code: {})".format(camera_index, error_code)
                )
            return ImageFrame.from_c_desc(image_desc, data=None)

        buffer_size = int(image_desc.data_size or image_buffer.image_data_size)
        if buffer_size <= 0:
            raise AuroraSDKError("Camera mask image {} returned an empty buffer".format(camera_index))

        raw_buffer = (ctypes.c_uint8 * buffer_size)()
        image_buffer.image_data = ctypes.cast(raw_buffer, ctypes.c_void_p)
        image_buffer.image_data_size = buffer_size

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_get_static_camera_mask_image(
            self._handle, camera_index, ctypes.byref(image_desc), ctypes.byref(image_buffer), timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError(
                "Failed to get camera mask image {} (error code: {})".format(camera_index, error_code)
            )

        return ImageFrame.from_c_desc(image_desc, data=bytes(raw_buffer[: image_desc.data_size]))

    def set_static_camera_mask_image(self, camera_index, image, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        width, height, stride, payload = self._coerce_image_payload(image)

        image_desc = ImageDesc()
        image_desc.width = width
        image_desc.height = height
        image_desc.stride = stride
        image_desc.format = 0
        image_desc.data_size = len(payload)

        payload_buffer = ctypes.create_string_buffer(payload)
        error_code = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_set_static_camera_mask_image(
            self._handle,
            camera_index,
            ctypes.byref(image_desc),
            ctypes.cast(payload_buffer, ctypes.c_void_p),
            timeout_ms,
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError(
                "Failed to set camera mask image {} (error code: {})".format(camera_index, error_code)
            )

    def remove_static_camera_mask_image(self, camera_index, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_remove_static_camera_mask_image(
            self._handle, camera_index, timeout_ms
        )
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError(
                "Failed to remove camera mask image {} (error code: {})".format(camera_index, error_code)
            )

    def refresh(self, timeout_ms=5000):
        self._ensure_connected()
        self._ensure_handle()

        error_code = self._c_bindings.lib.slamtec_aurora_sdk_camera_mask_refresh(self._handle, timeout_ms)
        if error_code != ERRORCODE_OK:
            raise AuroraSDKError("Failed to refresh camera mask manager (error code: {})".format(error_code))

    def _coerce_image_payload(self, image):
        if isinstance(image, ImageFrame):
            if image.pixel_format != 0:
                raise AuroraSDKError("Camera mask ImageFrame must be grayscale")
            if not image.data:
                raise AuroraSDKError("Camera mask ImageFrame has no payload")

            stride = image.stride or image.width
            return image.width, image.height, stride, bytes(image.data)

        if np is None:
            raise AuroraSDKError("NumPy is required for non-ImageFrame camera mask uploads")

        array = np.asarray(image)
        if array.ndim == 3 and array.shape[2] == 1:
            array = array[:, :, 0]
        if array.ndim != 2:
            raise AuroraSDKError("Camera mask image must be a 2D uint8 array")

        contiguous = np.ascontiguousarray(array, dtype=np.uint8)
        height, width = contiguous.shape
        stride = int(contiguous.strides[0])
        return width, height, stride, contiguous.tobytes(order="C")
