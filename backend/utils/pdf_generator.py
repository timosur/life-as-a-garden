import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from settings import settings


async def print_garden_to_pdf(
    url: str = None, output_filename: str = "Lebensgarten.pdf"
) -> str:
    """
    Print a garden page to PDF using Playwright.

    Args:
        url: The URL to print (defaults to frontend_url from settings)
        output_filename: The name of the output PDF file

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
    return asyncio.run(print_garden_to_pdf(url, output_filename))
