# timesync

Standalone time synchronization client for Aurora SDK 2.1.1.

## Import

```python
from slamtec_aurora_sdk import timesync
```

## Classes

### TimeSyncClient

Standalone Aurora time synchronization client.

#### Methods

**get_default_options**(cls, c_bindings)

**close**(self)

**connect**(self, server_address, server_port)

**set_options**(self, options)

**initialize**(self)

**is_synchronized**(self)

**is_running**(self)

**translate_timestamp**(self, aurora_timestamp_ns)

**get_quality**(self)

**get_current_server_timestamp**(self, timeout_ms)

**stop**(self)

**get_wallclock_offset**(self, timeout_ms)

**sync_server_wallclock**(self, timeout_ms)

**evaluate_wallclock_accuracy**(self, timeout_ms)

#### Special Methods

**__init__**(self, domain, c_bindings)

**__enter__**(self)

**__exit__**(self, exc_type, exc_val, exc_tb)

**__del__**(self)

## Functions

**_as_bytes**(value)
