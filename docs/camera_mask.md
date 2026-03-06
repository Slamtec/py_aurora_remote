# camera_mask

Camera mask management for Aurora SDK 2.1.1.

## Import

```python
from slamtec_aurora_sdk import camera_mask
```

## Classes

### CameraMaskManager

Manage static camera masks on the device.

#### Methods

**close**(self)

**is_static_mask_enabled**(self, timeout_ms)

**set_static_mask_enable**(self, enable, timeout_ms)

**get_static_camera_mask_image_id_list**(self, timeout_ms)

**get_static_camera_mask_image**(self, camera_index, timeout_ms)

**set_static_camera_mask_image**(self, camera_index, image, timeout_ms)

**remove_static_camera_mask_image**(self, camera_index, timeout_ms)

**refresh**(self, timeout_ms)

#### Special Methods

**__init__**(self, controller, c_bindings)

**__del__**(self)
