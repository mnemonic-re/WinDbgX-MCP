"""Dynamic Custom Hook Loader for WinDbgMCP.

Allows users to load external Python hook scripts with process_input(text, context)
and/or process_output(text, context) callbacks to dynamically transform tool arguments
and debug output at runtime.
"""

from __future__ import annotations

import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

ResolvedCallback = Callable[[str, Dict[str, Any]], Optional[str]]


class CustomHook:
    """Encapsulates loaded user hook script callbacks."""

    def __init__(
        self,
        path: Path,
        process_input_callback: Optional[ResolvedCallback] = None,
        process_output_callback: Optional[ResolvedCallback] = None,
    ):
        self.path = path
        self.process_input_callback = process_input_callback
        self.process_output_callback = process_output_callback

    def apply_input_hook(self, text: str, tool_name: str = "") -> str:
        """Apply custom input transformation callback if defined."""
        if not self.process_input_callback:
            return text
        try:
            res = self.process_input_callback(text, {"hook": "input", "tool_name": tool_name})
            return res if isinstance(res, str) else text
        except Exception as e:
            logger.warning("Error executing custom input hook: %s", e)
            return text

    def apply_output_hook(self, text: str, tool_name: str = "") -> str:
        """Apply custom output transformation callback if defined."""
        if not self.process_output_callback:
            return text
        try:
            res = self.process_output_callback(text, {"hook": "output", "tool_name": tool_name})
            return res if isinstance(res, str) else text
        except Exception as e:
            logger.warning("Error executing custom output hook: %s", e)
            return text


ACTIVE_CUSTOM_HOOK: Optional[CustomHook] = None


def load_custom_hook(script_path: str) -> CustomHook:
    """Load and validate an external Python hook script."""
    global ACTIVE_CUSTOM_HOOK
    path = Path(script_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Hook script not found: '{path}'")

    module_name = f"windbg_mcp_custom_hook_{path.stem}_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load hook script spec from '{path}'")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    input_cb = _resolve_callback(module, "process_input")
    output_cb = _resolve_callback(module, "process_output")

    if input_cb is None and output_cb is None:
        raise ValueError(
            f"Hook script '{path}' must define 'process_input(text[, context])' or 'process_output(text[, context])'."
        )

    hook_obj = CustomHook(
        path=path,
        process_input_callback=input_cb,
        process_output_callback=output_cb,
    )
    ACTIVE_CUSTOM_HOOK = hook_obj
    return hook_obj


def get_active_custom_hook() -> Optional[CustomHook]:
    """Retrieve current globally active custom hook."""
    return ACTIVE_CUSTOM_HOOK


def _resolve_callback(module: Any, callback_name: str) -> Optional[ResolvedCallback]:
    """Inspect module attribute and return normalized ResolvedCallback signature."""
    callback = getattr(module, callback_name, None)
    if callback is None:
        return None
    if not callable(callback):
        raise TypeError(f"Attribute '{callback_name}' in hook script must be a callable function.")

    signature = inspect.signature(callback)
    params = [
        p for p in signature.parameters.values()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in signature.parameters.values())

    if len(params) == 1 and not has_varargs:
        return lambda text, context: callback(text)

    if len(params) >= 2 or has_varargs:
        return lambda text, context: callback(text, context)

    raise TypeError(f"Callback '{callback_name}' must accept 'text' or 'text, context' parameters.")
