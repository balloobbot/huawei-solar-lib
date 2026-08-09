"""Register components for every Huawei device type this library supports."""

from . import emma, scharger, sdongle, shared, smartlogger, sun2000
from .base import HuaweiComponent

__all__ = [
    "HuaweiComponent",
    "emma",
    "scharger",
    "sdongle",
    "shared",
    "smartlogger",
    "sun2000",
]
