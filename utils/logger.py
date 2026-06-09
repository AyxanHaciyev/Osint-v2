"""
KƏŞF OSINT Framework — Logger Module
======================================

Dual-output logging system using Loguru with Rich console integration.
Features:
    - File logging with rotation (10MB, keep 5 backups)
    - Rich-formatted console output with color coding
    - Automatic sensitive data masking (IPs, emails, phone numbers)
    - Session ID tracking for multi-session operations
    - Thread-safe operation

Usage:
    from utils.logger import setup_logger, mask_sensitive

    logger = setup_logger(session_id="abc123")
    logger.info("Starting OSINT scan for target")
    
    masked = mask_sensitive("Contact john@example.com at 192.168.1.1")
    # -> "Contact j***@e******.com at ***.***.1.1"
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as _loguru_logger
from rich.console import Console
from rich.text import Text

# ── Constants ────────────────────────────────────────────────────────────────

# Regex patterns for sensitive data detection
_EMAIL_PATTERN = re.compile(
    r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
)
_IPV4_PATTERN = re.compile(
    r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'
)
_PHONE_PATTERN = re.compile(
    r'(?<!\d)(\+?\d{1,3}[\s.-]?)(\(?\d{2,4}\)?[\s.-]?)'
    r'(\d{3}[\s.-]?\d{2}[\s.-]?\d{2})(?!\d)'
)

# Log format strings
_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
    "session:{extra[session_id]} | {module}:{function}:{line} | {message}"
)
_CONSOLE_FORMAT = (
    "<level>{level:<8}</level> | "
    "<cyan>{extra[session_id]}</cyan> | <level>{message}</level>"
)

# Rich console for colored output
_console = Console(stderr=True)


# ── Sensitive Data Masking ───────────────────────────────────────────────────

def mask_sensitive(text: str) -> str:
    """Mask sensitive data in text strings.

    Replaces emails, IPv4 addresses, and phone numbers with partially
    redacted versions to prevent accidental exposure in logs.

    Args:
        text: The input text potentially containing sensitive data.

    Returns:
        Text with sensitive data masked.

    Examples:
        >>> mask_sensitive("Email: user@example.com")
        'Email: u***@e******.com'
        >>> mask_sensitive("IP: 192.168.1.100")
        'IP: ***.***.1.100'
        >>> mask_sensitive("Phone: +994 50 123 45 67")
        'Phone: +994 ** *** ** 67'
    """
    if not isinstance(text, str):
        text = str(text)

    # Mask email addresses: show first char of local + first char of domain
    def _mask_email(match: re.Match) -> str:
        local_part = match.group(1)
        domain = match.group(2)
        masked_local = local_part[0] + "***" if local_part else "***"
        domain_parts = domain.split(".")
        masked_domain = domain_parts[0][0] + "*" * min(6, len(domain_parts[0]) - 1)
        return f"{masked_local}@{masked_domain}.{domain_parts[-1]}"

    text = _EMAIL_PATTERN.sub(_mask_email, text)

    # Mask IPv4 addresses: hide first two octets
    def _mask_ipv4(match: re.Match) -> str:
        return f"***.***." f"{match.group(3)}.{match.group(4)}"

    text = _IPV4_PATTERN.sub(_mask_ipv4, text)

    # Mask phone numbers: show country code and last 2 digits
    def _mask_phone(match: re.Match) -> str:
        prefix = match.group(1).strip()
        suffix = match.group(3).strip()
        last_two = suffix[-2:] if len(suffix) >= 2 else suffix
        return f"{prefix} ** *** ** {last_two}"

    text = _PHONE_PATTERN.sub(_mask_phone, text)

    return text


# ── Rich Console Sink ────────────────────────────────────────────────────────

def _rich_sink(message) -> None:
    """Custom Loguru sink that outputs via Rich console.

    Maps Loguru log levels to Rich styles for colored terminal output.
    Applies sensitive data masking before display.
    """
    record = message.record
    level = record["level"].name

    # Map log levels to Rich style colors
    level_styles = {
        "TRACE": "dim",
        "DEBUG": "dim cyan",
        "INFO": "green",
        "SUCCESS": "bold green",
        "WARNING": "bold yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }

    style = level_styles.get(level, "white")
    session_id = record["extra"].get("session_id", "???")
    masked_msg = mask_sensitive(str(record["message"]))

    text = Text()
    text.append(f"{level:<8}", style=style)
    text.append(" | ", style="dim")
    text.append(f"{session_id}", style="cyan")
    text.append(" | ", style="dim")
    text.append(masked_msg, style=style)

    _console.print(text)


# ── Logger Setup ─────────────────────────────────────────────────────────────

def setup_logger(
    session_id: str,
    log_dir: str = "./logs",
    level: str = "DEBUG",
    rotation: str = "10 MB",
    retention: int = 5,
    mask_in_file: bool = True,
) -> "Logger":
    """Configure and return a Loguru logger instance.

    Sets up dual-output logging:
      1. File output with detailed timestamps, rotation, and retention.
      2. Rich console output with color-coded levels.

    Both outputs automatically mask sensitive data (emails, IPs, phones).

    Args:
        session_id: Unique identifier for the current session.
        log_dir: Directory path for log files. Created if it doesn't exist.
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        rotation: Log file rotation threshold (e.g., "10 MB", "1 day").
        retention: Number of rotated log files to keep.
        mask_in_file: Whether to mask sensitive data in file logs.

    Returns:
        Configured Loguru logger instance bound with the session ID.

    Raises:
        OSError: If the log directory cannot be created.

    Example:
        >>> logger = setup_logger("sess_abc123", log_dir="./logs")
        >>> logger.info("VPN check passed for target")
        >>> logger.warning("Rate limit approaching: 180/200 queries used")
    """
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove default Loguru handlers to start fresh
    _loguru_logger.remove()

    # Bind session ID to all log messages
    bound_logger = _loguru_logger.bind(session_id=session_id)

    # ── File Handler ─────────────────────────────────────────────────────
    log_file = log_path / f"kesf_{session_id}.log"

    if mask_in_file:
        # Custom format function that masks sensitive data in file output
        def _masked_file_format(record: dict) -> str:
            record["message"] = mask_sensitive(str(record["message"]))
            return _FILE_FORMAT + "\n"

        _loguru_logger.add(
            str(log_file),
            format=_masked_file_format,
            level=level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
            enqueue=True,  # Thread-safe
            backtrace=True,
            diagnose=False,  # Don't expose variable values in tracebacks
        )
    else:
        _loguru_logger.add(
            str(log_file),
            format=_FILE_FORMAT,
            level=level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            diagnose=False,
        )

    # ── Rich Console Handler ─────────────────────────────────────────────
    _loguru_logger.add(
        _rich_sink,
        level=level,
        colorize=False,  # Rich handles colors
        format="{message}",  # Minimal — Rich sink does formatting
    )

    bound_logger.info(f"Logger initialized | log_file={log_file}")

    return bound_logger


# ── Module-level convenience ─────────────────────────────────────────────────

def get_logger(session_id: Optional[str] = None) -> "Logger":
    """Get a logger instance bound to a session ID.

    If no session_id is provided, returns the default Loguru logger
    without session binding.

    Args:
        session_id: Optional session identifier.

    Returns:
        Loguru logger instance.
    """
    if session_id:
        return _loguru_logger.bind(session_id=session_id)
    return _loguru_logger.bind(session_id="unbound")
