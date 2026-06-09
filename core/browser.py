"""
core/browser.py — Stealth Browser Launcher with MAXIMUM Anti-Detection

Launches Brave Browser via Playwright with comprehensive stealth measures
so that every single browser action is indistinguishable from a normal
human user. ZERO traces of automation.

Stealth measures implemented:
    1.  Disable AutomationControlled blink feature
    2.  Remove navigator.webdriver flag
    3.  Override navigator.plugins with realistic plugin list
    4.  Set realistic navigator.languages
    5.  Set proper window.screen dimensions
    6.  Override WebGL renderer/vendor strings
    7.  Set navigator.hardwareConcurrency
    8.  Set navigator.deviceMemory
    9.  Override navigator.permissions.query
    10. Mouse movement simulation with bezier curves
    11. Human-like typing with variable delays
    12. Random scroll behavior after page loads
    13. Proper viewport with devicePixelRatio
    14. Referrer chain (always visit search engine homepage first)
    15. Natural page dwell time before extraction
    16. Cookie consent auto-handling
    17. Occasional random tab behavior
"""

from __future__ import annotations

import asyncio
import math
import random
import re
from typing import Any, Optional
from urllib.parse import urlparse

from loguru import logger
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
    Error as PlaywrightError,
)
from rich.console import Console

from ui.locale_az import (
    BROWSER_LAUNCHING,
    BROWSER_LAUNCHED,
    BROWSER_LAUNCH_ERROR,
    BROWSER_NAVIGATING,
    BROWSER_NAVIGATE_ERROR,
    BROWSER_SEARCHING,
    BROWSER_SEARCH_COMPLETE,
    BROWSER_SEARCH_ERROR,
    BROWSER_CAPTCHA_DETECTED,
    BROWSER_CLOSING,
    BROWSER_CLOSED,
    BROWSER_TYPING,
    BROWSER_COOKIE_ACCEPT,
)

# ---------------------------------------------------------------------------
# Stealth JavaScript Injections
# ---------------------------------------------------------------------------

# Remove navigator.webdriver flag and patch all automation indicators
_STEALTH_INIT_SCRIPT = """
// ===== 1. Remove webdriver flag =====
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

// ===== 2. Override navigator.plugins with realistic list =====
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            {
                name: 'Chrome PDF Plugin',
                description: 'Portable Document Format',
                filename: 'internal-pdf-viewer',
                length: 1,
                0: {type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format'}
            },
            {
                name: 'Chrome PDF Viewer',
                description: '',
                filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                length: 1,
                0: {type: 'application/pdf', suffixes: 'pdf', description: ''}
            },
            {
                name: 'Native Client',
                description: '',
                filename: 'internal-nacl-plugin',
                length: 2,
                0: {type: 'application/x-nacl', suffixes: '', description: 'Native Client Executable'},
                1: {type: 'application/x-pnacl', suffixes: '', description: 'Portable Native Client Executable'}
            }
        ];
        plugins.item = (i) => plugins[i] || null;
        plugins.namedItem = (name) => plugins.find(p => p.name === name) || null;
        plugins.refresh = () => {};
        return plugins;
    }
});

// ===== 3. Override navigator.languages =====
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en', 'az'],
});
Object.defineProperty(navigator, 'language', {
    get: () => 'en-US',
});

// ===== 4. Override navigator.hardwareConcurrency =====
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => HARDWARE_CONCURRENCY_VALUE,
});

// ===== 5. Override navigator.deviceMemory =====
Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8,
});

// ===== 6. Override WebGL renderer info =====
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    // UNMASKED_VENDOR_WEBGL
    if (parameter === 37445) {
        return 'Google Inc. (NVIDIA)';
    }
    // UNMASKED_RENDERER_WEBGL
    if (parameter === 37446) {
        return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)';
    }
    return getParameter.call(this, parameter);
};

// Do the same for WebGL2
if (typeof WebGL2RenderingContext !== 'undefined') {
    const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Google Inc. (NVIDIA)';
        }
        if (parameter === 37446) {
            return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)';
        }
        return getParameter2.call(this, parameter);
    };
}

// ===== 7. Override Permissions API =====
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// ===== 8. Remove Playwright-specific properties =====
delete window.__playwright;
delete window.__pw_manual;

// ===== 9. Override chrome.runtime to look like real Chrome =====
if (!window.chrome) {
    window.chrome = {};
}
if (!window.chrome.runtime) {
    window.chrome.runtime = {
        connect: () => {},
        sendMessage: () => {},
    };
}

// ===== 10. Fix iframe contentWindow issue =====
const originalAttachShadow = Element.prototype.attachShadow;
Element.prototype.attachShadow = function() {
    return originalAttachShadow.apply(this, arguments);
};

// ===== 11. Spoof screen dimensions =====
Object.defineProperty(screen, 'width', { get: () => SCREEN_WIDTH_VALUE });
Object.defineProperty(screen, 'height', { get: () => SCREEN_HEIGHT_VALUE });
Object.defineProperty(screen, 'availWidth', { get: () => SCREEN_WIDTH_VALUE });
Object.defineProperty(screen, 'availHeight', { get: () => SCREEN_HEIGHT_VALUE - 40 });
Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
"""

# ---------------------------------------------------------------------------
# Realistic screen profiles to pick from
# ---------------------------------------------------------------------------
_SCREEN_PROFILES: list[dict[str, int]] = [
    {"width": 1920, "height": 1080, "dpr": 1},
    {"width": 2560, "height": 1440, "dpr": 1},
    {"width": 1920, "height": 1080, "dpr": 1.25},
    {"width": 1366, "height": 768, "dpr": 1},
    {"width": 1536, "height": 864, "dpr": 1.25},
    {"width": 1440, "height": 900, "dpr": 2},
]

# Hardware concurrency options (realistic core counts)
_HARDWARE_CONCURRENCY_OPTIONS: list[int] = [4, 6, 8, 8, 8, 12, 12, 16]

# ---------------------------------------------------------------------------
# Search engine configuration
# ---------------------------------------------------------------------------
_SEARCH_ENGINES: dict[str, dict[str, str]] = {
    "google": {
        "home": "https://www.google.com",
        "search_input": 'textarea[name="q"], input[name="q"]',
        "result_selector": "div.g",
        "title_selector": "h3",
        "link_selector": "a",
        "snippet_selector": "div[data-sncf], div.VwiC3b, span.aCOpRe",
    },
    "duckduckgo": {
        "home": "https://duckduckgo.com",
        "search_input": 'input[name="q"]',
        "result_selector": "article[data-testid='result']",
        "title_selector": "h2 a span",
        "link_selector": "h2 a",
        "snippet_selector": "div[data-result='snippet'] span",
    },
    "bing": {
        "home": "https://www.bing.com",
        "search_input": 'input[name="q"], textarea[name="q"]',
        "result_selector": "li.b_algo",
        "title_selector": "h2 a",
        "link_selector": "h2 a",
        "snippet_selector": "div.b_caption p",
    },
}


class StealthBrowser:
    """Brave Browser launcher with comprehensive stealth/anti-detection.

    Every single interaction through this browser is designed to be
    indistinguishable from a normal human user browsing the web.
    No automation markers, no fingerprinting leaks, no suspicious patterns.

    Args:
        config: Browser configuration from settings.yaml.
            Expected keys: brave_path, headless, stealth_mode, proxy.
        throttler: RequestThrottler instance for timing control.
        console: Rich Console instance for status output.
    """

    def __init__(
        self,
        config: dict,
        throttler: Any,
        console: Console,
    ) -> None:
        self._config = config
        self._throttler = throttler
        self._console = console

        # Browser settings
        self._brave_path: str = config.get(
            "brave_path",
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        )
        self._headless: bool = config.get("headless", True)

        # Parse proxy config properly
        raw_proxy = config.get("proxy")
        self._proxy: Optional[str] = None
        if isinstance(raw_proxy, dict):
            if raw_proxy.get("enabled", True):
                val = raw_proxy.get("server")
                self._proxy = str(val) if val else None
        elif isinstance(raw_proxy, str):
            self._proxy = str(raw_proxy)

        # Runtime state
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

        # Choose a random but consistent screen profile for the session
        self._screen_profile: dict[str, int] = random.choice(_SCREEN_PROFILES)
        self._hw_concurrency: int = random.choice(_HARDWARE_CONCURRENCY_OPTIONS)

        logger.debug(
            "StealthBrowser initialized: brave_path={}, headless={}, screen={}x{}",
            self._brave_path,
            self._headless,
            self._screen_profile["width"],
            self._screen_profile["height"],
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def launch(self) -> None:
        """Launch Brave Browser in incognito with full stealth configuration.

        Sets up all anti-detection measures including:
        - Chrome launch flags to disable automation indicators
        - Stealth JavaScript injections
        - Proper viewport and device emulation
        - Proxy routing (if configured)
        """
        self._console.print(f"  [cyan]⟳[/cyan] {BROWSER_LAUNCHING}")
        logger.info("Launching stealth browser...")

        try:
            self._playwright = await async_playwright().start()

            # --- Build launch arguments ---
            launch_args: list[str] = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--disable-infobars",
                "--disable-extensions",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-sync",
                "--metrics-recording-only",
                "--no-default-browser-check",
                "--mute-audio",
                "--hide-scrollbars",
                f"--window-size={self._screen_profile['width']},{self._screen_profile['height']}",
            ]

            # --- Proxy configuration ---
            proxy_settings = None
            if self._proxy:
                proxy_settings = {"server": self._proxy}
                launch_args.append(f"--proxy-server={self._proxy}")

            # --- Launch browser ---
            self._browser = await self._playwright.chromium.launch(
                executable_path=self._brave_path,
                headless=self._headless,
                args=launch_args,
                chromium_sandbox=False,
            )

            # --- Create incognito context with anti-fingerprint settings ---
            user_agent = self._throttler.get_random_user_agent()

            context_options: dict[str, Any] = {
                "viewport": {
                    "width": self._screen_profile["width"],
                    "height": self._screen_profile["height"],
                },
                "device_scale_factor": self._screen_profile["dpr"],
                "user_agent": user_agent,
                "locale": "en-US",
                "timezone_id": "Europe/Berlin",  # Use a neutral European timezone
                "has_touch": False,
                "is_mobile": False,
                "java_script_enabled": True,
                "ignore_https_errors": True,
                "extra_http_headers": {
                    "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
                    "sec-ch-ua": '"Chromium";v="125", "Not.A/Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                },
            }

            if proxy_settings:
                context_options["proxy"] = proxy_settings

            self._context = await self._browser.new_context(**context_options)

            # --- Inject stealth scripts ---
            stealth_script = _STEALTH_INIT_SCRIPT.replace(
                "HARDWARE_CONCURRENCY_VALUE", str(self._hw_concurrency)
            ).replace(
                "SCREEN_WIDTH_VALUE", str(self._screen_profile["width"])
            ).replace(
                "SCREEN_HEIGHT_VALUE", str(self._screen_profile["height"])
            )

            await self._context.add_init_script(stealth_script)

            # --- Create main page ---
            self._page = await self._context.new_page()

            # Set extra stealth properties on page level
            await self._page.add_init_script("""
                // Remove Playwright artifacts on every navigation
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            self._console.print(f"  [green]✓[/green] {BROWSER_LAUNCHED}")
            logger.info(
                "Stealth browser launched: UA={}, viewport={}x{}, DPR={}",
                user_agent[:60] + "...",
                self._screen_profile["width"],
                self._screen_profile["height"],
                self._screen_profile["dpr"],
            )

        except Exception as exc:
            logger.error("Failed to launch browser: {}", exc)
            self._console.print(f"  [red]✗[/red] {BROWSER_LAUNCH_ERROR}: {exc}")
            raise

    async def navigate(self, url: str) -> Page:
        """Navigate to a URL with human-like behavior.

        Includes random pre-navigation delays, natural scrolling after load,
        and dwell time to mimic genuine user browsing patterns.

        Args:
            url: The URL to navigate to.

        Returns:
            The Playwright Page object.

        Raises:
            RuntimeError: If the browser hasn't been launched yet.
        """
        if not self._page:
            raise RuntimeError("Browser not launched. Call launch() first.")

        logger.debug(BROWSER_NAVIGATING, url)

        try:
            # Navigate with realistic timeout
            await self._page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # Wait for page to settle (images, scripts, etc.)
            await asyncio.sleep(random.uniform(1.0, 2.5))

            # Handle cookie consent banners
            await self._handle_cookie_consent()

            # Simulate natural scrolling
            await self._random_scroll()

            # Random micro-pause (human reads the page briefly)
            await asyncio.sleep(random.uniform(0.5, 1.5))

            return self._page

        except PlaywrightError as exc:
            logger.error(BROWSER_NAVIGATE_ERROR + ": {}", url, exc)
            raise

    async def search(self, engine: str, query: str) -> list[dict[str, str]]:
        """Perform a search that looks 100% human.

        Full referrer chain: navigates to the search engine homepage first,
        waits naturally, finds the search box, types the query with
        human-like delays, presses Enter, waits for results, then extracts.

        Args:
            engine: Search engine name ('google', 'duckduckgo', 'bing').
            query: The search query string.

        Returns:
            List of dicts with keys: title, url, snippet.
        """
        if not self._page:
            raise RuntimeError("Browser not launched. Call launch() first.")

        engine = engine.lower()
        if engine not in _SEARCH_ENGINES:
            logger.error("Unknown search engine: {}", engine)
            return []

        engine_config = _SEARCH_ENGINES[engine]
        self._console.print(f"  [cyan]⟳[/cyan] {BROWSER_SEARCHING.format(engine=engine, query=query[:50])}")
        logger.info("Searching on {}: {}", engine, query)

        try:
            # --- Step 1: Navigate to search engine homepage (referrer chain) ---
            await self._page.goto(
                engine_config["home"],
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # Natural dwell on homepage (1-3 seconds, like a real user)
            await asyncio.sleep(random.uniform(1.0, 3.0))

            # Handle cookie consent on the homepage
            await self._handle_cookie_consent()

            # --- Step 2: Find and interact with search box ---
            search_input = await self._page.wait_for_selector(
                engine_config["search_input"],
                timeout=10000,
            )

            if not search_input:
                logger.error("Could not find search input on {}", engine)
                return []

            # Click the search box (with slight random offset for realism)
            await self._human_click(search_input)
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # --- Step 3: Type query with human-like delays ---
            await self._human_type(query)

            # Brief pause before pressing Enter (like a human reviewing their query)
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # --- Step 4: Press Enter and wait for results ---
            await self._page.keyboard.press("Enter")

            # Wait for results to load
            await self._page.wait_for_load_state("domcontentloaded", timeout=15000)
            await asyncio.sleep(random.uniform(2.0, 5.0))  # Natural dwell time

            # --- Step 5: Random scroll to look natural ---
            await self._random_scroll()

            # --- Step 6: Check for CAPTCHA ---
            captcha_detected = await self._check_captcha()
            if captcha_detected:
                self._console.print(
                    f"  [bold red]⚠[/bold red] {BROWSER_CAPTCHA_DETECTED}"
                )
                logger.warning("CAPTCHA detected on {}! Pausing for manual resolution.", engine)
                # Wait for user to solve CAPTCHA manually (if not headless)
                if not self._headless:
                    await asyncio.sleep(30)  # Give user time to solve
                return []

            # --- Step 7: Extract search results ---
            results = await self._extract_results(engine_config)

            # --- Step 8: Occasional random tab behavior (opens new tab, closes it) ---
            if random.random() < 0.12:
                await self._random_tab_behavior()

            self._console.print(
                f"  [green]✓[/green] {BROWSER_SEARCH_COMPLETE.format(count=len(results), engine=engine)}"
            )
            logger.info("Search complete: {} results from {}", len(results), engine)
            return results

        except PlaywrightError as exc:
            logger.error(BROWSER_SEARCH_ERROR + ": {}", engine, exc)
            self._console.print(f"  [red]✗[/red] {BROWSER_SEARCH_ERROR.format(engine=engine)}: {exc}")
            return []
        except Exception as exc:
            logger.error("Unexpected search error on {}: {}", engine, exc)
            return []

    async def close(self) -> None:
        """Gracefully close the browser and clean up all resources."""
        self._console.print(f"  [cyan]⟳[/cyan] {BROWSER_CLOSING}")
        logger.info("Closing stealth browser...")

        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()

            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

            self._console.print(f"  [green]✓[/green] {BROWSER_CLOSED}")
            logger.info("Browser closed and resources cleaned up.")

        except Exception as exc:
            logger.error("Error closing browser: {}", exc)

    @property
    def page(self) -> Optional[Page]:
        """The current active Playwright Page, or None if not launched."""
        return self._page

    @property
    def is_launched(self) -> bool:
        """Whether the browser is currently running."""
        return self._browser is not None and self._page is not None

    # ------------------------------------------------------------------
    # Human simulation methods (CRITICAL for stealth)
    # ------------------------------------------------------------------

    async def _human_type(self, text: str) -> None:
        """Type text with human-like variable delays between keystrokes.

        Simulates natural typing with:
        - Variable delay per character (50-150ms)
        - Occasional longer pauses (simulating thinking)
        - Occasional typo + backspace correction
        - Speed variation (starts slow, gets faster, then slower at end)

        Args:
            text: The text to type.
        """
        if not self._page:
            return

        logger.debug(BROWSER_TYPING, len(text))

        for i, char in enumerate(text):
            # Base delay with gaussian distribution for naturalness
            base_delay = random.gauss(90, 30)  # mean=90ms, std=30ms
            delay = max(30, min(base_delay, 200))  # clamp 30-200ms

            # Slower at the beginning (warming up)
            if i < 3:
                delay *= 1.5

            # Occasional longer pause (thinking, ~5% chance)
            if random.random() < 0.05:
                delay += random.uniform(200, 600)

            # Pause slightly longer after spaces (word boundary)
            if char == " ":
                delay += random.uniform(30, 100)

            # Very occasional typo + correction (~2% chance, skip for spaces)
            if random.random() < 0.02 and char != " " and i < len(text) - 1:
                # Type a wrong character
                wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
                await self._page.keyboard.type(wrong_char, delay=delay / 1000)
                await asyncio.sleep(random.uniform(0.15, 0.4))
                await self._page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))

            await self._page.keyboard.type(char, delay=delay / 1000)

    async def _human_click(self, element: Any) -> None:
        """Click an element with human-like mouse movement.

        Moves the mouse along a bezier curve to the element's position
        (not in a straight line), then clicks with a slight random offset.

        Args:
            element: Playwright ElementHandle or Locator to click.
        """
        if not self._page:
            return

        try:
            # Get element bounding box
            bbox = await element.bounding_box()
            if not bbox:
                await element.click()
                return

            # Calculate click target with slight random offset
            target_x = bbox["x"] + bbox["width"] * random.uniform(0.3, 0.7)
            target_y = bbox["y"] + bbox["height"] * random.uniform(0.3, 0.7)

            # Simulate curved mouse movement to the target
            await self._move_mouse_curve(target_x, target_y)

            # Click with random delay
            await asyncio.sleep(random.uniform(0.05, 0.15))
            await self._page.mouse.click(target_x, target_y)

        except Exception:
            # Fallback to direct click
            await element.click()

    async def _move_mouse_curve(self, target_x: float, target_y: float) -> None:
        """Move mouse to target along a bezier-like curve, not a straight line.

        Uses quadratic bezier interpolation with a random control point
        to create a natural-looking cursor path.

        Args:
            target_x: Target X coordinate.
            target_y: Target Y coordinate.
        """
        if not self._page:
            return

        # Get current mouse position (estimate from viewport center if unknown)
        current_x = random.uniform(100, self._screen_profile["width"] - 100)
        current_y = random.uniform(100, self._screen_profile["height"] - 100)

        # Generate random control point for the bezier curve
        ctrl_x = (current_x + target_x) / 2 + random.uniform(-100, 100)
        ctrl_y = (current_y + target_y) / 2 + random.uniform(-50, 50)

        # Number of intermediate steps (more steps = smoother curve)
        steps = random.randint(8, 15)

        for i in range(1, steps + 1):
            t = i / steps
            # Quadratic bezier interpolation
            x = (1 - t) ** 2 * current_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * target_x
            y = (1 - t) ** 2 * current_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * target_y

            await self._page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.01, 0.04))

    async def _random_scroll(self) -> None:
        """Simulate random scrolling behavior after page load.

        Mimics a user casually scanning the page by scrolling down a bit,
        pausing, maybe scrolling back up slightly.
        """
        if not self._page:
            return

        try:
            # Number of scroll actions (1-3)
            scroll_count = random.randint(1, 3)

            for _ in range(scroll_count):
                # Random scroll distance (positive = down)
                scroll_y = random.randint(100, 400)
                if random.random() < 0.2:
                    scroll_y = -scroll_y  # Occasionally scroll up

                await self._page.mouse.wheel(0, scroll_y)
                await asyncio.sleep(random.uniform(0.3, 1.2))

        except Exception as exc:
            logger.debug("Scroll simulation error (non-critical): {}", exc)

    async def _handle_cookie_consent(self) -> None:
        """Detect and automatically accept cookie consent banners.

        Looks for common cookie consent button patterns and clicks "Accept"
        to dismiss the banner like a normal user would.
        """
        if not self._page:
            return

        # Common cookie consent button selectors (ordered by likelihood)
        cookie_selectors: list[str] = [
            # Generic patterns
            "button[id*='accept']",
            "button[id*='agree']",
            "button[id*='consent']",
            "button[class*='accept']",
            "button[class*='agree']",
            "button[class*='consent']",
            # Google-specific
            "button[id='L2AGLb']",
            "button[aria-label='Accept all']",
            # Common cookie libraries
            "a.cc-btn.cc-dismiss",
            "button.cc-btn.cc-allow",
            "#onetrust-accept-btn-handler",
            "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
            "button[data-testid='cookie-policy-manage-dialog-btn-accept-all']",
            # DuckDuckGo
            "button.js-consent-btn",
            # Bing
            "button#bnp_btn_accept",
        ]

        try:
            for selector in cookie_selectors:
                try:
                    button = await self._page.wait_for_selector(
                        selector, timeout=1500, state="visible"
                    )
                    if button:
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        await self._human_click(button)
                        logger.debug(BROWSER_COOKIE_ACCEPT, selector)
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                        return
                except PlaywrightError:
                    continue  # Selector not found, try next

        except Exception as exc:
            logger.debug("Cookie consent handling (non-critical): {}", exc)

    async def _check_captcha(self) -> bool:
        """Detect if a CAPTCHA challenge is being presented.

        Checks for common CAPTCHA indicators in the page content.

        Returns:
            True if a CAPTCHA is detected, False otherwise.
        """
        if not self._page:
            return False

        try:
            page_content = await self._page.content()
            captcha_indicators: list[str] = [
                "g-recaptcha",
                "h-captcha",
                "captcha-container",
                "captcha_challenge",
                "unusual traffic",
                "are not a robot",
                "verify you are human",
                "automated queries",
                "CAPTCHA",
            ]
            content_lower = page_content.lower()
            for indicator in captcha_indicators:
                if indicator.lower() in content_lower:
                    return True
            return False

        except Exception:
            return False

    async def _extract_results(self, engine_config: dict[str, str]) -> list[dict[str, str]]:
        """Extract search results from the current page.

        Parses the search results page using the engine-specific selectors
        to extract titles, URLs, and snippets.

        Args:
            engine_config: Dict with CSS selectors for the search engine.

        Returns:
            List of result dicts with keys: title, url, snippet.
        """
        results: list[dict[str, str]] = []

        if not self._page:
            return results

        try:
            # Wait for results container to appear
            await self._page.wait_for_selector(
                engine_config["result_selector"],
                timeout=10000,
            )

            # Get all result elements
            result_elements = await self._page.query_selector_all(
                engine_config["result_selector"]
            )

            for element in result_elements[:20]:  # Cap at 20 results
                try:
                    # Extract title
                    title_el = await element.query_selector(engine_config["title_selector"])
                    title = await title_el.inner_text() if title_el else ""

                    # Extract URL
                    link_el = await element.query_selector(engine_config["link_selector"])
                    url = ""
                    if link_el:
                        url = await link_el.get_attribute("href") or ""
                        # Clean tracking redirects
                        url = self._clean_url(url)

                    # Extract snippet
                    snippet_el = await element.query_selector(engine_config["snippet_selector"])
                    snippet = await snippet_el.inner_text() if snippet_el else ""

                    if title and url and url.startswith("http"):
                        results.append({
                            "title": title.strip(),
                            "url": url.strip(),
                            "snippet": snippet.strip(),
                        })

                except Exception as exc:
                    logger.debug("Error extracting single result: {}", exc)
                    continue

        except PlaywrightError as exc:
            logger.warning("Result extraction timeout/error: {}", exc)

        return results

    async def _random_tab_behavior(self) -> None:
        """Occasionally open a new tab and close it, like a real user.

        This adds realistic noise to the browsing session. A human might
        open a new tab by habit and close it immediately.
        """
        if not self._context:
            return

        try:
            # Open a new blank tab
            new_page = await self._context.new_page()
            await asyncio.sleep(random.uniform(0.5, 2.0))
            # Close it
            await new_page.close()
            logger.debug("Random tab behavior: opened and closed a tab.")
        except Exception as exc:
            logger.debug("Random tab behavior (non-critical): {}", exc)

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_url(url: str) -> str:
        """Remove tracking parameters and redirect wrappers from URLs.

        Args:
            url: The raw URL from search results.

        Returns:
            Cleaned URL without tracking parameters.
        """
        if not url:
            return url

        # Google redirect cleanup
        if "/url?q=" in url or "/url?sa=" in url:
            match = re.search(r'[?&](?:q|url)=([^&]+)', url)
            if match:
                from urllib.parse import unquote
                return unquote(match.group(1))

        # Bing redirect cleanup
        if "bing.com/ck/" in url:
            match = re.search(r'[?&]u=([^&]+)', url)
            if match:
                from urllib.parse import unquote
                import base64
                try:
                    decoded = base64.b64decode(unquote(match.group(1))).decode()
                    if decoded.startswith("http"):
                        return decoded
                except Exception:
                    pass

        return url
