"""Exceptions from the Huawei Solar library."""

from typing import Any


class HuaweiSolarException(Exception):  # noqa: N818
    """Base class for Huawei Solar exceptions."""


class DeviceDetectionError(HuaweiSolarException):
    """Failed to detect the type of the connected device."""


class EncodeError(HuaweiSolarException):
    """Encoding failed."""


class TimeOfUsePeriodsException(HuaweiSolarException):
    """Validation of TOU periods failed."""


class PeakPeriodsValidationError(Exception):
    """Validation of Peak Periods failed."""


class ConnectionException(HuaweiSolarException):
    """Exception connecting to device."""


class ReadException(HuaweiSolarException):
    """Exception reading register from device."""

    def __init__(self, *args: Any, modbus_exception_code: int | None = None, **kwargs: Any) -> None:  # noqa: ANN401
        """Create ReadException."""
        super().__init__(*args, **kwargs)
        self.modbus_exception_code = modbus_exception_code


class DecodeError(ReadException):
    """Decoding failed."""


class UnexpectedResponseContent(HuaweiSolarException):
    """The response from the device contained unexpected content."""


class ConnectionInterruptedException(HuaweiSolarException):
    """Connection to the inverter was interrupted."""


class WriteException(HuaweiSolarException):
    """Exception writing register to device."""

    def __init__(self, *args: Any, modbus_exception_code: int | None = None, **kwargs: Any) -> None:  # noqa: ANN401
        """Create WriteException."""
        super().__init__(*args, **kwargs)
        self.modbus_exception_code = modbus_exception_code


class InvalidCredentials(HuaweiSolarException):
    """Logging in on the inverter failed."""


class UnsupportedDeviceException(HuaweiSolarException):
    """No bridge class is available for this device."""


class PermissionDeniedError(HuaweiSolarException):
    """The device refused the request because no login session is established.

    Huawei answers with the private Modbus exception code ``0x80`` for this.
    ``modbus_connection`` has no way to register a vendor exception code, so the
    code is recognised here and turned into this exception at the boundary.
    """
