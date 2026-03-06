# dashcam_recorder

Dashcam recorder management for Aurora SDK 2.1.1.

## Import

```python
from slamtec_aurora_sdk import dashcam_recorder
```

## Classes

### DashcamStorageInfo

Wrapper around a dashcam storage info handle.

#### Properties

**path**

**sessions**

#### Methods

**is_valid**(self)

**close**(self)

**has_storage_status**(self)

**get_storage_status**(self)

**get_session_count**(self)

**get_session**(self, index)

**has_current_session**(self)

**get_current_session**(self)

#### Special Methods

**__init__**(self, handle, c_bindings)

**__del__**(self)

### DashcamRecorderManager

Monitor and control the device dashcam recorder.

#### Methods

**get_status**(self, timeout_ms)

**get_storage_info**(self, timeout_ms)

**set_enable**(self, enable, timeout_ms)

**set_size_limit**(self, size_limit_gb, timeout_ms)

**invalidate_sessions**(self, timeout_ms)

#### Special Methods

**__init__**(self, controller, c_bindings)
