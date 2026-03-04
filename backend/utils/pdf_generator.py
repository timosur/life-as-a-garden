import asyncio
import aiohttp
from pathlib import Path
from playwright.async_api import async_playwright
from settings import settings

# Backend URL for direct API access (bypasses nginx auth/rate-limiting)
BACKEND_DIRECT_URL = "http://localhost:8000"


async def _proxy_api_request(route, backend_url: str):
    """Intercept browser API calls and forward directly to the backend, bypassing nginx."""
    request = route.request
    path = request.url.split("/api/", 1)[1]
    target_url = f"{backend_url}/api/{path}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ("host",)},
                data=request.post_data if request.method != "GET" else None,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                body = await resp.read()
                await route.fulfill(
                    status=resp.status,
                    headers=dict(resp.headers),
                    body=body,
                )
    except Exception as e:
        print(f"❌ API proxy failed for {target_url}: {e}")
        await route.abort("connectionrefused")


async def print_to_pdf(
    url: str = None, output_filename: str = "Lebensgarten.pdf", selector: str = None
) -> str:
    """
    Print a page to PDF using Playwright.

    Args:
        url: The URL to print (defaults to frontend_url from settings)
        output_filename: The name of the output PDF file
        selector: CSS selector to wait for before generating PDF

    Returns:
        str: The absolute path to the generated PDF file
    """
    if url is None:
        url = settings.frontend_base_url

    output_path = Path("output") / output_filename
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    console_messages = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
            ],
        )

        page = await browser.new_page()

        # Capture browser console logs for debugging
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_messages.append(f"[PAGE_ERROR] {err}"))

        # Intercept /api/* requests and route directly to backend, bypassing nginx
        await page.route("**/api/**", lambda route: _proxy_api_request(route, BACKEND_DIRECT_URL))

        try:
            print(f"🌐 Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)

            if selector:
                try:
                    await page.wait_for_selector(selector, timeout=30000)
                    print(f"✅ Found selector: {selector}")
                except Exception:
                    if console_messages:
                        print("📋 Browser console output:")
                        for msg in console_messages:
                            print(f"   {msg}")

                    raise RuntimeError(
                        f"Required selector '{selector}' not found after 30s. "
                        f"The page likely failed to load data. Check console output above."
                    )
            else:
                try:
                    await page.wait_for_selector(
                        ".notes-container, .canvas-container, .app-content, main",
                        timeout=10000,
                    )
                except Exception:
                    print(
                        "⚠️ No specific content selector found, waiting for general content..."
                    )
                    await page.wait_for_function(
                        "document.body.children.length > 0", timeout=10000
                    )

            # Additional wait for any async data loading
            await page.wait_for_timeout(2000)

            content = await page.content()
            print(f"🔍 Page content length: {len(content)} characters")

            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
            )

            print(f"✅ PDF saved to {output_path}")
            return str(output_path)

        finally:
            if console_messages:
                print("📋 Browser console output:")
                for msg in console_messages:
                    print(f"   {msg}")
            await browser.close()


def print_garden_to_pdf_sync(
    url: str = None, output_filename: str = "Lebensgarten.pdf"
) -> str:
    """
    Synchronous wrapper for the async PDF generation function.
    """
    return asyncio.run(print_to_pdf(url, output_filename, selector=".page-garden"))


def print_notes_to_pdf_sync(output_filename: str = "Notes.pdf") -> str:
    """
    Generate a PDF from the notes page.

    Args:
        output_filename: The name of the output PDF file

    Returns:
        str: The absolute path to the generated PDF file
    """
    notes_url = f"{settings.frontend_base_url}notes"
    print(f"📄 Printing notes to PDF at {notes_url}...")
    return asyncio.run(
        print_to_pdf(notes_url, output_filename, selector=".no-notes, .note-card")
    )
