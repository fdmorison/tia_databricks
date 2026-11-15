"""
tia_databricks public API.

This module defines the public, stable interface of the Databricks provider
used by Tiozin pipelines.

Only the symbols exported here are considered part of the supported API.
All other modules and classes inside this package are internal implementation
details and may change without notice.
"""

from contextlib import suppress

__all__ = []

with suppress(ImportError):
    from .runners.connect_runner import DatabricksConnectRunner

    __all__ += ["DatabricksConnectRunner"]
