"""
core/throttle.py — Intelligent Request Throttling & Anti-Detection Module

Provides human-like request timing with gaussian-distributed delays, burst
detection and cooldown, per-domain rate limiting, and User-Agent rotation.
All timing patterns are designed to mimic natural human browsing behavior
so that automated queries are indistinguishable from organic traffic.
"""

from __future__ import annotations

import math
import random
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

from loguru import logger

from ui.locale_az import (
    THROTTLE_WAITING,
    THROTTLE_RATE_LIMITED,
    THROTTLE_QUERY_COUNT,
    THROTTLE_COOLDOWN,
    THROTTLE_RESUMING,
    THROTTLE_BACKOFF,
    THROTTLE_BLOCKED,
    THROTTLE_ADAPTIVE,
)

# ---------------------------------------------------------------------------
# Default User-Agent pool (used only when config/user_agents.txt is missing)
# These are REAL, current user agents — never invent fake ones.
# ---------------------------------------------------------------------------
_FALLBACK_USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

# Weight distribution — common browsers get picked more often
_FALLBACK_WEIGHTS: list[float] = [0.22, 0.18, 0.15, 0.12, 0.10, 0.08, 0.08, 0.07]


class RequestThrottler:
    """Intelligent request throttler that mimics human browsing patterns.

    Features:
        - Gaussian-distributed random delays (not uniform) for natural timing
        - Burst detection with automatic cooldown
        - Per-domain rate limiting to avoid hammering a single host
        - User-Agent rotation from a weighted pool
        - Session-wide query counting with hard cap
        - Jitter on all delay values to prevent detectable periodicity

    Args:
        config: Dictionary with throttle settings from settings.yaml.
            Expected keys: base_delay_min, base_delay_max, burst_limit,
            burst_cooldown, max_queries_per_session, domain_cooldown.
    """

    def __init__(self, config: dict) -> None:
        # --- Timing parameters ---
        self._base_delay_min: float = config.get("base_delay_min", 3.0)
        self._base_delay_max: float = config.get("base_delay_max", 8.0)
        self._burst_limit: int = config.get("burst_limit", 5)
        self._burst_cooldown: float = config.get("burst_cooldown", 30.0)
        self._max_queries: int = config.get("max_queries_per_session", 200)
        self._domain_cooldown: float = config.get("domain_cooldown", 15.0)

        # --- Internal state ---
        self._query_count: int = 0
        self._burst_timestamps: list[float] = []
        self._domain_last_access: dict[str, float] = defaultdict(float)
        self._session_start: float = time.monotonic()

        # --- User-Agent pool ---
        self._user_agents: list[str] = []
        self._ua_weights: list[float] = []
        self._load_user_agents(config.get("user_agents_file", "config/user_agents.txt"))

        logger.debug(
            "RequestThrottler initialized: delay={}-{}s, burst_limit={}, max_queries={}",
            self._base_delay_min,
            self._base_delay_max,
            self._burst_limit,
            self._max_queries,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def wait(self, domain: Optional[str] = None) -> None:
        """Wait with a randomized, human-like delay before the next request.

        Uses a gaussian distribution centered between min and max delay,
        with added jitter and burst cooldown logic. This produces timing
        that looks natural rather than metronomic.

        Args:
            domain: Optional domain name. If provided, enforces per-domain
                    cooldown on top of the base delay.
        """
        import asyncio

        # --- Calculate base delay using gaussian distribution ---
        mean_delay = (self._base_delay_min + self._base_delay_max) / 2.0
        std_dev = (self._base_delay_max - self._base_delay_min) / 4.0  # ~95% within range
        delay = random.gauss(mean_delay, std_dev)

        # Clamp to reasonable bounds (never negative, never absurdly long)
        delay = max(self._base_delay_min * 0.6, min(delay, self._base_delay_max * 1.5))

        # --- Add jitter (±15% random noise) ---
        jitter_factor = 1.0 + random.uniform(-0.15, 0.15)
        delay *= jitter_factor

        # --- Burst detection cooldown ---
        now = time.monotonic()
        self._burst_timestamps = [
            ts for ts in self._burst_timestamps if now - ts < self._burst_cooldown
        ]
        if len(self._burst_timestamps) >= self._burst_limit:
            burst_extra = self._burst_cooldown + random.uniform(2.0, 8.0)
            logger.warning(
                THROTTLE_COOLDOWN.format(seconds=burst_extra)
            )
            delay += burst_extra

        # --- Per-domain cooldown ---
        if domain:
            last_access = self._domain_last_access.get(domain, 0.0)
            since_last = now - last_access
            if since_last < self._domain_cooldown:
                domain_wait = self._domain_cooldown - since_last + random.uniform(1.0, 3.0)
                logger.info(
                    THROTTLE_RATE_LIMITED.format(seconds=domain_wait)
                )
                delay += domain_wait

        # --- Occasional "long pause" (simulates human distraction) ---
        if random.random() < 0.08:  # ~8% chance of a longer pause
            delay += random.uniform(3.0, 12.0)

        logger.debug(THROTTLE_WAITING.format(seconds=f"{delay:.1f}"))
        await asyncio.sleep(delay)

    def get_random_user_agent(self) -> str:
        """Return a random User-Agent from the pool, weighted toward common ones.

        More popular browsers (Chrome on Windows) are weighted higher to match
        real-world browser distribution and avoid standing out.

        Returns:
            A realistic User-Agent string.
        """
        if self._user_agents and self._ua_weights:
            return random.choices(self._user_agents, weights=self._ua_weights, k=1)[0]
        return random.choices(_FALLBACK_USER_AGENTS, weights=_FALLBACK_WEIGHTS, k=1)[0]

    def can_query(self) -> bool:
        """Check whether we haven't exceeded session rate limits.

        Returns:
            True if more queries are allowed in this session, False otherwise.
        """
        if self._query_count >= self._max_queries:
            logger.warning(
                THROTTLE_BLOCKED.format(minutes=0)
            )
            return False
        return True

    def record_query(self, domain: Optional[str] = None) -> None:
        """Record a query and update all internal counters.

        Args:
            domain: Optional domain that was queried (for per-domain tracking).
        """
        now = time.monotonic()
        self._query_count += 1
        self._burst_timestamps.append(now)
        if domain:
            self._domain_last_access[domain] = now
        logger.debug(
            THROTTLE_QUERY_COUNT.format(
                current=self._query_count, max=self._max_queries
            )
        )

    @property
    def queries_remaining(self) -> int:
        """Number of queries remaining in this session."""
        return max(0, self._max_queries - self._query_count)

    @property
    def query_count(self) -> int:
        """Total queries executed so far in this session."""
        return self._query_count

    @property
    def session_elapsed(self) -> float:
        """Seconds elapsed since the throttler was initialized."""
        return time.monotonic() - self._session_start

    def reset(self) -> None:
        """Reset all counters for a new session."""
        self._query_count = 0
        self._burst_timestamps.clear()
        self._domain_last_access.clear()
        self._session_start = time.monotonic()
        logger.info(THROTTLE_RESUMING)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_user_agents(self, filepath: str) -> None:
        """Load user agents from a text file (one per line).

        Assigns weights using a decaying distribution: agents listed first
        (assumed to be more common) receive higher weights.

        Args:
            filepath: Path to the user agents file.
        """
        try:
            ua_path = Path(filepath)
            if not ua_path.is_absolute():
                # Resolve relative to project root
                ua_path = Path(__file__).resolve().parent.parent / filepath

            if ua_path.exists():
                with open(ua_path, "r", encoding="utf-8") as f:
                    agents = [line.strip() for line in f if line.strip() and not line.startswith("#")]

                if agents:
                    self._user_agents = agents
                    # Assign exponentially decaying weights so that agents listed
                    # first (most common) are selected more frequently.
                    n = len(agents)
                    raw_weights = [math.exp(-0.02 * i) for i in range(n)]
                    total_weight = sum(raw_weights)
                    self._ua_weights = [w / total_weight for w in raw_weights]
                    logger.info(
                        THROTTLE_ADAPTIVE.format(rate=len(agents))
                    )
                    return

            logger.warning("User-Agent file not found: {}", str(ua_path))
        except Exception as exc:
            logger.error("Error loading User-Agent file: {}", str(exc))

        # Fall back to built-in pool
        self._user_agents = list(_FALLBACK_USER_AGENTS)
        self._ua_weights = list(_FALLBACK_WEIGHTS)
        logger.info("Using {} built-in fallback user agents.", len(self._user_agents))
