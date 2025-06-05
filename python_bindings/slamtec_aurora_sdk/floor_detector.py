#!/usr/bin/env python3

"""
Floor Detector module for Aurora SDK.

Provides access to auto floor detection functionality including:
- Floor detection histogram
- Floor descriptions and current floor
- Floor detection status
"""

from .exceptions import AuroraSDKError, ConnectionError


class FloorDetector:
    """
    Floor detector for Aurora SDK.
    
    Provides access to auto floor detection functionality that helps
    with multi-floor environments.
    """
    
    def __init__(self, controller, c_bindings=None):
        """
        Initialize floor detector.
        
        Args:
            controller: Aurora controller instance
            c_bindings: C bindings instance (optional)
        """
        self._controller = controller
        self._c_bindings = c_bindings
        
    def _ensure_c_bindings(self):
        """Ensure C bindings are available."""
        if self._c_bindings is None:
            from .c_bindings import get_c_bindings
            self._c_bindings = get_c_bindings()
            
    def _ensure_connected(self):
        """Ensure device is connected."""
        if not self._controller.is_connected():
            raise ConnectionError("Not connected to any device")
    
    def get_detection_histogram(self):
        """
        Get floor detection histogram.
        
        Returns:
            tuple: (histogram_info, histogram_data)
                - histogram_info: FloorDetectionHistogramInfo with bin info
                - histogram_data: list of float values for each bin
                
        Raises:
            ConnectionError: If not connected to device
            AuroraSDKError: If failed to get histogram data
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_floor_detection_histogram(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError("Failed to get floor detection histogram: {}".format(e))
    
    def get_all_detection_info(self):
        """
        Get all floor detection descriptions and current floor ID.
        
        Returns:
            tuple: (floor_descriptions, current_floor_id)
                - floor_descriptions: list of FloorDetectionDesc objects
                - current_floor_id: int, ID of current floor
                
        Raises:
            ConnectionError: If not connected to device
            AuroraSDKError: If failed to get floor info
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_all_floor_detection_info(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError("Failed to get all floor detection info: {}".format(e))
    
    def get_current_detection_desc(self):
        """
        Get current floor detection description.
        
        Returns:
            FloorDetectionDesc: Description of current floor
            
        Raises:
            ConnectionError: If not connected to device
            AuroraSDKError: If failed to get floor description
        """
        self._ensure_connected()
        self._ensure_c_bindings()
        
        try:
            return self._c_bindings.get_current_floor_detection_desc(self._controller.session_handle)
        except Exception as e:
            raise AuroraSDKError("Failed to get current floor detection desc: {}".format(e))