# floor_detector

Floor Detector module for Aurora SDK.

Provides access to auto floor detection functionality including:
- Floor detection histogram
- Floor descriptions and current floor
- Floor detection status

## Import

```python
from slamtec_aurora_sdk import floor_detector
```

## Classes

### FloorDetector

Floor detector for Aurora SDK.

Provides access to auto floor detection functionality that helps
with multi-floor environments.

#### Methods

**get_detection_histogram**(self)

Get floor detection histogram.

Returns:
    tuple: (histogram_info, histogram_data)
        - histogram_info: FloorDetectionHistogramInfo with bin info
        - histogram_data: list of float values for each bin
        
Raises:
    ConnectionError: If not connected to device
    AuroraSDKError: If failed to get histogram data

**get_all_detection_info**(self)

Get all floor detection descriptions and current floor ID.

Returns:
    tuple: (floor_descriptions, current_floor_id)
        - floor_descriptions: list of FloorDetectionDesc objects
        - current_floor_id: int, ID of current floor
        
Raises:
    ConnectionError: If not connected to device
    AuroraSDKError: If failed to get floor info

**get_current_detection_desc**(self)

Get current floor detection description.

Returns:
    FloorDetectionDesc: Description of current floor
    
Raises:
    ConnectionError: If not connected to device
    AuroraSDKError: If failed to get floor description

#### Special Methods

**__init__**(self, controller, c_bindings)

Initialize floor detector.

Args:
    controller: Aurora controller instance
    c_bindings: C bindings instance (optional)
