# exceptions

Exception classes for Aurora SDK Python bindings.

## Import

```python
from slamtec_aurora_sdk import exceptions
```

## Classes

### AuroraSDKError

**Inherits from:** Exception

Base exception for Aurora SDK errors.

#### Special Methods

**__init__**(self, message, error_code)

### ConnectionError

**Inherits from:** AuroraSDKError

Exception raised when connection to Aurora device fails.

### DataNotReadyError

**Inherits from:** AuroraSDKError

Exception raised when requested data is not ready.

### TimeoutError

**Inherits from:** AuroraSDKError

Exception raised when operation times out.

### InvalidArgumentError

**Inherits from:** AuroraSDKError

Exception raised when invalid arguments are provided.

### NotSupportedError

**Inherits from:** AuroraSDKError

Exception raised when operation is not supported.

### ConnectionLostError

**Inherits from:** AuroraSDKError

Exception raised when connection to device is lost.

## Functions

**error_code_to_exception**(error_code, message)

Convert error code to appropriate exception.
