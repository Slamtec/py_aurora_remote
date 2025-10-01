# data_recorder

Aurora SDK DataRecorder component.

Handles sensor data recording for dataset generation and debugging.

## Import

```python
from slamtec_aurora_sdk import data_recorder
```

## Classes

### DataRecorder

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

#### Methods

**start_recording**(self, recorder_type, target_folder)

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

**stop_recording**(self, recorder_type)

Stop an active recording session.

Args:
    recorder_type (int): Type of recorder to stop

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to stop recording

Example:
    sdk.data_recorder.stop_recording(DATARECORDER_TYPE_COLMAP_DATASET)

**is_recording**(self, recorder_type)

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

**set_option_string**(self, recorder_type, key, value)

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

**set_option_int**(self, recorder_type, key, value)

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

**set_option_float**(self, recorder_type, key, value)

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

**set_option_bool**(self, recorder_type, key, value)

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

**reset_options**(self, recorder_type)

Reset all recorder options to defaults.

Args:
    recorder_type (int): Type of recorder to reset

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to reset options

Example:
    sdk.data_recorder.reset_options(DATARECORDER_TYPE_COLMAP_DATASET)

**query_status_int**(self, recorder_type, key, use_cached)

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

**query_status_float**(self, recorder_type, key, use_cached)

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

#### Special Methods

**__init__**(self, controller, c_bindings)

Initialize DataRecorder component.

Args:
    controller: Controller component instance
    c_bindings: Optional C bindings instance
