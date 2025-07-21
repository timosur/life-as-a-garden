import base64
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def print_garden_to_pdf(
    url: str = "http://localhost:5173/", output_filename: str = "Lebensgarten.pdf"
) -> str:
    """
    Print a garden page to PDF using headless Chrome.

    Args:
        url: The URL to print
        output_filename: The name of the output PDF file

    Returns:
        str: The absolute path to the generated PDF file
    """
    output_path = Path("output") / output_filename
    output_path = output_path.resolve()

    # Set up headless Chrome with PDF printing enabled
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Start browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Load the website
        driver.get(url)

        # Wait until body is fully loaded
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Optional: extra delay for JS-heavy pages
        except Exception as e:
            print("Warning: Timeout waiting for page to load:", e)

        # Generate PDF via DevTools Protocol
        pdf_data = driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "printBackground": True,
                "landscape": False,
                "paperWidth": 8.27,  # A4 size
                "paperHeight": 11.69,
            },
        )

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(pdf_data["data"]))

        print(f"✅ PDF saved to {output_path}")
        return str(output_path)

    finally:
        driver.quit()
