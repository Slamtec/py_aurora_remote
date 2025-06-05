"""
Exception classes for Aurora SDK Python bindings.
"""


class AuroraSDKError(Exception):
    """Base exception for Aurora SDK errors."""
    
    def __init__(self, message, error_code = -1):
        super().__init__(message)
        self.error_code = error_code


class ConnectionError(AuroraSDKError):
    """Exception raised when connection to Aurora device fails."""
    pass


class DataNotReadyError(AuroraSDKError):
    """Exception raised when requested data is not ready."""
    pass


class TimeoutError(AuroraSDKError):
    """Exception raised when operation times out."""
    pass


class InvalidArgumentError(AuroraSDKError):
    """Exception raised when invalid arguments are provided."""
    pass


class NotSupportedError(AuroraSDKError):
    """Exception raised when operation is not supported."""
    pass


class ConnectionLostError(AuroraSDKError):
    """Exception raised when connection to device is lost."""
    pass


def error_code_to_exception(error_code, message):
    """Convert error code to appropriate exception."""
    from .data_types import (
        ERRORCODE_OK, ERRORCODE_FAILED, ERRORCODE_NOT_READY,
        ERRORCODE_INVALID_ARGUMENT, ERRORCODE_TIMEOUT,
        ERRORCODE_NOT_SUPPORTED, ERRORCODE_CONNECTION_LOST
    )
    
    if error_code == ERRORCODE_OK:
        return None
    elif error_code == ERRORCODE_NOT_READY:
        return DataNotReadyError(message, error_code)
    elif error_code == ERRORCODE_INVALID_ARGUMENT:
        return InvalidArgumentError(message, error_code)
    elif error_code == ERRORCODE_TIMEOUT:
        return TimeoutError(message, error_code)
    elif error_code == ERRORCODE_NOT_SUPPORTED:
        return NotSupportedError(message, error_code)
    elif error_code == ERRORCODE_CONNECTION_LOST:
        return ConnectionLostError(message, error_code)
    else:
        return AuroraSDKError(message, error_code)