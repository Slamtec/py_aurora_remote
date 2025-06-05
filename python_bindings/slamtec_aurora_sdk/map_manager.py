"""
Aurora SDK MapManager component.

Handles VSLAM map storage operations (save/load) using async sessions.
"""

import ctypes
import threading
import time
from .c_bindings import get_c_bindings
from .exceptions import AuroraSDKError, ConnectionError
from .data_types import (
    ERRORCODE_OK,
    MapStorageSessionStatus,
    MapStorageSessionResultCallback,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_UPLOAD,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_DOWNLOAD,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FINISHED,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_WORKING,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_IDLE,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_FAILED,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_ABORTED,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_REJECTED,
    SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_STATUS_TIMEOUT
)


class MapManager:
    """
    MapManager component for Aurora SDK.
    
    Handles VSLAM map storage operations with async sessions:
    - Download maps from Aurora device to local files
    - Upload maps from local files to Aurora device  
    - Monitor progress of map storage operations
    - Handle session status and error conditions
    
    The map storage operations are asynchronous - they run in the background
    while you can query progress and wait for completion.
    """
    
    def __init__(self, controller, c_bindings=None):
        """
        Initialize MapManager component.
        
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
        
        # Session management
        self._session_result = None
        self._session_callback = None
        self._result_lock = threading.Lock()
    
    def _ensure_c_bindings(self):
        """Ensure C bindings are available or raise appropriate error."""
        if self._c_bindings is None:
            raise AuroraSDKError(f"Aurora SDK not available: {getattr(self, '_c_bindings_error', 'Unknown error')}")
    
    def _ensure_connected(self):
        """Ensure we're connected to a device."""
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")
    
    def _session_result_callback(self, user_data, is_ok):
        """Internal callback for session completion."""
        with self._result_lock:
            self._session_result = bool(is_ok)
    
    def start_download_session(self, map_file_path, callback=None, user_data=None):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        # Reset session state
        with self._result_lock:
            self._session_result = None
        
        # Set up callback - always use internal callback for completion tracking
        def internal_callback(user_data_ptr, is_ok):
            # Call internal callback
            self._session_result_callback(user_data_ptr, is_ok)
            # Call user callback if provided
            if callback is not None:
                try:
                    callback(user_data, is_ok)
                except Exception:
                    pass  # Don't let user callback errors break the internal tracking
        
        callback_func = MapStorageSessionResultCallback(internal_callback)
        callback_user_data = None
        
        self._session_callback = callback_func  # Keep reference to prevent GC
        
        try:
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_mapmanager_start_storage_session(
                self._controller.session_handle,
                map_file_path.encode('utf-8'),
                SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_DOWNLOAD,
                callback_func,
                callback_user_data
            )
            
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError(f"Failed to start download session, error code: {error_code}")
            
            return True
            
        except Exception as e:
            raise AuroraSDKError(f"Failed to start download session: {e}")
    
    def start_upload_session(self, map_file_path, callback=None, user_data=None):
        """
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
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        # Reset session state
        with self._result_lock:
            self._session_result = None
        
        # Set up callback - always use internal callback for completion tracking
        def internal_callback(user_data_ptr, is_ok):
            # Call internal callback
            self._session_result_callback(user_data_ptr, is_ok)
            # Call user callback if provided
            if callback is not None:
                try:
                    callback(user_data, is_ok)
                except Exception:
                    pass  # Don't let user callback errors break the internal tracking
        
        callback_func = MapStorageSessionResultCallback(internal_callback)
        callback_user_data = None
        
        self._session_callback = callback_func  # Keep reference to prevent GC
        
        try:
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_mapmanager_start_storage_session(
                self._controller.session_handle,
                map_file_path.encode('utf-8'),
                SLAMTEC_AURORA_SDK_MAPSTORAGE_SESSION_TYPE_UPLOAD,
                callback_func,
                callback_user_data
            )
            
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError(f"Failed to start upload session, error code: {error_code}")
            
            return True
            
        except Exception as e:
            raise AuroraSDKError(f"Failed to start upload session: {e}")
    
    def abort_session(self):
        """
        Abort the current map storage session.
        
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If C bindings not available
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            self._c_bindings.lib.slamtec_aurora_sdk_mapmanager_abort_session(
                self._controller.session_handle
            )
        except Exception as e:
            raise AuroraSDKError(f"Failed to abort session: {e}")
    
    def is_session_active(self):
        """
        Check if a map storage session is currently active.
        
        Returns:
            bool: True if session is active, False otherwise
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If C bindings not available
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            result = self._c_bindings.lib.slamtec_aurora_sdk_mapmanager_is_storage_session_active(
                self._controller.session_handle
            )
            return result != 0
        except Exception as e:
            raise AuroraSDKError(f"Failed to check session status: {e}")
    
    def query_session_status(self):
        """
        Query the progress and status of the current map storage session.
        
        Returns:
            MapStorageSessionStatus: Status object with progress and flags
            
        Raises:
            ConnectionError: If not connected to a device
            AuroraSDKError: If failed to query status
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            status = MapStorageSessionStatus()
            error_code = self._c_bindings.lib.slamtec_aurora_sdk_mapmanager_query_storage_status(
                self._controller.session_handle,
                ctypes.byref(status)
            )
            
            if error_code != ERRORCODE_OK:
                raise AuroraSDKError(f"Failed to query session status, error code: {error_code}")
            
            return status
            
        except Exception as e:
            raise AuroraSDKError(f"Failed to query session status: {e}")
    
    def wait_for_completion(self, timeout_seconds=None, progress_callback=None):
        """
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
        """
        start_time = time.time()
        
        while self.is_session_active():
            # Check timeout
            if timeout_seconds is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout_seconds:
                    raise TimeoutError(f"Map storage session timed out after {timeout_seconds} seconds")
            
            # Get status and call progress callback
            try:
                status = self.query_session_status()
                if progress_callback:
                    progress_callback(status)
            except Exception as e:
                raise AuroraSDKError(f"Failed to monitor session progress: {e}")
            
            # Sleep briefly before next check
            time.sleep(0.5)
        
        # Session is no longer active, get final result
        with self._result_lock:
            result = self._session_result
        
        if result is None:
            # Try to get final status to determine result
            try:
                final_status = self.query_session_status()
                result = final_status.is_finished()
                # Update our internal result based on status
                if result is not None:
                    with self._result_lock:
                        self._session_result = result
            except:
                # If we can't get status, assume failure
                result = False
        
        return result
    
    def download_map(self, map_file_path, timeout_seconds=None, progress_callback=None):
        """
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
        """
        if not self.start_download_session(map_file_path):
            return False
        
        return self.wait_for_completion(timeout_seconds, progress_callback)
    
    def upload_map(self, map_file_path, timeout_seconds=None, progress_callback=None):
        """
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
        """
        if not self.start_upload_session(map_file_path):
            return False
        
        return self.wait_for_completion(timeout_seconds, progress_callback)
    