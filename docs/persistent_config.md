# persistent_config

Persistent configuration management for Aurora SDK 2.1.1.

## Import

```python
from slamtec_aurora_sdk import persistent_config
```

## Classes

### ConfigData

JSON-backed config data wrapper for persistent configuration APIs.

#### Properties

**handle**

#### Methods

**is_valid**(self)

**close**(self)

**load_from_string**(self, json_string)

**dump_to_string**(self)

**load_from_file**(self, file_path)

**save_to_file**(self, file_path)

**to_object**(self)

**from_string**(cls, json_string, c_bindings)

**from_object**(cls, value, c_bindings)

#### Special Methods

**__init__**(self, c_bindings, handle, owned)

**__del__**(self)

### PersistentConfigManager

Manager for device persistent configuration entries.

#### Methods

**enum_all_entries**(self, timeout_ms)

**get_config_data**(self, filter_path, timeout_ms)

**get_config**(self, filter_path, timeout_ms)

**get_config_object**(self, filter_path, timeout_ms)

**set_config**(self, filter_path, key, config, timeout_ms)

**reset_config**(self, filter_path, timeout_ms)

**reset_all_config**(self, timeout_ms)

#### Special Methods

**__init__**(self, controller, c_bindings)

## Functions

**_as_bytes**(value)
