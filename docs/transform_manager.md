# transform_manager

Transform manager for Aurora SDK 2.1.1.

## Import

```python
from slamtec_aurora_sdk import transform_manager
```

## Classes

### TransformManager

Manage configurable device transforms.

#### Methods

**close**(self)

**get_all_transform_names**(self, timeout_ms)

**get_transform**(self, name, timeout_ms)

**set_transform**(self, name, pose, timeout_ms)

**reset_transform**(self, name, timeout_ms)

**has_transform**(self, name, timeout_ms)

**refresh**(self, timeout_ms)

#### Special Methods

**__init__**(self, controller, c_bindings)

**__del__**(self)

## Functions

**_as_bytes**(value)

**_coerce_pose_se3**(pose)
