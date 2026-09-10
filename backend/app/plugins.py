from importlib import import_module

from backend.app.errors import AppError


def load_plugin(path: str, role: str):
    if not path:
        raise AppError(503, "integration_not_configured", f"Configure GRAPHTRACE_{role} first; see docs/INTEGRATION.md.")
    module_name, separator, attribute = path.partition(":")
    if not separator or not module_name or not attribute:
        raise AppError(503, "integration_invalid", f"GRAPHTRACE_{role} must be module:function.")
    try:
        plugin = getattr(import_module(module_name), attribute)
    except (ImportError, AttributeError) as exc:
        raise AppError(503, "integration_unavailable", f"Could not load the configured {role.lower()}.") from exc
    if not callable(plugin):
        raise AppError(503, "integration_invalid", f"Configured {role.lower()} must be callable.")
    return plugin
