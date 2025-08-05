import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from settings import settings


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
    # Use settings default if no URL provided
    if url is None:
        url = settings.frontend_base_url

    output_path = Path("output") / output_filename
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser
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

        try:
            # Navigate to URL and wait for load
            await page.goto(url, wait_until="networkidle")

            # Wait for React to render - use provided selector or fallback to general ones
            if selector:
                try:
                    await page.wait_for_selector(selector, timeout=10000)
                    print(f"✅ Found selector: {selector}")
                except Exception:
                    print(
                        f"⚠️ Selector '{selector}' not found, falling back to general content..."
                    )
                    await page.wait_for_function(
                        "document.body.children.length > 0", timeout=10000
                    )
            else:
                try:
                    # Try to wait for any main content container
                    await page.wait_for_selector(
                        ".notes-container, .canvas-container, .app-content, main",
                        timeout=10000,
                    )
                except Exception:
                    print(
                        "⚠️ No specific content selector found, waiting for general content..."
                    )
                    # Fallback: wait for any content in body
                    await page.wait_for_function(
                        "document.body.children.length > 0", timeout=10000
                    )

            # Additional wait for any async data loading
            await page.wait_for_timeout(2000)

            # Check if we actually have content
            content = await page.content()
            print(f"🔍 Page content length: {len(content)} characters")

            # Generate PDF
            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
            )

            print(f"✅ PDF saved to {output_path}")
            return str(output_path)

        finally:
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
