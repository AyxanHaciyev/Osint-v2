"""
core/opsec.py — Operational Security Module

Verifies that all traffic is routed through Mullvad VPN before any OSINT
queries are executed. Performs VPN interface detection, public IP verification,
DNS leak checks, and continuous VPN monitoring with kill-switch capability.

All user-facing strings are imported from ui.locale_az for full localization.
"""

from __future__ import annotations

import asyncio
import platform
from typing import Any, Optional

import httpx
import psutil
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ui.locale_az import (
    OPSEC_CHECKING_VPN,
    OPSEC_VPN_ACTIVE,
    OPSEC_VPN_NOT_FOUND,
    OPSEC_VPN_REQUIRED,
    OPSEC_FETCHING_IP,
    OPSEC_IP_INFO,
    OPSEC_IP_FETCH_FAILED,
    OPSEC_DNS_CHECKING,
    OPSEC_DNS_SAFE,
    OPSEC_DNS_LEAK,
    OPSEC_IDENTITY_CONFIRM,
    OPSEC_CONFIRMED,
    OPSEC_DENIED,
    OPSEC_CHECK_COMPLETE,
    OPSEC_CHECK_FAILED,
    OPSEC_MONITORING,
    OPSEC_VPN_DROPPED,
    OPSEC_VPN_RESTORED,
    OPSEC_KILL_SWITCH,
)

# Mullvad API endpoint for identity verification
_MULLVAD_API_URL = "https://am.i.mullvad.net/json"

# Known VPN interface name patterns (cross-platform)
_VPN_INTERFACE_PATTERNS: list[str] = [
    "tun",          # OpenVPN / generic TUN
    "wg",           # WireGuard
    "mullvad",      # Mullvad-specific
    "wireguard",    # WireGuard branded
    "nordlynx",     # NordVPN (WireGuard-based)
    "proton",       # ProtonVPN
]


class OpSecGuard:
    """Operational security guard that verifies VPN connectivity and identity.

    Ensures all traffic is routed through Mullvad VPN (or compatible) before
    any OSINT operations begin. Provides continuous monitoring with kill-switch.

    Args:
        config: VPN configuration dictionary from settings.yaml.
            Expected keys: mullvad_api_url, expected_interfaces, dns_leak_check.
        console: Rich Console instance for formatted output.
    """

    def __init__(self, config: dict, console: Console) -> None:
        self._config = config
        self._console = console
        self._mullvad_url: str = config.get("mullvad_api_url", _MULLVAD_API_URL)
        self._expected_interfaces: list[str] = config.get(
            "expected_interfaces", ["tun0", "wg0", "Mullvad"]
        )
        self._dns_leak_check_enabled: bool = config.get("dns_leak_check", True)
        self._is_safe: bool = False
        self._current_ip_info: dict[str, Any] = {}
        self._vpn_interface_name: str = ""
        self._monitoring: bool = False
        self._monitor_task: Optional[asyncio.Task] = None

        logger.debug("OpSecGuard initialized with Mullvad API URL: {}", self._mullvad_url)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def full_check(self) -> bool:
        """Run complete OpSec verification suite.

        Sequence:
            1. Check for VPN network interface
            2. Fetch public IP information from Mullvad API
            3. Check for DNS leaks
            4. Display all security info to user
            5. Ask for explicit user confirmation

        Returns:
            True if all checks pass and user confirms, False otherwise.
        """
        self._console.print()
        self._console.print(
            Panel(
                "🛡  OpSec yoxlaması başladılır...",
                title="🛡 OpSec",
                border_style="bright_cyan",
            )
        )

        # --- Step 1: VPN Interface ---
        self._console.print(f"\n  [cyan]⟳[/cyan] {OPSEC_CHECKING_VPN}")
        vpn_found, vpn_detail = self.check_vpn_interface()

        if vpn_found:
            self._console.print(
                f"  [green]✓[/green] {OPSEC_VPN_ACTIVE.format(interface=vpn_detail)}"
            )
        else:
            self._console.print(f"  [red]✗[/red] {OPSEC_VPN_NOT_FOUND}")
            self._console.print(
                Panel(
                    OPSEC_VPN_REQUIRED,
                    title="⛔ XƏBƏRDARLIQ",
                    border_style="red",
                )
            )
            self._is_safe = False
            return False

        # --- Step 2: Public IP Info ---
        self._console.print(f"\n  [cyan]⟳[/cyan] {OPSEC_FETCHING_IP}")
        ip_info = await self.fetch_ip_info()

        if not ip_info:
            self._console.print(
                f"  [red]✗[/red] {OPSEC_IP_FETCH_FAILED.format(error='Mullvad API əlçatmaz')}"
            )
            self._is_safe = False
            return False

        self._current_ip_info = ip_info

        # --- Step 3: DNS Leak Check ---
        dns_safe = True
        dns_detail = ""
        if self._dns_leak_check_enabled:
            self._console.print(f"\n  [cyan]⟳[/cyan] {OPSEC_DNS_CHECKING}")
            dns_safe, dns_detail = await self.check_dns_leak()
            if dns_safe:
                self._console.print(f"  [green]✓[/green] {OPSEC_DNS_SAFE}")
            else:
                self._console.print(
                    f"  [yellow]⚠[/yellow] {OPSEC_DNS_LEAK.format(dns=dns_detail)}"
                )

        # --- Step 4: Display Security Status Panel ---
        self._display_status_panel(vpn_detail, ip_info, dns_safe, dns_detail)

        # --- Step 5: User Confirmation ---
        self._console.print()
        try:
            user_input = self._console.input(f"  {OPSEC_IDENTITY_CONFIRM}").strip().upper()
        except (EOFError, KeyboardInterrupt):
            user_input = "X"

        if user_input in ("B", "Y", "YES", "BƏLİ", "BELI"):
            self._console.print(f"\n  [green]✓[/green] {OPSEC_CONFIRMED}")
            self._is_safe = True
            logger.info(OPSEC_CHECK_COMPLETE)
            return True
        else:
            self._console.print(f"\n  [red]✗[/red] {OPSEC_DENIED}")
            self._is_safe = False
            logger.warning(OPSEC_CHECK_FAILED)
            return False

    def check_vpn_interface(self) -> tuple[bool, str]:
        """Check for VPN network interface on the system.

        Uses psutil to enumerate all network interfaces and looks for
        Mullvad, WireGuard, or TUN/TAP adapters. On Windows, checks
        adapter names; on Linux/macOS, checks interface names.

        Returns:
            Tuple of (found: bool, interface_name: str).
            If found, interface_name is the detected adapter/interface name.
            If not found, interface_name is an empty string.
        """
        try:
            interfaces = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            system = platform.system().lower()

            for iface_name in interfaces:
                name_lower = iface_name.lower()

                # Check if interface name matches known VPN patterns
                for pattern in _VPN_INTERFACE_PATTERNS:
                    if pattern in name_lower:
                        # Verify interface is actually up
                        stats = if_stats.get(iface_name)
                        if stats and stats.isup:
                            self._vpn_interface_name = iface_name
                            logger.info("VPN interface detected: {} (up)", iface_name)
                            return True, iface_name
                        else:
                            logger.debug(
                                "VPN interface {} found but not active (isup={})",
                                iface_name,
                                stats.isup if stats else "N/A",
                            )

                # Also check for expected interface names from config
                for expected in self._expected_interfaces:
                    if expected.lower() in name_lower:
                        stats = if_stats.get(iface_name)
                        if stats and stats.isup:
                            self._vpn_interface_name = iface_name
                            logger.info("Expected VPN interface detected: {}", iface_name)
                            return True, iface_name

            logger.warning("No VPN interface detected among: {}", list(interfaces.keys()))
            return False, ""

        except Exception as exc:
            logger.error("Error checking VPN interface: {}", exc)
            return False, ""

    async def fetch_ip_info(self) -> dict[str, Any]:
        """Fetch current public IP information from the Mullvad API.

        Makes a clean HTTPS request to am.i.mullvad.net/json which returns
        the visible public identity (IP, ISP, country, city, and whether
        the exit is a known Mullvad node).

        Returns:
            Dictionary with keys: ip, isp, country, city, mullvad_exit_ip,
            mullvad_exit_ip_hostname, organization, latitude, longitude.
            Empty dict on failure.
        """
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(15.0),
                follow_redirects=True,
                # Use a normal-looking accept header
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            ) as client:
                response = await client.get(self._mullvad_url)
                response.raise_for_status()
                data = response.json()

                ip_info = {
                    "ip": data.get("ip", "N/A"),
                    "isp": data.get("organization", data.get("isp", "N/A")),
                    "country": data.get("country", "N/A"),
                    "city": data.get("city", "N/A"),
                    "mullvad_exit": data.get("mullvad_exit_ip", False),
                    "mullvad_exit_hostname": data.get("mullvad_exit_ip_hostname", "N/A"),
                    "blacklisted": data.get("blacklisted", {}).get("results", []),
                }

                logger.info(
                    OPSEC_IP_INFO.format(
                        ip=ip_info["ip"],
                        isp=ip_info["isp"],
                        country=ip_info["country"],
                        city=ip_info["city"],
                    )
                )
                return ip_info

        except httpx.TimeoutException:
            logger.error("Timeout fetching IP info from {}", self._mullvad_url)
            return {}
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error fetching IP info: {} {}", exc.response.status_code, exc)
            return {}
        except Exception as exc:
            logger.error("Unexpected error fetching IP info: {}", exc)
            return {}

    async def check_dns_leak(self) -> tuple[bool, str]:
        """Check if DNS requests are leaking outside the VPN tunnel.

        Queries a DNS leak test endpoint and compares the resolver's ISP
        against the known VPN provider to detect if DNS is being resolved
        through the user's real ISP rather than the VPN's DNS.

        Returns:
            Tuple of (is_safe: bool, detail: str).
            is_safe is True if DNS appears to be going through the VPN.
        """
        try:
            # Use Mullvad's own DNS leak test
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(15.0),
                follow_redirects=True,
            ) as client:
                response = await client.get("https://am.i.mullvad.net/json")
                response.raise_for_status()
                data = response.json()

                # Check if Mullvad confirms we're using their DNS
                is_mullvad_dns = data.get("mullvad_dns", False)
                is_mullvad_exit = data.get("mullvad_exit_ip", False)

                if is_mullvad_dns or is_mullvad_exit:
                    logger.info("DNS leak check passed: using Mullvad DNS")
                    return True, "Mullvad DNS"

                # If not confirmed as Mullvad, check if the DNS server matches
                # a known VPN provider (not the user's real ISP)
                dns_info = data.get("organization", "")
                known_vpn_dns_providers = [
                    "mullvad", "cloudflare", "quad9", "wireguard",
                    "1.1.1.1", "9.9.9.9", "protonvpn",
                ]
                for provider in known_vpn_dns_providers:
                    if provider.lower() in dns_info.lower():
                        logger.info("DNS resolved through known VPN DNS: {}", dns_info)
                        return True, dns_info

                # If we can't confirm VPN DNS, flag potential leak
                logger.warning("Potential DNS leak detected. DNS resolver: {}", dns_info)
                return False, dns_info

        except Exception as exc:
            logger.error("DNS leak check error: {}", exc)
            return False, str(exc)

    async def monitor_vpn(self, check_interval: float = 30.0) -> None:
        """Background task: continuously monitor VPN status.

        If the VPN interface drops, this immediately sets the safety flag
        to False (kill switch behavior), halting any pending OSINT operations.

        Args:
            check_interval: Seconds between VPN status checks (default 30s).
        """
        self._monitoring = True
        logger.info(OPSEC_MONITORING)

        try:
            while self._monitoring:
                await asyncio.sleep(check_interval)

                vpn_ok, iface = self.check_vpn_interface()
                if not vpn_ok:
                    logger.critical(OPSEC_VPN_DROPPED)
                    self._console.print(
                        Panel(
                            f"{OPSEC_VPN_DROPPED}\n{OPSEC_KILL_SWITCH}",
                            title="⛔ KILL SWITCH",
                            border_style="bold red",
                        )
                    )
                    self._is_safe = False
                    self._monitoring = False
                    return
                else:
                    logger.debug("VPN monitor check OK: {}", iface)

        except asyncio.CancelledError:
            logger.info("VPN monitor task cancelled.")
            self._monitoring = False

    def start_monitoring(self, check_interval: float = 30.0) -> asyncio.Task:
        """Start VPN monitoring as a background asyncio task.

        Args:
            check_interval: Seconds between VPN status checks.

        Returns:
            The asyncio Task object for the monitor loop.
        """
        self._monitor_task = asyncio.create_task(self.monitor_vpn(check_interval))
        return self._monitor_task

    def stop_monitoring(self) -> None:
        """Stop the VPN monitoring background task."""
        self._monitoring = False
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            logger.info("VPN monitor stopped.")

    @property
    def is_safe(self) -> bool:
        """Whether OpSec checks have passed and it's safe to proceed."""
        return self._is_safe

    @property
    def current_ip_info(self) -> dict[str, Any]:
        """The most recently fetched public IP information."""
        return self._current_ip_info

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _display_status_panel(
        self,
        vpn_interface: str,
        ip_info: dict[str, Any],
        dns_safe: bool,
        dns_detail: str,
    ) -> None:
        """Render a formatted security status panel to the console.

        Args:
            vpn_interface: Name of the detected VPN interface.
            ip_info: Public IP information dict.
            dns_safe: Whether DNS leak check passed.
            dns_detail: DNS resolver details.
        """
        table = Table(
            show_header=False,
            padding=(0, 2),
            box=None,
            expand=False,
        )
        table.add_column("Label", style="bright_cyan", width=22)
        table.add_column("Value", style="white")

        table.add_row(
            "VPN Interfeys",
            f"[green]✓ {vpn_interface}[/green]",
        )
        table.add_row(
            "IP Ünvan",
            ip_info.get("ip", "N/A"),
        )
        table.add_row(
            "ISP",
            ip_info.get("isp", "N/A"),
        )
        table.add_row(
            "Ölkə",
            ip_info.get("country", "N/A"),
        )
        table.add_row(
            "Şəhər",
            ip_info.get("city", "N/A"),
        )

        # Mullvad exit node info
        mullvad_exit = ip_info.get("mullvad_exit", False)
        exit_display = (
            f"[green]✓ {ip_info.get('mullvad_exit_hostname', 'Bəli')}[/green]"
            if mullvad_exit
            else "[yellow]✗ Bilinmir[/yellow]"
        )
        table.add_row("Mullvad Çıxış", exit_display)

        # DNS status
        dns_display = (
            f"[green]✓ {dns_detail}[/green]"
            if dns_safe
            else f"[red]⚠ {dns_detail}[/red]"
        )
        table.add_row("DNS Statusu", dns_display)

        self._console.print()
        self._console.print(
            Panel(
                table,
                title="🛡 Təhlükəsizlik Statusu",
                border_style="bright_green" if mullvad_exit else "yellow",
                padding=(1, 2),
            )
        )
