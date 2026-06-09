"""
KƏŞF OSINT Framework — Helpers Module
=======================================

Common utility functions for file operations, hashing, timestamps,
session management, and data formatting.

Usage:
    from utils.helpers import (
        generate_session_id, safe_filename, hash_target,
        timestamp_now, ensure_dir, clean_sandbox, file_size_human,
    )

    sid = generate_session_id()           # "k7x3m9p2"
    name = safe_filename("John Doe 2024") # "John_Doe_2024"
    h = hash_target({"name": "Əli"})      # "a1b2c3d4e5f6..."
    ts = timestamp_now()                  # "2024-01-15_14-30-22"
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

import arrow


# ── Session ID Generation ───────────────────────────────────────────────────

def generate_session_id(length: int = 8) -> str:
    """Generate a short, unique, URL-safe session identifier.

    Uses cryptographically secure random bytes to produce a
    human-readable session ID. Format: lowercase alphanumeric.

    Args:
        length: Length of the session ID (default: 8).
            Must be between 4 and 32.

    Returns:
        A unique session ID string.

    Raises:
        ValueError: If length is outside the valid range.

    Examples:
        >>> sid = generate_session_id()
        >>> len(sid)
        8
        >>> sid.isalnum()
        True
    """
    if not 4 <= length <= 32:
        raise ValueError(f"Session ID length must be 4-32, got {length}")

    # Use secrets for cryptographic randomness
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ── Filename Sanitization ───────────────────────────────────────────────────

def safe_filename(name: str, max_length: int = 200) -> str:
    """Sanitize a string for use as a filesystem-safe filename.

    Replaces or removes characters that are invalid in Windows/Unix
    filenames. Preserves Azerbaijani characters (ə, ş, ç, etc.).

    Args:
        name: Raw string to sanitize.
        max_length: Maximum filename length (default: 200).

    Returns:
        Sanitized filename string. Returns 'unnamed' if input is empty
        after sanitization.

    Examples:
        >>> safe_filename("John Doe / Report 2024")
        'John_Doe_-_Report_2024'
        >>> safe_filename("user@email.com")
        'user_email.com'
        >>> safe_filename("../../../etc/passwd")
        'etc_passwd'
    """
    if not name or not isinstance(name, str):
        return "unnamed"

    # Remove path traversal sequences
    sanitized = name.replace('..', '')

    # Replace path separators and invalid chars with underscores
    # Keep: alphanumeric, Azerbaijani chars, underscore, hyphen, dot, space
    sanitized = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        '_',
        sanitized
    )

    # Replace spaces and consecutive underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)

    # Strip leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_.')

    return sanitized if sanitized else "unnamed"


# ── Target Hashing ──────────────────────────────────────────────────────────

def hash_target(data: dict) -> str:
    """Create a consistent SHA-256 hash for a target data dictionary.

    Produces a deterministic hash regardless of key ordering.
    Useful for deduplication and cache keying.

    Args:
        data: Dictionary containing target information.

    Returns:
        Hex-encoded SHA-256 hash string (64 characters).

    Raises:
        TypeError: If data is not a dictionary.

    Examples:
        >>> hash_target({"name": "Əli", "city": "Bakı"})
        'a1b2c3...'
        >>> hash_target({"city": "Bakı", "name": "Əli"})  # Same hash
        'a1b2c3...'
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data).__name__}")

    # Sort keys for deterministic ordering, handle nested structures
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# ── Timestamps ───────────────────────────────────────────────────────────────

def timestamp_now(fmt: str = "YYYY-MM-DD_HH-mm-ss") -> str:
    """Get the current timestamp in a formatted string.

    Uses Arrow for timezone-aware timestamps. Default format is
    filesystem-safe (no colons or spaces).

    Args:
        fmt: Arrow-compatible format string.
            Default: "YYYY-MM-DD_HH-mm-ss"

    Returns:
        Formatted timestamp string.

    Examples:
        >>> timestamp_now()
        '2024-01-15_14-30-22'
        >>> timestamp_now("YYYY/MM/DD HH:mm:ss")
        '2024/01/15 14:30:22'
    """
    return arrow.now().format(fmt)


def timestamp_utc(fmt: str = "YYYY-MM-DD_HH-mm-ss") -> str:
    """Get the current UTC timestamp in a formatted string.

    Args:
        fmt: Arrow-compatible format string.

    Returns:
        Formatted UTC timestamp string.
    """
    return arrow.utcnow().format(fmt)


# ── Directory Management ────────────────────────────────────────────────────

def ensure_dir(path: Union[str, Path]) -> Path:
    """Create a directory (and parents) if it doesn't exist.

    Thread-safe — uses exist_ok=True to handle race conditions.

    Args:
        path: Directory path to create. Accepts string or Path.

    Returns:
        Path object pointing to the ensured directory.

    Raises:
        OSError: If the directory cannot be created (permissions, etc.).
        ValueError: If path is empty.

    Examples:
        >>> p = ensure_dir("./reports/2024")
        >>> p.exists()
        True
    """
    if not path:
        raise ValueError("Directory path cannot be empty")

    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


# ── Sandbox Cleanup ─────────────────────────────────────────────────────────

def clean_sandbox(sandbox_dir: str) -> dict:
    """Safely remove all contents of the sandbox directory.

    Removes all files and subdirectories within the sandbox,
    but preserves the sandbox directory itself. Logs statistics
    about cleaned items.

    Args:
        sandbox_dir: Path to the sandbox directory.

    Returns:
        Dictionary with cleanup statistics:
            - files_removed (int): Number of files deleted
            - dirs_removed (int): Number of directories deleted
            - errors (list[str]): Any errors encountered
            - total_bytes_freed (int): Total bytes freed

    Examples:
        >>> stats = clean_sandbox("./sandbox")
        >>> print(stats)
        {'files_removed': 5, 'dirs_removed': 2, 'errors': [], 'total_bytes_freed': 1048576}
    """
    stats = {
        "files_removed": 0,
        "dirs_removed": 0,
        "errors": [],
        "total_bytes_freed": 0,
    }

    sandbox_path = Path(sandbox_dir)

    if not sandbox_path.exists():
        return stats

    if not sandbox_path.is_dir():
        stats["errors"].append(f"Not a directory: {sandbox_dir}")
        return stats

    for item in list(sandbox_path.iterdir()):
        try:
            if item.is_file() or item.is_symlink():
                file_size = item.stat().st_size if item.is_file() else 0
                item.unlink()
                stats["files_removed"] += 1
                stats["total_bytes_freed"] += file_size

            elif item.is_dir():
                # Calculate directory size before removal
                dir_size = sum(
                    f.stat().st_size
                    for f in item.rglob('*')
                    if f.is_file()
                )
                file_count = sum(1 for f in item.rglob('*') if f.is_file())

                shutil.rmtree(item, ignore_errors=False)
                stats["dirs_removed"] += 1
                stats["files_removed"] += file_count
                stats["total_bytes_freed"] += dir_size

        except PermissionError as e:
            stats["errors"].append(f"Permission denied: {item} — {e}")
        except OSError as e:
            stats["errors"].append(f"OS error removing {item} — {e}")

    return stats


# ── File Size Formatting ────────────────────────────────────────────────────

def file_size_human(size_bytes: int) -> str:
    """Convert a file size in bytes to a human-readable string.

    Uses binary units (KiB, MiB, GiB) for precision, matching
    how most operating systems report file sizes.

    Args:
        size_bytes: File size in bytes. Must be non-negative.

    Returns:
        Human-readable file size string.

    Examples:
        >>> file_size_human(0)
        '0 B'
        >>> file_size_human(1023)
        '1023 B'
        >>> file_size_human(1024)
        '1.0 KiB'
        >>> file_size_human(1048576)
        '1.0 MiB'
        >>> file_size_human(1073741824)
        '1.0 GiB'
        >>> file_size_human(5368709120)
        '5.0 GiB'
    """
    if size_bytes < 0:
        raise ValueError(f"File size cannot be negative: {size_bytes}")

    if size_bytes == 0:
        return "0 B"

    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"

    return f"{size:.1f} {units[unit_index]}"


# ── Miscellaneous ────────────────────────────────────────────────────────────

def truncate_string(text: str, max_length: int = 100, suffix: str = "…") -> str:
    """Truncate a string to a maximum length with an ellipsis suffix.

    Args:
        text: String to truncate.
        max_length: Maximum length including suffix.
        suffix: String to append when truncated.

    Returns:
        Truncated string.
    """
    if not text or len(text) <= max_length:
        return text or ""
    return text[: max_length - len(suffix)] + suffix


def flatten_dict(
    data: dict,
    parent_key: str = "",
    separator: str = ".",
) -> dict:
    """Flatten a nested dictionary into a single-level dict with dot-notation keys.

    Useful for logging and hashing nested target data.

    Args:
        data: Nested dictionary to flatten.
        parent_key: Prefix for keys (used in recursion).
        separator: Separator between nested keys.

    Returns:
        Flattened dictionary.

    Examples:
        >>> flatten_dict({"a": {"b": 1, "c": {"d": 2}}})
        {'a.b': 1, 'a.c.d': 2}
    """
    items: list[tuple[str, object]] = []
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    return dict(items)
