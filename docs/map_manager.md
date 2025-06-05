# map_manager

Aurora SDK MapManager component.

Handles VSLAM map storage operations (save/load) using async sessions.

## Import

```python
from slamtec_aurora_sdk import map_manager
```

## Classes

### MapManager

MapManager component for Aurora SDK.

Handles VSLAM map storage operations with async sessions:
- Download maps from Aurora device to local files
- Upload maps from local files to Aurora device  
- Monitor progress of map storage operations
- Handle session status and error conditions

The map storage operations are asynchronous - they run in the background
while you can query progress and wait for completion.

#### Methods

**start_download_session**(self, map_file_path, callback, user_data)

Start downloading a map from the Aurora device to local file.

This operation runs asynchronously. Use is_session_active() and 
query_session_status() to monitor progress, or wait_for_completion()
to block until finished.

Args:
    map_file_path (str): Local file path where map will be saved
    callback (callable, optional): Callback function called when complete.
                                 Signature: callback(user_data, is_ok)
    user_data: User data passed to callback
    
Returns:
    bool: True if session started successfully, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to start download session

**start_upload_session**(self, map_file_path, callback, user_data)

Start uploading a map from local file to the Aurora device.

This operation runs asynchronously. Use is_session_active() and 
query_session_status() to monitor progress, or wait_for_completion()
to block until finished.

Args:
    map_file_path (str): Local file path of map to upload
    callback (callable, optional): Callback function called when complete.
                                 Signature: callback(user_data, is_ok)
    user_data: User data passed to callback
    
Returns:
    bool: True if session started successfully, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to start upload session

**abort_session**(self)

Abort the current map storage session.

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If C bindings not available

**is_session_active**(self)

Check if a map storage session is currently active.

Returns:
    bool: True if session is active, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If C bindings not available

**query_session_status**(self)

Query the progress and status of the current map storage session.

Returns:
    MapStorageSessionStatus: Status object with progress and flags
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to query status

**wait_for_completion**(self, timeout_seconds, progress_callback)

Wait for the current map storage session to complete.

This method blocks until the session finishes, is aborted, or times out.

Args:
    timeout_seconds (float, optional): Maximum time to wait in seconds.
                                     None means wait indefinitely.
    progress_callback (callable, optional): Callback called with progress updates.
                                           Signature: callback(status)
    
Returns:
    bool: True if session completed successfully, False if failed/aborted
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If session monitoring failed
    TimeoutError: If timeout_seconds exceeded

**download_map**(self, map_file_path, timeout_seconds, progress_callback)

Download a map from Aurora device to local file (blocking).

This is a convenience method that starts a download session and waits
for completion.

Args:
    map_file_path (str): Local file path where map will be saved
    timeout_seconds (float, optional): Maximum time to wait
    progress_callback (callable, optional): Progress callback function
    
Returns:
    bool: True if download successful, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If download failed
    TimeoutError: If timeout exceeded

**upload_map**(self, map_file_path, timeout_seconds, progress_callback)

Upload a map from local file to Aurora device (blocking).

This is a convenience method that starts an upload session and waits
for completion.

Args:
    map_file_path (str): Local file path of map to upload
    timeout_seconds (float, optional): Maximum time to wait
    progress_callback (callable, optional): Progress callback function
    
Returns:
    bool: True if upload successful, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If upload failed
    TimeoutError: If timeout exceeded

#### Special Methods

**__init__**(self, controller, c_bindings)

Initialize MapManager component.

Args:
    controller: Controller component instance
    c_bindings: Optional C bindings instance

## Functions

**internal_callback**(user_data_ptr, is_ok)

**internal_callback**(user_data_ptr, is_ok)
