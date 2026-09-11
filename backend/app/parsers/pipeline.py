"""
DEPRECATED SHIM — DO NOT USE DIRECTLY
======================================
This file is a backward-compatibility re-export shim.

The canonical location of the M1 → M3 parser bridge is now:
    backend/artifact_intelligence/pipeline.py

Update your imports to:
    from backend.artifact_intelligence.pipeline import parse_project
"""
import warnings

warnings.warn(
    "backend.app.parsers.pipeline is deprecated. "
    "Import from backend.artifact_intelligence.pipeline instead.",
    DeprecationWarning,
    stacklevel=2,
)

from backend.artifact_intelligence.pipeline import parse_project  # noqa: F401, E402

__all__ = ["parse_project"]
