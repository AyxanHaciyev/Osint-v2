"""
core/dorking.py — Dork Query Generator & Search Orchestrator

Generates targeted dork queries from templates and target data, then
executes them across multiple search engines with full stealth rotation.
Deduplicates results and identifies documents for further analysis.

All queries are designed to look like normal human searches — no
automation markers, no rapid-fire patterns, natural engine rotation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from core.browser import StealthBrowser
from core.throttle import RequestThrottler
from ui.locale_az import (
    DORK_GENERATING,
    DORK_GENERATED,
    DORK_TEMPLATE_LOAD_ERROR,
    DORK_EXECUTING,
    DORK_RESULT_COUNT,
    DORK_CAMPAIGN_START,
    DORK_CAMPAIGN_PROGRESS,
    DORK_CAMPAIGN_COMPLETE,
    DORK_DEDUP_COUNT,
    DORK_DOCUMENT_FOUND,
    DORK_NO_RESULTS,
    DORK_LIMIT_REACHED,
    DORK_ENGINE_ROTATE,
)

# Document file extensions to detect in search results
_DOCUMENT_EXTENSIONS: set[str] = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls",
    ".pptx", ".ppt", ".odt", ".ods", ".csv",
    ".txt", ".rtf",
}

# Default dork template categories if the template file is missing
_FALLBACK_TEMPLATES: list[dict[str, Any]] = [
    {
        "category": "name_search",
        "priority": 1,
        "template": '"{first_name} {last_name}"',
        "engines": ["google", "duckduckgo", "bing"],
        "description": "Basic full name search",
    },
    {
        "category": "name_location",
        "priority": 2,
        "template": '"{first_name} {last_name}" "{location}"',
        "engines": ["google", "duckduckgo"],
        "description": "Name + location",
    },
    {
        "category": "name_employer",
        "priority": 2,
        "template": '"{first_name} {last_name}" "{employer}"',
        "engines": ["google", "bing"],
        "description": "Name + employer",
    },
    {
        "category": "username_search",
        "priority": 1,
        "template": '"{username}"',
        "engines": ["google", "duckduckgo", "bing"],
        "description": "Username search",
    },
    {
        "category": "document_discovery",
        "priority": 3,
        "template": '"{first_name} {last_name}" filetype:pdf',
        "engines": ["google", "bing"],
        "description": "PDF document discovery",
    },
    {
        "category": "document_discovery",
        "priority": 3,
        "template": '"{first_name} {last_name}" filetype:docx',
        "engines": ["google", "bing"],
        "description": "DOCX document discovery",
    },
    {
        "category": "linkedin",
        "priority": 2,
        "template": 'site:linkedin.com "{first_name} {last_name}"',
        "engines": ["google", "duckduckgo"],
        "description": "LinkedIn profile",
    },
    {
        "category": "social_media",
        "priority": 3,
        "template": 'site:github.com "{username}"',
        "engines": ["google"],
        "description": "GitHub profile",
    },
    {
        "category": "email_pattern",
        "priority": 4,
        "template": '"{email}"',
        "engines": ["google", "duckduckgo"],
        "description": "Email search",
    },
    {
        "category": "directory_index",
        "priority": 5,
        "template": 'intitle:"index of" "{first_name} {last_name}"',
        "engines": ["google"],
        "description": "Open directory search",
    },
    {
        "category": "az_regional",
        "priority": 3,
        "template": 'site:.az "{first_name} {last_name}"',
        "engines": ["google", "bing"],
        "description": "Azerbaijan domain search",
    },
]


class DorkEngine:
    """Dork query generator and search orchestrator.

    Generates targeted dork queries from templates filled with target data,
    then executes them across multiple search engines with intelligent rotation,
    throttling, and deduplication.

    Args:
        config: Dorking configuration from settings.yaml.
            Expected keys: max_results_per_query, search_engines, safe_mode.
        browser: StealthBrowser instance for executing searches.
        throttler: RequestThrottler instance for timing control.
        console: Rich Console instance for output.
    """

    def __init__(
        self,
        config: dict,
        browser: StealthBrowser,
        throttler: RequestThrottler,
        console: Console,
    ) -> None:
        self._config = config
        self._browser = browser
        self._throttler = throttler
        self._console = console

        self._max_results: int = config.get("max_results_per_query", 20)
        self._search_engines: list[str] = config.get(
            "search_engines", ["google", "duckduckgo", "bing"]
        )
        self._safe_mode: bool = config.get("safe_mode", True)

        # Templates loaded from file or fallback
        self._templates: list[dict[str, Any]] = []
        self._load_templates(config.get("templates_file", "data/dork_templates.json"))

        # Result tracking for deduplication
        self._seen_urls: set[str] = set()
        self._all_results: list[dict[str, Any]] = []

        logger.debug(
            "DorkEngine initialized: engines={}, max_results={}, templates={}",
            self._search_engines,
            self._max_results,
            len(self._templates),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_dorks(self, target_data: dict[str, str]) -> list[dict[str, Any]]:
        """Generate all dork queries from templates filled with target data.

        Takes the target's known data points and fills in the template
        placeholders to create executable dork queries. Skips templates
        where required data is missing. Results are sorted by priority.

        Args:
            target_data: Dictionary of known target data. Expected keys:
                first_name, last_name, username, email, location, employer,
                university, phone. All are optional — templates with
                missing data are simply skipped.

        Returns:
            List of dicts: {query, category, priority, engines, description}.
            Sorted by priority (1 = highest priority).
        """
        self._console.print(f"  [cyan]⟳[/cyan] {DORK_GENERATING}")
        logger.info("Generating dork queries for target data: {}", list(target_data.keys()))

        dorks: list[dict[str, Any]] = []

        for template in self._templates:
            try:
                query_template = template["template"]

                # Check if all required placeholders can be filled
                placeholders = re.findall(r'\{(\w+)\}', query_template)
                missing = [p for p in placeholders if not target_data.get(p)]

                if missing:
                    logger.debug(
                        "Skipping template '{}': missing data for {}",
                        template.get("description", "N/A"),
                        missing,
                    )
                    continue

                # Fill in the template with target data
                query = query_template.format(**target_data)

                # Clean and validate the query
                query = query.strip()
                if not query or len(query) < 3:
                    continue

                dorks.append({
                    "query": query,
                    "category": template.get("category", "general"),
                    "priority": template.get("priority", 5),
                    "engines": template.get("engines", self._search_engines),
                    "description": template.get("description", ""),
                })

            except KeyError as exc:
                logger.debug("Template key error: {}", exc)
                continue
            except Exception as exc:
                logger.warning("Error processing template: {}", exc)
                continue

        # Sort by priority (lower number = higher priority)
        dorks.sort(key=lambda d: d["priority"])

        self._console.print(
            f"  [green]✓[/green] {DORK_GENERATED.format(count=len(dorks))}"
        )
        logger.info("Generated {} dork queries from {} templates", len(dorks), len(self._templates))

        return dorks

    async def execute_search(
        self,
        dork: str,
        engine: str = "google",
    ) -> list[dict[str, str]]:
        """Execute a single dork query via the StealthBrowser.

        Applies throttling before the search, passes the query to the
        browser's search method, then deduplicates results against
        previously seen URLs.

        Args:
            dork: The dork query string to search.
            engine: Search engine to use ('google', 'duckduckgo', 'bing').

        Returns:
            List of new (non-duplicate) results: {title, url, snippet}.
        """
        if not self._throttler.can_query():
            self._console.print(f"  [yellow]⚠[/yellow] {DORK_LIMIT_REACHED}")
            logger.warning("Query limit reached, cannot execute search.")
            return []

        logger.info(DORK_EXECUTING, dork[:60], engine)
        self._console.print(f"  [dim]› Axtarış edilir ({engine}):[/dim] [white]{dork[:50]}[/white]...")

        # Throttle — wait with human-like delay
        domain = urlparse(f"https://{engine}.com").hostname or engine
        await self._throttler.wait(domain=domain)

        # Execute the search
        results = await self._browser.search(engine, dork)

        # Record the query
        self._throttler.record_query(domain=domain)

        # Deduplicate against previously seen URLs
        new_results: list[dict[str, str]] = []
        for result in results:
            url = result.get("url", "")
            normalized_url = self._normalize_url(url)
            if normalized_url and normalized_url not in self._seen_urls:
                self._seen_urls.add(normalized_url)
                new_results.append(result)

            self._console.print(f"    [green]✓ {len(new_results)} yeni nəticə tapıldı.[/green]")
            logger.info(
                DORK_RESULT_COUNT,
                len(new_results),
                len(results) - len(new_results),
            )
        else:
            logger.debug(DORK_NO_RESULTS, dork[:50])

        return new_results

    async def run_campaign(
        self,
        target_data: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Run a full dorking campaign across all engines.

        Generates all dorks, executes them with intelligent engine rotation,
        deduplicates the final results, and identifies any documents found.

        Args:
            target_data: Dictionary of target data for dork generation.

        Returns:
            Consolidated list of all results with document detection flags.
            Each result: {title, url, snippet, engine, query, is_document,
                          document_type}.
        """
        self._console.print(f"\n  [bold cyan]{DORK_CAMPAIGN_START}[/bold cyan]")
        logger.info("Starting dorking campaign...")

        # Generate all dork queries
        dorks = self.generate_dorks(target_data)
        if not dorks:
            logger.warning("No dork queries generated — insufficient target data.")
            return []

        all_results: list[dict[str, Any]] = []
        engine_index = 0

        # Display progress
        total_queries = sum(len(d["engines"]) for d in dorks)
        queries_executed = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self._console.console,
        ) as progress:
            task = progress.add_task(
                DORK_CAMPAIGN_PROGRESS,
                total=total_queries,
            )

            for dork_info in dorks:
                if not self._throttler.can_query():
                    self._console.print(f"  [yellow]⚠[/yellow] {DORK_LIMIT_REACHED}")
                    break

                query = dork_info["query"]
                engines = dork_info["engines"]

                for engine in engines:
                    if not self._throttler.can_query():
                        break

                    # Rotate engines to avoid hammering one
                    logger.debug(DORK_ENGINE_ROTATE, engine, query[:40])

                    try:
                        results = await self.execute_search(query, engine)

                        for result in results:
                            enriched = {
                                **result,
                                "engine": engine,
                                "query": query,
                                "category": dork_info["category"],
                                "is_document": False,
                                "document_type": None,
                            }
                            all_results.append(enriched)

                    except Exception as exc:
                        logger.error("Search error for '{}' on {}: {}", query[:40], engine, exc)

                    queries_executed += 1
                    progress.update(task, completed=queries_executed)

        # Detect documents in results
        doc_results = self.detect_documents(all_results)
        doc_count = sum(1 for r in all_results if r.get("is_document", False))

        # Store all results
        self._all_results.extend(all_results)

        # Display summary
        self._display_campaign_summary(all_results, doc_count)

        self._console.print(
            f"\n  [green]✓[/green] {DORK_CAMPAIGN_COMPLETE.format(total=len(all_results), docs=doc_count)}"
        )
        logger.info(
            "Campaign complete: {} total results, {} documents found, {} queries used",
            len(all_results),
            doc_count,
            queries_executed,
        )

        return all_results

    def detect_documents(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Identify document links in search results.

        Scans URLs and titles for document file extensions and marks
        matching results with is_document=True and the detected file type.

        Args:
            results: List of search result dicts to scan.

        Returns:
            Subset of results that are documents (also mutates the originals
            to set is_document and document_type fields).
        """
        documents: list[dict[str, Any]] = []

        for result in results:
            url = result.get("url", "").lower()
            title = result.get("title", "").lower()

            # Check URL for document extensions
            parsed = urlparse(url)
            path = parsed.path.lower()

            for ext in _DOCUMENT_EXTENSIONS:
                if path.endswith(ext) or ext[1:] in title:
                    result["is_document"] = True
                    result["document_type"] = ext.lstrip(".")
                    documents.append(result)

                    self._console.print(
                        f"    [yellow]📄[/yellow] {DORK_DOCUMENT_FOUND.format(doc_type=ext.lstrip('.').upper(), url=url[:80])}"
                    )
                    logger.info("Document found: {} ({})", url[:80], ext)
                    break

            # Also check for "filetype:" or "index of" indicators in snippet
            snippet = result.get("snippet", "").lower()
            if not result.get("is_document") and any(
                kw in snippet for kw in ["download pdf", "скачать", "yüklə", "download doc"]
            ):
                result["is_document"] = True
                result["document_type"] = "unknown"
                documents.append(result)

        return documents

    @property
    def seen_url_count(self) -> int:
        """Number of unique URLs seen across all searches."""
        return len(self._seen_urls)

    @property
    def all_results(self) -> list[dict[str, Any]]:
        """All accumulated results from this engine's lifetime."""
        return list(self._all_results)

    def reset(self) -> None:
        """Reset all result tracking for a new campaign."""
        self._seen_urls.clear()
        self._all_results.clear()
        logger.info("DorkEngine reset: cleared all result tracking.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_templates(self, filepath: str) -> None:
        """Load dork templates from a JSON file.

        Falls back to built-in templates if the file is missing or invalid.

        Args:
            filepath: Path to the dork_templates.json file.
        """
        try:
            template_path = Path(filepath)
            if not template_path.is_absolute():
                template_path = Path(__file__).resolve().parent.parent / filepath

            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Support both flat list and categorized structure
                if isinstance(data, list):
                    self._templates = data
                elif isinstance(data, dict):
                    # Flatten categories into a single list
                    templates = []
                    for category, items in data.items():
                        if isinstance(items, list):
                            for item in items:
                                item.setdefault("category", category)
                                templates.append(item)
                    self._templates = templates
                else:
                    raise ValueError(f"Unexpected template format: {type(data)}")

                logger.info("Loaded {} dork templates from {}", len(self._templates), template_path)
                return

            logger.warning(DORK_TEMPLATE_LOAD_ERROR, str(template_path))

        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in dork templates: {}", exc)
        except Exception as exc:
            logger.error("Error loading dork templates: {}", exc)

        # Fallback to built-in templates
        self._templates = list(_FALLBACK_TEMPLATES)
        logger.info("Using {} built-in fallback dork templates", len(self._templates))

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize a URL for deduplication.

        Strips trailing slashes, query parameters (except meaningful ones),
        and fragments to identify the same page under different URLs.

        Args:
            url: The URL to normalize.

        Returns:
            Normalized URL string, or empty string if invalid.
        """
        if not url:
            return ""

        try:
            parsed = urlparse(url)
            # Keep scheme, netloc, path (strip trailing slash)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
            return normalized.lower()
        except Exception:
            return url.lower().strip()

    def _display_campaign_summary(
        self,
        results: list[dict[str, Any]],
        doc_count: int,
    ) -> None:
        """Display a summary table of campaign results.

        Args:
            results: All search results from the campaign.
            doc_count: Number of documents detected.
        """
        # Aggregate by category
        categories: dict[str, int] = {}
        engines_used: dict[str, int] = {}

        for r in results:
            cat = r.get("category", "unknown")
            eng = r.get("engine", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            engines_used[eng] = engines_used.get(eng, 0) + 1

        table = Table(
            title="📊 Nəticə xülasəsi",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Kateqoriya", style="bright_white")
        table.add_column("Nəticə sayı", justify="right", style="green")

        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            table.add_row(cat, str(count))

        table.add_row("─" * 20, "─" * 10, style="dim")
        table.add_row("[bold]CƏMİ[/bold]", f"[bold]{len(results)}[/bold]")
        table.add_row("[bold]📄 Sənədlər[/bold]", f"[bold yellow]{doc_count}[/bold yellow]")

        self._console.print()
        self._console.print(table)
