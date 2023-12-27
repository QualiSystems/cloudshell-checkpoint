from __future__ import annotations


class BaseCheckpointError(Exception):
    """Base BaseCheckpointError Error."""


class NotImplementedCheckpointError(NotImplementedError):
    """CheckPoint Not Implemented Error."""


class NotSupportedCheckpointError(BaseCheckpointError):
    """Not supported by CheckPoint Gaia."""


class ShutdownOkCheckpointError(BaseCheckpointError):
    """Error means that device successfully went down."""


class SnmpCheckpointError(BaseCheckpointError):
    """Base SNMP CheckPoint Error."""
