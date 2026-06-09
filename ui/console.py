"""KƏŞF — Əsas konsol render modulu.

`rich` kitabxanasını əhatə edən `KESFConsole` sinfi vasitəsilə
bütün terminal çıxışları idarə olunur.

Rəng sxemi:
  • Əsas:      cyan / teal  (#00d4aa)
  • Arxa fon:  (terminal default — tünd tövsiyə olunur)
  • Xəbərdarlıq: yellow
  • Xəta:      red / bright_red
  • Uğur:      green / bright_green
"""

from __future__ import annotations

from typing import Any

from rich.align import Align
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from ui import locale_az as L
from ui.panels import (
    PRIMARY,
    PRIMARY_BOLD,
    ACCENT,
    ACCENT_BOLD,
    BORDER_COLOR,
    DIM_BORDER,
    SUCCESS,
    WARNING,
    ERROR,
    MUTED,
    LABEL_STYLE,
    VALUE_STYLE,
    create_header_panel,
    create_opsec_panel,
    create_target_panel,
    create_search_panel,
    create_document_panel,
    create_graph_panel,
    create_session_panel,
    create_results_panel,
    create_intelligence_panel,
    create_error_panel,
    create_warning_panel,
    create_info_panel,
    create_success_panel,
)


# ─── Custom Rich Theme ───────────────────────────────────────

_KESF_THEME = Theme(
    {
        "kesf.primary": "#00d4aa",
        "kesf.accent": "#00b4d8",
        "kesf.success": "bright_green",
        "kesf.warning": "yellow",
        "kesf.error": "bright_red",
        "kesf.muted": "dim white",
        "kesf.label": "bold white",
        "kesf.value": "#00d4aa",
        "kesf.header": "bold #00d4aa on #0a2a2a",
        "kesf.border": "bright_cyan",
    }
)


class KESFConsole:
    """KƏŞF layihəsinin əsas konsol fasadı.

    Bütün terminal çıxışları bu sinif vasitəsilə keçir.
    Rich kitabxanasının Panel, Table, Progress, Text və s.
    komponentlərindən istifadə edir.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._console = Console(theme=_KESF_THEME, **kwargs)

    # ─── Proxied helpers ──────────────────────────────────────

    @property
    def console(self) -> Console:
        """Daxili `rich.console.Console` obyektinə birbaşa giriş."""
        return self._console

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Birbaşa `Console.print` proxy-si."""
        self._console.print(*args, **kwargs)

    def rule(self, title: str = "", **kwargs: Any) -> None:
        """Horizontal ayırıcı xətt."""
        self._console.rule(title, style=DIM_BORDER, **kwargs)

    def blank(self, count: int = 1) -> None:
        """Boş sətir(lər) çap edir."""
        for _ in range(count):
            self._console.print()

    # ══════════════════════════════════════════════════════════
    #  BANNER
    # ══════════════════════════════════════════════════════════

    def show_banner(self) -> None:
        """Proqramın giriş banner-ini göstərir — ASCII art + versiya."""
        self.blank()
        self._console.print(create_header_panel())
        self.blank()

    # ══════════════════════════════════════════════════════════
    #  OPSEC STATUS
    # ══════════════════════════════════════════════════════════

    def show_opsec_status(
        self,
        ip: str,
        isp: str,
        country: str,
        city: str,
        vpn_interface: str | None = None,
        dns_safe: bool = True,
        dns_server: str | None = None,
    ) -> None:
        """VPN / IP / DNS vəziyyəti panelini göstərir."""
        data = {
            "vpn_active": vpn_interface is not None,
            "vpn_interface": vpn_interface or "—",
            "ip": ip,
            "isp": isp,
            "country": country,
            "city": city,
            "dns_safe": dns_safe,
            "dns_server": dns_server,
        }
        self._console.print(create_opsec_panel(data))

    # ══════════════════════════════════════════════════════════
    #  SESSION STATUS
    # ══════════════════════════════════════════════════════════

    def show_session_status(
        self,
        session_id: str,
        duration: str,
        query_count: int,
        max_queries: int,
        graph_nodes: int = 0,
        graph_edges: int = 0,
        confidence: float = 0.0,
    ) -> None:
        """Canlı sessiya vəziyyəti zolağını göstərir."""
        data = {
            "session_id": session_id,
            "duration": duration,
            "query_count": query_count,
            "max_queries": max_queries,
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges,
            "confidence": confidence,
        }
        self._console.print(create_session_panel(data))

    # ══════════════════════════════════════════════════════════
    #  TARGET SUMMARY
    # ══════════════════════════════════════════════════════════

    def show_target_summary(self, target_data: dict) -> None:
        """Hədəf məlumatlarının formatlanmış cədvəlini göstərir."""
        self._console.print(create_target_panel(target_data))

    # ══════════════════════════════════════════════════════════
    #  CONFIRM PROMPT  (B/X)
    # ══════════════════════════════════════════════════════════

    def prompt_confirm(self, message: str) -> bool:
        """Azerbaijani B/X təsdiq sorğusu.

        Returns True əgər istifadəçi "B" (Bəli) cavab verərsə.
        """
        while True:
            answer = self._console.input(
                f"[{PRIMARY_BOLD}]{message}[/] "
            ).strip().upper()
            if answer == L.GENERAL_YES:
                return True
            if answer == L.GENERAL_NO:
                return False
            self._console.print(
                f"[{WARNING}]{L.GENERAL_INVALID_INPUT}[/]"
            )

    # ══════════════════════════════════════════════════════════
    #  SEARCH PROGRESS
    # ══════════════════════════════════════════════════════════

    def show_search_progress(
        self,
        engine: str,
        query: str,
        results_count: int,
    ) -> None:
        """Cari axtarış gedişatını göstərir."""
        status = L.DORK_RESULTS_FOUND.format(count=results_count)
        self._console.print(create_search_panel(engine, query, status))

    # ══════════════════════════════════════════════════════════
    #  DOCUMENT FOUND
    # ══════════════════════════════════════════════════════════

    def show_document_found(
        self,
        filename: str,
        url: str,
        context: str,
        size: str,
        file_type: str | None = None,
    ) -> None:
        """Sənəd aşkarlanması xəbərdarlıq panelini göstərir."""
        doc_info = {
            "filename": filename,
            "url": url,
            "context": context,
            "size": size,
            "file_type": file_type,
        }
        self._console.print(create_document_panel(doc_info))

    # ══════════════════════════════════════════════════════════
    #  RESULTS TABLE
    # ══════════════════════════════════════════════════════════

    def show_results_table(
        self,
        results: list[dict],
        title: str = "Axtarış Nəticələri",
    ) -> None:
        """Axtarış nəticələrini Rich cədvəli olaraq göstərir.

        Parameters
        ----------
        results : list[dict]
            Each dict: {url, title, snippet, source}
        """
        if not results:
            self.show_info(L.DORK_NO_RESULTS)
            return
        self._console.print(create_results_panel(results, title=title))
        self._console.print(
            f"  [{MUTED}]{L.DORK_COMPLETE.format(total=len(results))}[/]"
        )

    # ══════════════════════════════════════════════════════════
    #  INTELLIGENCE UPDATE
    # ══════════════════════════════════════════════════════════

    def show_intelligence_update(
        self,
        nodes: int,
        edges: int,
        new_pivots: int,
        depth: int,
        max_depth: int | None = None,
    ) -> None:
        """Kəşfiyyat mühərriki yeniləmə panelini göstərir."""
        self._console.print(
            create_intelligence_panel(nodes, edges, new_pivots, depth, max_depth)
        )

    # ══════════════════════════════════════════════════════════
    #  GRAPH PANEL
    # ══════════════════════════════════════════════════════════

    def show_graph_summary(
        self,
        nodes: int,
        edges: int,
        confidence: float,
    ) -> None:
        """Kəşfiyyat qrafı xülasə panelini göstərir."""
        self._console.print(create_graph_panel(nodes, edges, confidence))

    # ══════════════════════════════════════════════════════════
    #  STATUS MESSAGES
    # ══════════════════════════════════════════════════════════

    def show_error(self, message: str) -> None:
        """Xəta mesajını panel daxilində göstərir."""
        self._console.print(create_error_panel(message))

    def show_warning(self, message: str) -> None:
        """Xəbərdarlıq mesajını panel daxilində göstərir."""
        self._console.print(create_warning_panel(message))

    def show_success(self, message: str) -> None:
        """Uğur mesajını panel daxilində göstərir."""
        self._console.print(create_success_panel(message))

    def show_info(self, message: str) -> None:
        """Məlumat mesajını panel daxilində göstərir."""
        self._console.print(create_info_panel(message))

    # ══════════════════════════════════════════════════════════
    #  INLINE STATUS (no panel)
    # ══════════════════════════════════════════════════════════

    def status_line(self, message: str, style: str = PRIMARY) -> None:
        """Tək sətirlik vəziyyət mesajı (panel olmadan)."""
        self._console.print(f"  [{style}]{message}[/]")

    def step(self, message: str) -> None:
        """Addım mesajı — kiçik ok işarəsi ilə."""
        self._console.print(f"  [dim]›[/] [{VALUE_STYLE}]{message}[/]")

    # ══════════════════════════════════════════════════════════
    #  PROGRESS BAR CONTEXT MANAGER
    # ══════════════════════════════════════════════════════════

    def progress(self, description: str = L.GENERAL_LOADING) -> Progress:
        """Geri qaytarılan `Progress` kontekst meneceri.

        Usage::

            with console.progress("Yüklənir") as prog:
                task = prog.add_task("items", total=100)
                for i in range(100):
                    prog.advance(task)
        """
        return Progress(
            SpinnerColumn("dots", style=PRIMARY),
            TextColumn(f"[{PRIMARY_BOLD}]{description}[/]"),
            BarColumn(bar_width=40, style=DIM_BORDER, complete_style=PRIMARY),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self._console,
        )

    # ══════════════════════════════════════════════════════════
    #  SPINNER CONTEXT MANAGER
    # ══════════════════════════════════════════════════════════

    def spinner(self, message: str = L.GENERAL_PROCESSING):
        """Rich status spinner kontekst meneceri.

        Usage::

            with console.spinner("Yüklənir..."):
                do_work()
        """
        return self._console.status(
            f"[{PRIMARY_BOLD}]{message}[/]",
            spinner="dots",
            spinner_style=PRIMARY,
        )

    # ══════════════════════════════════════════════════════════
    #  MENU
    # ══════════════════════════════════════════════════════════

    def show_menu(self, title: str, options: list[str]) -> int:
        """Nömrələnmiş menyu göstərir və seçimi geri qaytarır.

        Returns
        -------
        int
            Seçilmiş elementin 0-bazalı indeksi.
        """
        self.blank()
        self.rule(title)
        for idx, option in enumerate(options, 1):
            self._console.print(
                f"  [{PRIMARY_BOLD}]{idx}.[/]  [{LABEL_STYLE}]{option}[/]"
            )
        self.rule()

        while True:
            try:
                choice = int(
                    self._console.input(f"  [{PRIMARY_BOLD}]{L.MENU_CHOOSE}[/]")
                )
                if 1 <= choice <= len(options):
                    return choice - 1
            except ValueError:
                pass
            self._console.print(f"  [{WARNING}]{L.MENU_INVALID}[/]")

    # ══════════════════════════════════════════════════════════
    #  TARGET INPUT FORM
    # ══════════════════════════════════════════════════════════

    def collect_target_data(self) -> dict | None:
        """İnteraktiv hədəf məlumat forması.

        İstifadəçidən hədəf haqqında məlumat toplayır.
        Təsdiqlənərsə dict qaytarır, rədd edilərsə None.
        """
        self.blank()
        self.rule(L.INPUT_HEADER)
        self.blank()

        fields = {
            "first_name":  L.INPUT_FIRST_NAME,
            "last_name":   L.INPUT_LAST_NAME,
            "middle_name": L.INPUT_MIDDLE_NAME,
            "username":    L.INPUT_USERNAME,
            "email":       L.INPUT_EMAIL,
            "phone":       L.INPUT_PHONE,
            "employer":    L.INPUT_EMPLOYER,
            "university":  L.INPUT_UNIVERSITY,
            "city":        L.INPUT_CITY,
            "country":     L.INPUT_COUNTRY,
            "extra":       L.INPUT_EXTRA,
        }

        data: dict[str, str] = {}
        for key, prompt in fields.items():
            value = self._console.input(
                f"  [{PRIMARY_BOLD}]{prompt}[/]"
            ).strip()
            if value:
                data[key] = value

        # Default country
        if "country" not in data:
            data["country"] = "Azərbaycan"

        # Validate required fields
        if not data.get("first_name") or not data.get("last_name"):
            self.show_warning(L.INPUT_EMPTY_WARNING)
            return None

        self.blank()
        self.show_target_summary(data)
        self.blank()

        if self.prompt_confirm(L.INPUT_CONFIRM):
            return data

        self.show_info(L.GENERAL_CANCELLED)
        return None

    # ══════════════════════════════════════════════════════════
    #  DASHBOARD (composite)
    # ══════════════════════════════════════════════════════════

    def show_dashboard(
        self,
        opsec_data: dict,
        session_data: dict,
        target_data: dict | None = None,
    ) -> None:
        """Bütün statusları bir baxışda göstərən dashboard.

        OpSec paneli + Sessiya paneli yan-yana,
        altında hədəf paneli (əgər varsa).
        """
        top_panels = Columns(
            [
                create_opsec_panel(opsec_data),
                create_session_panel(session_data),
            ],
            equal=True,
            expand=True,
        )
        self._console.print(top_panels)

        if target_data:
            self._console.print(create_target_panel(target_data))

    # ══════════════════════════════════════════════════════════
    #  FAREWELL
    # ══════════════════════════════════════════════════════════

    def show_farewell(self) -> None:
        """Çıxış mesajı."""
        self.blank()
        self.rule()
        self._console.print(
            Align.center(
                Text(L.GENERAL_EXIT, style=PRIMARY_BOLD)
            )
        )
        self.rule()
        self.blank()
