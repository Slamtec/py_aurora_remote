"""
Aurora SDK DataRecorder component.

Handles sensor data recording for dataset generation and debugging.
"""

import ctypes
from .c_bindings import get_c_bindings
from .exceptions import AuroraSDKError, ConnectionError
from .data_types import (
    ERRORCODE_OK,
    DATARECORDER_TYPE_RAW_DATASET,
    DATARECORDER_TYPE_COLMAP_DATASET
)


class DataRecorder:
    """
    DataRecorder component for Aurora SDK.

    Handles recording of sensor data from Aurora device to disk:
    - RAW_DATASET: Record raw sensor data for offline processing
    - COLMAP_DATASET: Record COLMAP-compatible dataset for 3D reconstruction

    The recorder supports extensive configuration through options system:
    - Image quality settings (raw vs preview)
    - Stereo recording options
    - Image undistortion settings
    - Map point filtering
    - Output format options

    Typical usage:
        # Configure options before starting
        recorder.set_option_string(DATARECORDER_TYPE_COLMAP_DATASET, "image_quality", "raw")
        recorder.set_option_bool(DATARECORDER_TYPE_COLMAP_DATASET, "stereo_recording", True)

        # Start recording
        recorder.start_recording(DATARECORDER_TYPE_COLMAP_DATASET, "/path/to/output")

        # Query status
        if recorder.is_recording(DATARECORDER_TYPE_COLMAP_DATASET):
            kf_count = recorder.query_status_int(DATARECORDER_TYPE_COLMAP_DATASET, "kf_count")
            print(f"Recorded {kf_count} keyframes")

        # Stop recording
        recorder.stop_recording(DATARECORDER_TYPE_COLMAP_DATASET)
    """

    def __init__(self, controller, c_bindings=None):
        """
        Initialize DataRecorder component.

        Args:
            controller: Controller component instance
            c_bindings: Optional C bindings instance
        """
        self._controller = controller
        try:
            self._c_bindings = c_bindings or get_c_bindings()
        except Exception as e:
            # Store the error for later when methods are actually called
            self._c_bindings = None
            self._c_bindings_error = str(e)

    def _ensure_c_bindings(self):
        """Ensure C bindings are available or raise appropriate error."""
        if self._c_bindings is None:
            raise AuroraSDKError(f"Aurora SDK not available: {getattr(self, '_c_bindings_error', 'Unknown error')}")

    def _ensure_connected(self):
        """Ensure we're connected to a device."""
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")

    def start_recording(self, recorder_type, target_folder):
        """
        Start recording sensor data to specified folder.

        Before calling this, you should:
        1. Be connected to a device
        2. Enable background map data syncing (for COLMAP recording)
        3. Configure recorder options if needed

        Args:
            recorder_type (int): Type of recorder (DATARECORDER_TYPE_RAW_DATASET or
                               DATARECORDER_TYPE_COLMAP_DATASET)
            target_folder (str): Folder path where recorded data will be stored

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to start recording

        Example:
            sdk.controller.enable_map_data_syncing(True)
            sdk.data_recorder.set_option_string(DATARECORDER_TYPE_COLMAP_DATASET,
                                               "image_quality", "raw")
            sdk.data_recorder.start_recording(DATARECORDER_TYPE_COLMAP_DATASET,
                                             "/data/recording_001")
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        # Convert string to bytes for C API
        folder_bytes = target_folder.encode('utf-8') if isinstance(target_folder, str) else target_folder

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_start_recording(
            self._controller._session_handle,
            recorder_type,
            folder_bytes
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to start recording (error code: {result})")

    def stop_recording(self, recorder_type):
        """
        Stop an active recording session.

        Args:
            recorder_type (int): Type of recorder to stop

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to stop recording

        Example:
            sdk.data_recorder.stop_recording(DATARECORDER_TYPE_COLMAP_DATASET)
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_stop_recording(
            self._controller._session_handle,
            recorder_type
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to stop recording (error code: {result})")

    def is_recording(self, recorder_type):
        """
        Check if recorder is currently active.

        Args:
            recorder_type (int): Type of recorder to check

        Returns:
            bool: True if currently recording, False otherwise

        Raises:
            ConnectionError: If not connected to a device

        Example:
            if sdk.data_recorder.is_recording(DATARECORDER_TYPE_COLMAP_DATASET):
                print("Recording in progress...")
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_is_recording(
            self._controller._session_handle,
            recorder_type
        )

        return result != 0

    def set_option_string(self, recorder_type, key, value):
        """
        Set a string option for recorder configuration.

        Common string options:
        - "image_quality": "raw" or "preview" (default: "raw")
        - "file_format": "binary", "text", or "all" (default: "binary", COLMAP only)

        Args:
            recorder_type (int): Type of recorder
            key (str): Option key name
            value (str): String value to set

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to set option

        Example:
            sdk.data_recorder.set_option_string(DATARECORDER_TYPE_COLMAP_DATASET,
                                               "image_quality", "raw")
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        # Convert strings to bytes for C API
        key_bytes = key.encode('utf-8') if isinstance(key, str) else key
        value_bytes = value.encode('utf-8') if isinstance(value, str) else value

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_set_option_string(
            self._controller._session_handle,
            recorder_type,
            key_bytes,
            value_bytes
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to set option '{key}' (error code: {result})")

    def set_option_int(self, recorder_type, key, value):
        """
        Set an integer option for recorder configuration.

        Args:
            recorder_type (int): Type of recorder
            key (str): Option key name
            value (int): Integer value to set

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to set option

        Example:
            sdk.data_recorder.set_option_int(DATARECORDER_TYPE_RAW_DATASET,
                                           "frame_skip", 2)
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        key_bytes = key.encode('utf-8') if isinstance(key, str) else key

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_set_option_int32(
            self._controller._session_handle,
            recorder_type,
            key_bytes,
            int(value)
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to set option '{key}' (error code: {result})")

    def set_option_float(self, recorder_type, key, value):
        """
        Set a float option for recorder configuration.

        Args:
            recorder_type (int): Type of recorder
            key (str): Option key name
            value (float): Float value to set

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to set option

        Example:
            sdk.data_recorder.set_option_float(DATARECORDER_TYPE_RAW_DATASET,
                                              "target_fps", 30.0)
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        key_bytes = key.encode('utf-8') if isinstance(key, str) else key

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_set_option_float64(
            self._controller._session_handle,
            recorder_type,
            key_bytes,
            float(value)
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to set option '{key}' (error code: {result})")

    def set_option_bool(self, recorder_type, key, value):
        """
        Set a boolean option for recorder configuration.

        Common boolean options for COLMAP recorder:
        - "stereo_recording": Record both left and right images (default: False)
        - "undistort": Apply undistortion to images (default: True)
        - "undistort_force_focal_center": Force focal center to image center (default: True)
        - "keep_unused_map_points": Keep unused map points in output (default: False)
        - "multi_mapper": Store data in sparse/n/ folder (default: False)

        Args:
            recorder_type (int): Type of recorder
            key (str): Option key name
            value (bool): Boolean value to set

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to set option

        Example:
            sdk.data_recorder.set_option_bool(DATARECORDER_TYPE_COLMAP_DATASET,
                                             "stereo_recording", True)
            sdk.data_recorder.set_option_bool(DATARECORDER_TYPE_COLMAP_DATASET,
                                             "undistort", True)
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        key_bytes = key.encode('utf-8') if isinstance(key, str) else key

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_set_option_bool(
            self._controller._session_handle,
            recorder_type,
            key_bytes,
            1 if value else 0
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to set option '{key}' (error code: {result})")

    def reset_options(self, recorder_type):
        """
        Reset all recorder options to defaults.

        Args:
            recorder_type (int): Type of recorder to reset

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to reset options

        Example:
            sdk.data_recorder.reset_options(DATARECORDER_TYPE_COLMAP_DATASET)
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_set_option_reset(
            self._controller._session_handle,
            recorder_type
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to reset options (error code: {result})")

    def query_status_int(self, recorder_type, key, use_cached=False):
        """
        Query an integer status value from recorder.

        Common status keys:
        - "kf_count": Number of keyframes recorded
        - "frame_count": Number of frames recorded

        Args:
            recorder_type (int): Type of recorder
            key (str): Status key to query
            use_cached (bool): Use cached value instead of fresh query

        Returns:
            int: Status value

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to query status

        Example:
            kf_count = sdk.data_recorder.query_status_int(
                DATARECORDER_TYPE_COLMAP_DATASET, "kf_count")
            print(f"Recorded {kf_count} keyframes")
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        key_bytes = key.encode('utf-8') if isinstance(key, str) else key
        value_out = ctypes.c_int64()

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_query_status_int64(
            self._controller._session_handle,
            recorder_type,
            key_bytes,
            ctypes.byref(value_out),
            1 if use_cached else 0
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to query status '{key}' (error code: {result})")

        return value_out.value

    def query_status_float(self, recorder_type, key, use_cached=False):
        """
        Query a float status value from recorder.

        Args:
            recorder_type (int): Type of recorder
            key (str): Status key to query
            use_cached (bool): Use cached value instead of fresh query

        Returns:
            float: Status value

        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to query status

        Example:
            progress = sdk.data_recorder.query_status_float(
                DATARECORDER_TYPE_COLMAP_DATASET, "progress")
            print(f"Progress: {progress:.1f}%")
        """
        self._ensure_connected()
        self._ensure_c_bindings()

        key_bytes = key.encode('utf-8') if isinstance(key, str) else key
        value_out = ctypes.c_double()

        result = self._c_bindings.lib.slamtec_aurora_sdk_datarecorder_query_status_float64(
            self._controller._session_handle,
            recorder_type,
            key_bytes,
            ctypes.byref(value_out),
            1 if use_cached else 0
        )

        if result != ERRORCODE_OK:
            raise AuroraSDKError(f"Failed to query status '{key}' (error code: {result})")

        return value_out.value


__all__ = ['DataRecorder']
