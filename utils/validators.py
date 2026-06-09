"""
KƏŞF OSINT Framework — Validators Module
==========================================

Input validation and normalization utilities for OSINT data processing.
Features:
    - RFC-compliant email validation
    - Phone number validation with AZ +994 format support
    - Username validation with safe character checking
    - Azerbaijani name normalization (ə, ş, ç, ö, ü, ı, ğ)
    - URL domain extraction and safety checking

Usage:
    from utils.validators import validate_email, validate_phone, normalize_name

    assert validate_email("user@example.com") is True
    valid, normalized = validate_phone("+994501234567")
    name = normalize_name("  əli  həsənov  ")  # -> "Əli Həsənov"
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse

# ── Constants ────────────────────────────────────────────────────────────────

# RFC 5322 simplified email pattern — covers 99.9% of real-world addresses
_EMAIL_REGEX = re.compile(
    r'^(?!.*\.\.)(?!.*\.$)(?!^\.)'  # No consecutive dots, no leading/trailing dots
    r'[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+'
    r'@'
    r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'
    r'\.[a-zA-Z]{2,}$',
    re.IGNORECASE
)

# Valid username characters (alphanumeric, underscore, hyphen, dot)
_USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{1,38}[a-zA-Z0-9]$')

# Azerbaijan phone patterns
_AZ_PHONE_REGEX = re.compile(
    r'^(?:\+994|994|0)?'  # Country code or leading zero
    r'\s*[-.]?\s*'
    r'(10|12|18|20|21|22|23|24|25|26|27|29|33|36|40|41|44|50|51|55|60|70|77|99)'  # Operator/area codes
    r'\s*[-.]?\s*'
    r'(\d{3})'
    r'\s*[-.]?\s*'
    r'(\d{2})'
    r'\s*[-.]?\s*'
    r'(\d{2})$'
)

# International phone pattern (E.164-ish, relaxed)
_INTL_PHONE_REGEX = re.compile(
    r'^\+?[1-9]\d{6,14}$'
)

# Azerbaijani special characters and their ASCII equivalents
_AZ_CHAR_MAP = {
    'ə': 'ə', 'Ə': 'Ə',
    'ş': 'ş', 'Ş': 'Ş',
    'ç': 'ç', 'Ç': 'Ç',
    'ö': 'ö', 'Ö': 'Ö',
    'ü': 'ü', 'Ü': 'Ü',
    'ı': 'ı', 'I': 'I',
    'İ': 'İ', 'i': 'i',
    'ğ': 'ğ', 'Ğ': 'Ğ',
}

# Azerbaijani lowercase-to-uppercase mapping (special cases)
_AZ_UPPER_MAP = {
    'ə': 'Ə', 'ş': 'Ş', 'ç': 'Ç', 'ö': 'Ö',
    'ü': 'Ü', 'ı': 'I', 'i': 'İ', 'ğ': 'Ğ',
}

# Domains considered unsafe (local/private networks, common malware hosts)
_UNSAFE_DOMAINS = {
    'localhost', '127.0.0.1', '0.0.0.0', '::1',
    '10.0.0.0', '172.16.0.0', '192.168.0.0',
}

_UNSAFE_SCHEMES = {'file', 'ftp', 'javascript', 'data', 'vbscript'}

# Private/reserved IP ranges
_PRIVATE_IP_REGEX = re.compile(
    r'^(?:127\.|10\.|172\.(?:1[6-9]|2\d|3[01])\.|192\.168\.|169\.254\.|0\.)'
)


# ── Email Validation ─────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """Validate an email address against RFC 5322 (simplified).

    Checks format, length constraints, and rejects obviously invalid
    patterns like consecutive dots or missing TLD.

    Args:
        email: Email address string to validate.

    Returns:
        True if the email address is valid, False otherwise.

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("user@.com")
        False
        >>> validate_email("user@example")
        False
        >>> validate_email("")
        False
    """
    if not email or not isinstance(email, str):
        return False

    # Length checks per RFC 5321
    if len(email) > 254:
        return False

    parts = email.split('@')
    if len(parts) != 2:
        return False

    local_part, domain = parts

    # Local part max 64 chars
    if len(local_part) > 64 or len(local_part) == 0:
        return False

    # Domain must have at least one dot
    if '.' not in domain:
        return False

    return bool(_EMAIL_REGEX.match(email))


# ── Phone Validation ─────────────────────────────────────────────────────────

def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate and normalize a phone number.

    Supports Azerbaijan (+994) format with operator code detection.
    Falls back to international E.164 validation for non-AZ numbers.

    Args:
        phone: Phone number string (various formats accepted).

    Returns:
        Tuple of (is_valid, normalized_number).
        If valid, normalized_number is in +994XXXXXXXXX format for AZ
        numbers, or +XXXXXXXXXXX for international numbers.
        If invalid, normalized_number is an empty string.

    Examples:
        >>> validate_phone("+994 50 123 45 67")
        (True, '+994501234567')
        >>> validate_phone("050-123-45-67")
        (True, '+994501234567')
        >>> validate_phone("+1 555 123 4567")
        (True, '+15551234567')
        >>> validate_phone("12345")
        (False, '')
    """
    if not phone or not isinstance(phone, str):
        return False, ""

    # Strip whitespace and common formatting characters for initial check
    cleaned = phone.strip()

    # Try Azerbaijan format first
    az_match = _AZ_PHONE_REGEX.match(cleaned)
    if az_match:
        operator = az_match.group(1)
        part1 = az_match.group(2)
        part2 = az_match.group(3)
        part3 = az_match.group(4)
        normalized = f"+994{operator}{part1}{part2}{part3}"
        return True, normalized

    # Strip all non-digit characters except leading +
    has_plus = cleaned.startswith('+')
    digits_only = re.sub(r'[^\d]', '', cleaned)

    if not digits_only:
        return False, ""

    # Re-check as AZ number if it starts with 994
    if digits_only.startswith('994') and len(digits_only) == 12:
        remainder = digits_only[3:]
        az_recheck = _AZ_PHONE_REGEX.match(f"+994{remainder}")
        if az_recheck:
            normalized = f"+994{remainder}"
            return True, normalized

    # Try international format
    intl_number = f"+{digits_only}" if has_plus else f"+{digits_only}"
    if _INTL_PHONE_REGEX.match(digits_only):
        return True, f"+{digits_only}"

    return False, ""


# ── Username Validation ──────────────────────────────────────────────────────

def validate_username(username: str) -> bool:
    """Validate a username for safe characters and length.

    Usernames must:
    - Be 3-40 characters long
    - Start and end with alphanumeric characters
    - Contain only alphanumeric characters, underscores, hyphens, and dots
    - Not contain consecutive special characters

    Args:
        username: Username string to validate.

    Returns:
        True if the username is valid, False otherwise.

    Examples:
        >>> validate_username("john_doe")
        True
        >>> validate_username("a")
        False
        >>> validate_username("user..name")
        False
        >>> validate_username("valid-user.name")
        True
    """
    if not username or not isinstance(username, str):
        return False

    # Length check
    if len(username) < 3 or len(username) > 40:
        return False

    # Basic pattern check
    if not _USERNAME_REGEX.match(username):
        return False

    # No consecutive special characters
    if re.search(r'[._-]{2,}', username):
        return False

    return True


# ── Name Normalization ───────────────────────────────────────────────────────

def _az_title_char(char: str) -> str:
    """Convert a single character to Azerbaijani title case.

    Handles special Azerbaijani letters that Python's built-in
    str.title() doesn't process correctly.

    Args:
        char: Single character to convert.

    Returns:
        Title-cased character.
    """
    return _AZ_UPPER_MAP.get(char, char.upper())


def normalize_name(name: str) -> str:
    """Normalize an Azerbaijani name with proper casing and spacing.

    Handles:
    - Azerbaijani special characters (ə, ş, ç, ö, ü, ı, ğ, İ)
    - Proper title casing for Azerbaijani names
    - Whitespace normalization (strips, collapses)
    - Removal of extraneous characters

    Args:
        name: Raw name string to normalize.

    Returns:
        Normalized name with proper Azerbaijani title casing.

    Examples:
        >>> normalize_name("  əli  həsənov  ")
        'Əli Həsənov'
        >>> normalize_name("MƏHƏMMƏD ƏLİYEV")
        'Məhəmməd Əliyev'
        >>> normalize_name("şəhriyar")
        'Şəhriyar'
    """
    if not name or not isinstance(name, str):
        return ""

    # Remove control characters and normalize whitespace
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if not cleaned:
        return ""

    # Split into words and apply Azerbaijani title casing
    words = cleaned.split()
    title_words = []

    for word in words:
        if not word:
            continue

        # First character: uppercase (Azerbaijani-aware)
        first = _az_title_char(word[0])
        # Rest: lowercase (Azerbaijani-aware — handle İ -> i, I -> ı)
        rest = ""
        for ch in word[1:]:
            if ch == 'İ':
                rest += 'i'
            elif ch == 'I':
                rest += 'ı'
            else:
                rest += ch.lower()

        title_words.append(first + rest)

    return " ".join(title_words)


# ── URL Utilities ────────────────────────────────────────────────────────────

def extract_domain(url: str) -> str:
    """Extract the domain name from a URL.

    Handles URLs with or without scheme, strips 'www.' prefix,
    and returns the bare domain.

    Args:
        url: URL string to extract domain from.

    Returns:
        Extracted domain name, or empty string if extraction fails.

    Examples:
        >>> extract_domain("https://www.example.com/path?q=1")
        'example.com'
        >>> extract_domain("http://sub.domain.co.uk/page")
        'sub.domain.co.uk'
        >>> extract_domain("example.com")
        'example.com'
    """
    if not url or not isinstance(url, str):
        return ""

    url = url.strip()

    # Add scheme if missing (urlparse needs it)
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        url = f"https://{url}"

    try:
        parsed = urlparse(url)
        domain = parsed.hostname or ""

        # Strip www. prefix
        if domain.startswith("www."):
            domain = domain[4:]

        return domain.lower()

    except Exception:
        return ""


def is_safe_url(url: str) -> bool:
    """Check if a URL is safe for automated access.

    Rejects:
    - Local/private network addresses
    - Dangerous schemes (file://, javascript://, data://)
    - URLs pointing to reserved IP ranges
    - Malformed URLs

    Args:
        url: URL string to check.

    Returns:
        True if the URL is considered safe, False otherwise.

    Examples:
        >>> is_safe_url("https://example.com")
        True
        >>> is_safe_url("file:///etc/passwd")
        False
        >>> is_safe_url("http://127.0.0.1/admin")
        False
        >>> is_safe_url("javascript:alert(1)")
        False
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # Must have a valid scheme
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        url = f"https://{url}"

    try:
        parsed = urlparse(url)

        # Check scheme
        scheme = (parsed.scheme or "").lower()
        if scheme in _UNSAFE_SCHEMES:
            return False

        # Only allow http and https
        if scheme not in ('http', 'https'):
            return False

        # Check hostname
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False

        # Check against known unsafe domains
        if hostname in _UNSAFE_DOMAINS:
            return False

        # Check for private/reserved IP ranges
        if _PRIVATE_IP_REGEX.match(hostname):
            return False

        # Check for IPv6 loopback
        if hostname in ('::1', '[::1]'):
            return False

        # Must have a valid TLD (at least one dot for domain names)
        # Allow IP addresses that passed the private check
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname):
            if '.' not in hostname:
                return False

        return True

    except Exception:
        return False
