"""Airgapped security guards for KAVACH AI.

Provides:
    * ``AirgapViolation`` - raised when an external provider is requested in
      airgapped mode.
    * ``assert_provider_allowed`` - the airgapped provider guard.
    * File-upload validation: extension allowlist, size cap, filename sanitize
      (path-traversal safe, werkzeug-free).
"""
from __future__ import annotations

import os
import re
import unicodedata

from .. import config


class AirgapViolation(Exception):
    """Raised when an operation would breach the airgapped policy."""


class ValidationError(Exception):
    """Raised for invalid uploads / inputs."""


def assert_provider_allowed(provider_name: str, *, is_external: bool) -> None:
    """Block external providers when running airgapped."""
    if config.IS_AIRGAPPED and (is_external or provider_name.lower() in config.EXTERNAL_PROVIDERS):
        raise AirgapViolation(
            f"Provider '{provider_name}' is external and is blocked in "
            f"KAVACH_MODE=airgapped. Only local providers are permitted."
        )


_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    """Return a safe basename with no path components (path-traversal safe).

    Manual sanitize (no werkzeug):
        * strip directory parts / drive letters
        * normalize unicode
        * reject '..' and separators
        * collapse unsafe chars to '_'
    """
    if not filename:
        raise ValidationError("Empty filename.")
    # Take basename regardless of separator style.
    name = filename.replace("\\", "/").split("/")[-1]
    # Drop any Windows drive prefix leftover.
    name = name.split(":")[-1]
    name = unicodedata.normalize("NFKD", name)
    name = _SAFE_CHARS.sub("_", name).strip("._")
    if not name or name in {".", ".."}:
        raise ValidationError("Invalid filename after sanitization.")
    # Enforce a single extension segment safety.
    if ".." in name or "/" in name or "\\" in name:
        raise ValidationError("Path traversal detected in filename.")
    return name[:200]


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def validate_upload(filename: str, size_bytes: int) -> tuple[str, str]:
    """Validate an upload; return (safe_name, extension) or raise ValidationError."""
    safe = sanitize_filename(filename)
    ext = get_extension(safe)
    if ext not in config.ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '.{ext}' not allowed. Allowed: "
            f"{', '.join(sorted(config.ALLOWED_EXTENSIONS))}."
        )
    if size_bytes > config.MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"File exceeds max size of {config.MAX_UPLOAD_BYTES // (1024*1024)} MB."
        )
    return safe, ext


def safe_join(base_dir, filename: str):
    """Join base_dir + sanitized filename ensuring the result stays inside base."""
    from pathlib import Path

    base = Path(base_dir).resolve()
    safe = sanitize_filename(filename)
    target = (base / safe).resolve()
    if os.path.commonpath([str(base), str(target)]) != str(base):
        raise ValidationError("Resolved path escapes the base directory.")
    return target
