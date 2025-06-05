# controller

Aurora SDK Controller component.

Handles device connection, session management, and control operations.

## Import

```python
from slamtec_aurora_sdk import controller
```

## Classes

### Controller

Controller component for Aurora SDK.

Responsible for:
- Device discovery and connection management
- Session lifecycle (create, release)
- Device control operations (reset, reboot, etc.)
- Configuration management

#### Properties

**session_handle**

Get the session handle for use by other components.

#### Methods

**get_version_info**(self)

Get SDK version information.

Returns:
    dict containing version information

**create_session**(self)

Create SDK session.

Raises:
    AuroraSDKError: If session creation fails

**release_session**(self)

Release SDK session.

**discover_devices**(self, timeout)

Discover Aurora devices on the network.

Args:
    timeout: Discovery timeout in seconds
    
Returns:
    List of discovered device information dictionaries
    
Raises:
    AuroraSDKError: If discovery fails

**connect**(self, device_info, connection_string)

Connect to an Aurora device.

Args:
    device_info: Device info from discovery (preferred)
    connection_string: Direct connection string (fallback)
    
Raises:
    ConnectionError: If connection fails
    AuroraSDKError: If session not created or invalid parameters

**disconnect**(self)

Disconnect from current device.

**is_connected**(self)

Check if connected to a device.

Returns:
    bool: True if connected, False otherwise

**get_device_info**(self)

Get connected device information.

Returns:
    DeviceInfo object containing device details
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If failed to get device info

**enable_raw_data_subscription**(self, enable)

Enable/disable raw data subscription for better image quality.

Args:
    enable: True to enable, False to disable
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**reset_device**(self)

Reset the connected device.

Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If reset fails

**enable_map_data_syncing**(self, enable)

Enable/disable map data syncing.

Args:
    enable: True to enable, False to disable
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**require_mapping_mode**(self, timeout_ms)

Require device to enter mapping mode.

Args:
    timeout_ms: Timeout in milliseconds
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**resync_map_data**(self, invalidate_cache)

Force resync of map data.

Args:
    invalidate_cache: Whether to invalidate cache
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**set_enhanced_imaging_subscription**(self, enhanced_image_type, enable)

Set enhanced imaging subscription for specific image type.

Args:
    enhanced_image_type (int): Type of enhanced image (0: depth, 1: semantic segmentation)
    enable (bool): True to enable, False to disable
    
Returns:
    bool: True if successful, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**is_enhanced_imaging_subscribed**(self, enhanced_image_type)

Check if enhanced imaging is subscribed for specific image type.

Args:
    enhanced_image_type (int): Type of enhanced image (0: depth, 1: semantic segmentation)
    
Returns:
    bool: True if subscribed, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**require_semantic_segmentation_alternative_model**(self, use_alternative_model, timeout_ms)

Require semantic segmentation to use alternative model.

Args:
    use_alternative_model (bool): True to use alternative model, False for default
    timeout_ms (int): Timeout in milliseconds
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**require_relocalization**(self, timeout_ms)

Require the device to perform relocalization.

This method tells the Aurora device to perform relocalization to determine
its position within a previously built map. The device will use its current
sensor readings to match against the existing map.

Args:
    timeout_ms (int): Timeout in milliseconds (default: 5000)
    
Returns:
    bool: True if relocalization was successful, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If relocalization operation fails

**cancel_relocalization**(self)

Cancel an ongoing relocalization operation.

Returns:
    bool: True if cancellation was successful, False otherwise
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If cancellation operation fails

**require_map_reset**(self, timeout_ms)

Require the device to reset its map.

This will clear the current SLAM map and start mapping from scratch.

Args:
    timeout_ms (int): Timeout in milliseconds (default: 10000)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If map reset operation fails

**require_pure_localization_mode**(self, timeout_ms)

Require the device to enter pure localization mode.

In this mode, the device will not add new features to the map but will
only use existing map features for localization.

Args:
    timeout_ms (int): Timeout in milliseconds (default: 10000)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If mode switch operation fails

**is_device_connection_alive**(self)

Check if the device connection is alive and healthy.

Returns:
    bool: True if connection is alive, False otherwise
    
Raises:
    ConnectionError: If not connected to a device

**is_raw_data_subscribed**(self)

Check if raw data subscription is active.

Returns:
    bool: True if raw data is subscribed, False otherwise
    
Raises:
    ConnectionError: If not connected to a device

**set_low_rate_mode**(self, enable)

Enable/disable low rate mode for bandwidth management.

Args:
    enable (bool): True to enable low rate mode, False to disable
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**set_loop_closure**(self, enable, timeout_ms)

Enable/disable loop closure detection.

Args:
    enable (bool): True to enable loop closure, False to disable
    timeout_ms (int): Timeout in milliseconds (default: 5000)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If operation fails

**force_map_global_optimization**(self, timeout_ms)

Force global map optimization.

Args:
    timeout_ms (int): Timeout in milliseconds (default: 30000)
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If optimization fails

**send_custom_command**(self, command_id, data, timeout_ms)

Send custom command to device.

Args:
    command_id (int): Command ID (uint64)
    data (bytes or str, optional): Command data
    timeout_ms (int): Timeout in milliseconds (default: 5000)
    
Returns:
    bytes: Response data from device
    
Raises:
    ConnectionError: If not connected to a device
    AuroraSDKError: If command fails

#### Special Methods

**__init__**(self, c_bindings)

Initialize Controller component.
