"""KƏŞF — Təkrar istifadə olunan Rich panel komponentləri.

Bütün panellər vahid rəng sxemi ilə stilləşdirilib:
  • Əsas:    cyan / teal (#00d4aa)
  • Xəbərdarlıq: yellow
  • Xəta:    red / bright_red
  • Uğur:    green / bright_green
  • Məlumat: bright_cyan
  • Haşiyə:  bright_cyan / dim
"""

from __future__ import annotations

from rich.align import Align
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from ui import locale_az as L

# ─── Theme Constants ──────────────────────────────────────────
PRIMARY = "#00d4aa"
PRIMARY_BOLD = "bold #00d4aa"
ACCENT = "#00b4d8"
ACCENT_BOLD = "bold #00b4d8"
BORDER_COLOR = "bright_cyan"
DIM_BORDER = "dim cyan"
HEADER_BG = "on #0a2a2a"
SUCCESS = "bold bright_green"
WARNING = "bold yellow"
ERROR = "bold bright_red"
MUTED = "dim white"
LABEL_STYLE = "bold white"
VALUE_STYLE = "#00d4aa"
PANEL_PADDING = (1, 2)


# ══════════════════════════════════════════════════════════════
#  HEADER PANEL
# ══════════════════════════════════════════════════════════════

def create_header_panel() -> Panel:
    """Əsas proqram başlığı — gradient-style haşiyə ilə."""

    title_text = Text()
    title_text.append("██╗  ██╗", style=PRIMARY)
    title_text.append(" ")
    title_text.append("██████╗ ", style=ACCENT)
    title_text.append("███████╗", style=PRIMARY)
    title_text.append("███████╗\n", style=ACCENT)
    title_text.append("██║ ██╔╝", style=PRIMARY)
    title_text.append(" ")
    title_text.append("██╔════╝", style=ACCENT)
    title_text.append(" ██╔════╝", style=PRIMARY)
    title_text.append("██╔════╝\n", style=ACCENT)
    title_text.append("█████╔╝ ", style=PRIMARY)
    title_text.append(" ")
    title_text.append("████████╗", style=ACCENT)
    title_text.append("███████╗", style=PRIMARY)
    title_text.append("█████╗\n", style=ACCENT)
    title_text.append("██╔═██╗ ", style=PRIMARY)
    title_text.append(" ")
    title_text.append("╚════██║", style=ACCENT)
    title_text.append("╚════██║", style=PRIMARY)
    title_text.append("██╔══╝\n", style=ACCENT)
    title_text.append("██║  ██╗", style=PRIMARY)
    title_text.append(" ")
    title_text.append("██████╔╝", style=ACCENT)
    title_text.append("███████║", style=PRIMARY)
    title_text.append("██║\n", style=ACCENT)
    title_text.append("╚═╝  ╚═╝", style=PRIMARY)
    title_text.append(" ")
    title_text.append("╚═════╝ ", style=ACCENT)
    title_text.append("╚══════╝", style=PRIMARY)
    title_text.append("╚═╝\n", style=ACCENT)

    subtitle = Text()
    subtitle.append(f"\n{L.APP_FULL_NAME}\n", style=PRIMARY_BOLD)
    subtitle.append(L.APP_SUBTITLE, style=MUTED)
    subtitle.append(f"   v{L.APP_VERSION}", style="dim cyan")

    content = Text()
    content.append_text(title_text)
    content.append_text(subtitle)

    return Panel(
        Align.center(content),
        border_style=BORDER_COLOR,
        padding=PANEL_PADDING,
        title=f"[{PRIMARY_BOLD}]═══ {L.APP_NAME} ═══[/]",
        subtitle=f"[{MUTED}]{L.APP_DISCLAIMER}[/]",
    )


# ══════════════════════════════════════════════════════════════
#  OPSEC PANEL
# ══════════════════════════════════════════════════════════════

def create_opsec_panel(data: dict) -> Panel:
    """VPN / IP vəziyyəti paneli.

    Parameters
    ----------
    data : dict
        Keys: vpn_active (bool), vpn_interface (str),
              ip (str), isp (str), country (str), city (str),
              dns_safe (bool), dns_server (str | None)
    """
    table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    table.add_column("label", style=LABEL_STYLE, width=22)
    table.add_column("value", style=VALUE_STYLE)

    vpn_active: bool = data.get("vpn_active", False)
    vpn_style = SUCCESS if vpn_active else ERROR

    table.add_row(
        "🛡  VPN Vəziyyəti",
        Text(
            L.OPSEC_VPN_ACTIVE.format(interface=data.get("vpn_interface", "—"))
            if vpn_active
            else L.OPSEC_VPN_NOT_FOUND,
            style=vpn_style,
        ),
    )
    table.add_row(
        "🌐 IP / ISP",
        L.OPSEC_IP_INFO.format(
            ip=data.get("ip", "—"),
            isp=data.get("isp", "—"),
            country=data.get("country", "—"),
            city=data.get("city", "—"),
        ),
    )

    dns_safe: bool = data.get("dns_safe", True)
    dns_style = SUCCESS if dns_safe else WARNING
    dns_text = (
        L.OPSEC_DNS_SAFE
        if dns_safe
        else L.OPSEC_DNS_LEAK.format(dns=data.get("dns_server", "—"))
    )
    table.add_row("🔒 DNS Vəziyyəti", Text(dns_text, style=dns_style))

    border = BORDER_COLOR if vpn_active else "bright_red"
    return Panel(
        table,
        title=f"[{PRIMARY_BOLD}]🛡  OpSec Vəziyyəti[/]",
        border_style=border,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  TARGET PANEL
# ══════════════════════════════════════════════════════════════

def create_target_panel(target: dict) -> Panel:
    """Hədəf məlumatları paneli.

    Parameters
    ----------
    target : dict
        Keys match the field names: first_name, last_name,
        middle_name, username, email, phone, employer,
        university, city, country, extra
    """
    _field_map = [
        ("👤 Ad",              "first_name"),
        ("👤 Soyad",           "last_name"),
        ("👤 Ata adı",         "middle_name"),
        ("🆔 İstifadəçi adı", "username"),
        ("📧 E-poçt",         "email"),
        ("📞 Telefon",         "phone"),
        ("🏢 İş yeri",        "employer"),
        ("🎓 Universitet",    "university"),
        ("📍 Şəhər",          "city"),
        ("🌍 Ölkə",           "country"),
        ("📝 Əlavə",          "extra"),
    ]

    table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    table.add_column("label", style=LABEL_STYLE, width=22)
    table.add_column("value", style=VALUE_STYLE)

    for label, key in _field_map:
        value = target.get(key)
        if value:
            table.add_row(label, str(value))

    return Panel(
        table,
        title=f"[{PRIMARY_BOLD}]🎯 {L.INPUT_HEADER}[/]",
        border_style=BORDER_COLOR,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  SEARCH PANEL
# ══════════════════════════════════════════════════════════════

def create_search_panel(engine: str, query: str, status: str) -> Panel:
    """Cari axtarış paneli.

    Parameters
    ----------
    engine : str   — axtarış motoru adı (Google, Bing, …)
    query  : str   — axtarış sorğusu
    status : str   — vəziyyət mesajı
    """
    content = Text()
    content.append("🔍 ", style=PRIMARY)
    content.append(L.DORK_ENGINE.format(engine=engine), style=LABEL_STYLE)
    content.append("\n")
    content.append("📝 ", style=PRIMARY)
    content.append(L.DORK_QUERY.format(query=query), style=VALUE_STYLE)
    content.append("\n")
    content.append("📊 ", style=PRIMARY)
    content.append(status, style=MUTED)

    return Panel(
        content,
        title=f"[{PRIMARY_BOLD}]🔍 Axtarış[/]",
        border_style=BORDER_COLOR,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  DOCUMENT PANEL
# ══════════════════════════════════════════════════════════════

def create_document_panel(doc_info: dict) -> Panel:
    """Sənəd aşkarlanması paneli.

    Parameters
    ----------
    doc_info : dict
        Keys: filename, url, context, size, file_type (optional)
    """
    table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    table.add_column("label", style=LABEL_STYLE, width=18)
    table.add_column("value", style=VALUE_STYLE)

    table.add_row("📄 Fayl", doc_info.get("filename", "—"))
    table.add_row("🔗 URL", doc_info.get("url", "—"))
    table.add_row("📝 Kontekst", doc_info.get("context", "—"))
    table.add_row("📏 Ölçü", doc_info.get("size", "—"))
    if doc_info.get("file_type"):
        table.add_row("📎 Növ", doc_info["file_type"])

    return Panel(
        table,
        title=f"[{WARNING}]📄 {L.DOC_FOUND}[/]",
        border_style="yellow",
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  GRAPH / INTELLIGENCE PANEL
# ══════════════════════════════════════════════════════════════

def create_graph_panel(nodes: int, edges: int, confidence: float) -> Panel:
    """Kəşfiyyat qrafı xülasə paneli."""

    tree = Tree(
        f"[{PRIMARY_BOLD}]🧠 Kəşfiyyat Qrafı[/]",
        guide_style=DIM_BORDER,
    )
    tree.add(f"[{LABEL_STYLE}]Node sayı:[/]  [{VALUE_STYLE}]{nodes}[/]")
    tree.add(f"[{LABEL_STYLE}]Edge sayı:[/]  [{VALUE_STYLE}]{edges}[/]")

    conf_color = SUCCESS if confidence >= 70 else (WARNING if confidence >= 40 else ERROR)
    tree.add(
        f"[{LABEL_STYLE}]Etibar:[/]     [{conf_color}]{confidence:.1f}%[/]"
    )

    # Mini progress bar for confidence
    bar_width = 30
    filled = int(bar_width * confidence / 100)
    empty = bar_width - filled
    bar = Text()
    bar.append("  ▐", style=MUTED)
    bar.append("█" * filled, style=conf_color)
    bar.append("░" * empty, style=MUTED)
    bar.append("▌", style=MUTED)
    bar.append(f" {confidence:.1f}%", style=conf_color)
    tree.add(bar)

    return Panel(
        tree,
        title=f"[{PRIMARY_BOLD}]📊 {L.REPORT_GRAPH}[/]",
        border_style=BORDER_COLOR,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  SESSION PANEL
# ══════════════════════════════════════════════════════════════

def create_session_panel(session_data: dict) -> Panel:
    """Sessiya vəziyyəti paneli.

    Parameters
    ----------
    session_data : dict
        Keys: session_id, duration, query_count, max_queries,
              graph_nodes, graph_edges, confidence
    """
    table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    table.add_column("label", style=LABEL_STYLE, width=22)
    table.add_column("value", style=VALUE_STYLE)

    table.add_row("📅 Sessiya ID", session_data.get("session_id", "—"))
    table.add_row("⏱  Müddət", session_data.get("duration", "—"))

    qc = session_data.get("query_count", 0)
    mq = session_data.get("max_queries", 0)
    q_style = VALUE_STYLE if qc < mq * 0.8 else (WARNING if qc < mq else ERROR)
    table.add_row(
        "📊 Sorğular",
        Text(L.THROTTLE_QUERY_COUNT.format(current=qc, max=mq), style=q_style),
    )

    nodes = session_data.get("graph_nodes", 0)
    edges = session_data.get("graph_edges", 0)
    conf = session_data.get("confidence", 0)
    table.add_row(
        "🧠 Qraf",
        L.INTEL_GRAPH_STATS.format(nodes=nodes, edges=edges, confidence=conf),
    )

    return Panel(
        table,
        title=f"[{PRIMARY_BOLD}]📋 Sessiya Vəziyyəti[/]",
        border_style=BORDER_COLOR,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  RESULTS TABLE PANEL
# ══════════════════════════════════════════════════════════════

def create_results_panel(results: list[dict], title: str = "Nəticələr") -> Panel:
    """Axtarış nəticələri paneli (cədvəl).

    Parameters
    ----------
    results : list[dict]
        Each dict: {url, title, snippet, source}
    title : str
        Panelistartını təyin edir.
    """
    table = Table(
        show_lines=True,
        border_style=DIM_BORDER,
        header_style=PRIMARY_BOLD,
        expand=True,
    )
    table.add_column("#", style=MUTED, width=4, justify="right")
    table.add_column("Başlıq", style=LABEL_STYLE, ratio=3)
    table.add_column("URL", style=VALUE_STYLE, ratio=4)
    table.add_column("Mənbə", style=MUTED, width=12)

    for idx, r in enumerate(results, 1):
        table.add_row(
            str(idx),
            r.get("title", "—"),
            r.get("url", "—"),
            r.get("source", "—"),
        )

    return Panel(
        table,
        title=f"[{PRIMARY_BOLD}]📋 {title}[/]",
        border_style=BORDER_COLOR,
        padding=(1, 1),
    )


# ══════════════════════════════════════════════════════════════
#  INTELLIGENCE UPDATE PANEL
# ══════════════════════════════════════════════════════════════

def create_intelligence_panel(
    nodes: int,
    edges: int,
    new_pivots: int,
    depth: int,
    max_depth: int | None = None,
) -> Panel:
    """Kəşfiyyat mühərriki yeniləmə paneli."""

    content = Text()
    content.append("🧠 ", style=PRIMARY)
    content.append("Kəşfiyyat Mühərriki Yeniləməsi\n\n", style=PRIMARY_BOLD)
    content.append(f"  📊 Node:          ", style=LABEL_STYLE)
    content.append(f"{nodes}\n", style=VALUE_STYLE)
    content.append(f"  🔗 Edge:          ", style=LABEL_STYLE)
    content.append(f"{edges}\n", style=VALUE_STYLE)
    content.append(f"  🔄 Yeni Pivotlar: ", style=LABEL_STYLE)
    content.append(f"{new_pivots}\n", style=VALUE_STYLE)

    depth_str = f"{depth}/{max_depth}" if max_depth else str(depth)
    content.append(f"  🔍 Dərinlik:      ", style=LABEL_STYLE)
    content.append(f"{depth_str}\n", style=VALUE_STYLE)

    return Panel(
        content,
        title=f"[{PRIMARY_BOLD}]🧠 Kəşfiyyat[/]",
        border_style=BORDER_COLOR,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  REPORT SUMMARY PANEL
# ══════════════════════════════════════════════════════════════

def create_report_panel(report_data: dict) -> Panel:
    """Hesabat xülasəsi paneli.

    Parameters
    ----------
    report_data : dict
        Keys: title, session_id, date, total_queries,
              total_documents, total_pivots, sources
    """
    content = Text()
    content.append(f"📊 {L.REPORT_TITLE}\n\n", style=PRIMARY_BOLD)
    content.append(f"  📅 Tarix:         ", style=LABEL_STYLE)
    content.append(f"{report_data.get('date', '—')}\n", style=VALUE_STYLE)
    content.append(f"  📋 Sessiya:       ", style=LABEL_STYLE)
    content.append(f"{report_data.get('session_id', '—')}\n", style=VALUE_STYLE)
    content.append(f"  🔍 Sorğular:      ", style=LABEL_STYLE)
    content.append(f"{report_data.get('total_queries', 0)}\n", style=VALUE_STYLE)
    content.append(f"  📄 Sənədlər:      ", style=LABEL_STYLE)
    content.append(f"{report_data.get('total_documents', 0)}\n", style=VALUE_STYLE)
    content.append(f"  🔄 Pivotlar:      ", style=LABEL_STYLE)
    content.append(f"{report_data.get('total_pivots', 0)}\n", style=VALUE_STYLE)
    content.append(f"  📚 Mənbələr:      ", style=LABEL_STYLE)
    content.append(f"{report_data.get('sources', 0)}\n", style=VALUE_STYLE)

    return Panel(
        content,
        title=f"[{PRIMARY_BOLD}]📊 {L.REPORT_SUMMARY}[/]",
        border_style=BORDER_COLOR,
        padding=(1, 2),
    )


# ══════════════════════════════════════════════════════════════
#  ERROR / WARNING / INFO PANELS (compact)
# ══════════════════════════════════════════════════════════════

def create_error_panel(message: str) -> Panel:
    """Xəta paneli."""
    return Panel(
        Text(f"❌  {message}", style=ERROR),
        border_style="bright_red",
        title=f"[{ERROR}]Xəta[/]",
        padding=(0, 2),
    )


def create_warning_panel(message: str) -> Panel:
    """Xəbərdarlıq paneli."""
    return Panel(
        Text(f"⚠   {message}", style=WARNING),
        border_style="yellow",
        title=f"[{WARNING}]Xəbərdarlıq[/]",
        padding=(0, 2),
    )


def create_info_panel(message: str) -> Panel:
    """Məlumat paneli."""
    return Panel(
        Text(f"ℹ   {message}", style="bright_cyan"),
        border_style=BORDER_COLOR,
        title=f"[bold bright_cyan]Məlumat[/]",
        padding=(0, 2),
    )


def create_success_panel(message: str) -> Panel:
    """Uğur paneli."""
    return Panel(
        Text(f"✅  {message}", style=SUCCESS),
        border_style="bright_green",
        title=f"[{SUCCESS}]Uğurlu[/]",
        padding=(0, 2),
    )
