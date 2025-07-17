import base64
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI(title="Life as a Garden API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Garden data structure
garden_data = {
    "areals": [
        {
            "id": "core-family",
            "name": "Core Family",
            "horizontalPos": "left",
            "verticalPos": "bottom",
            "size": "large",
            "plants": [
                {
                    "name": "Bobo",
                    "health": "healthy",
                    "imagePath": "rose",
                    "size": "big",
                    "position": "top",
                },
                {
                    "name": "Finja",
                    "health": "healthy",
                    "imagePath": "sunflower",
                    "size": "big",
                    "position": "left",
                },
                {
                    "name": "Mats",
                    "health": "healthy",
                    "imagePath": "happy-bamboo",
                    "size": "big",
                    "position": "right",
                },
                {
                    "name": "Mama",
                    "health": "healthy",
                    "imagePath": "lavendel",
                    "size": "medium",
                    "position": "center",
                },
                {
                    "name": "Papa",
                    "health": "okay",
                    "imagePath": "cactus",
                    "size": "small",
                    "position": "bottom",
                },
            ],
        },
        {
            "id": "sport",
            "name": "Sport",
            "horizontalPos": "right",
            "verticalPos": "bottom",
            "size": "large",
            "plants": [
                {
                    "name": "Fahrrad fahren",
                    "health": "healthy",
                    "imagePath": "thymian",
                    "size": "big",
                    "position": "top",
                },
                {
                    "name": "Joggen",
                    "health": "okay",
                    "imagePath": "oat-grass",
                    "size": "big",
                    "position": "center",
                },
                {
                    "name": "Klettern",
                    "health": "healthy",
                    "imagePath": "hop",
                    "size": "big",
                    "position": "left",
                },
                {
                    "name": "Yoga",
                    "health": "healthy",
                    "imagePath": "lotus-flower",
                    "size": "medium",
                    "position": "right",
                },
                {
                    "name": "Schwimmen",
                    "health": "okay",
                    "imagePath": "water-hyacinth",
                    "size": "medium",
                    "position": "bottom-left",
                },
                {
                    "name": "Fußball",
                    "health": "dead",
                    "imagePath": "grass",
                    "size": "small",
                    "position": "bottom-right",
                },
            ],
        },
        {
            "id": "mental-health",
            "name": "Mental Health",
            "horizontalPos": "left",
            "verticalPos": "middle",
            "size": "large",
            "plants": [
                {
                    "name": "Meditation",
                    "health": "healthy",
                    "imagePath": "bonsai",
                    "size": "big",
                    "position": "center",
                },
                {
                    "name": "Lesen",
                    "health": "healthy",
                    "imagePath": "ivy",
                    "size": "medium",
                    "position": "left",
                },
                {
                    "name": "Journaling",
                    "health": "healthy",
                    "imagePath": "sage",
                    "size": "medium",
                    "position": "right",
                },
                {
                    "name": "Waldbaden",
                    "health": "okay",
                    "imagePath": "sequoia",
                    "size": "medium",
                    "position": "bottom",
                },
                {
                    "name": "Psychotherapie",
                    "health": "healthy",
                    "imagePath": "aloe-vera",
                    "size": "big",
                    "position": "top",
                },
            ],
        },
        {
            "id": "extended-family",
            "name": "Extended Family",
            "horizontalPos": "right",
            "verticalPos": "middle",
            "size": "medium",
            "plants": [
                {
                    "name": "Oma",
                    "health": "dead",
                    "imagePath": "snowdrop",
                    "size": "small",
                    "position": "right",
                },
                {
                    "name": "Frankes",
                    "health": "healthy",
                    "imagePath": "marigold",
                    "size": "big",
                    "position": "center-top-mid",
                },
                {
                    "name": "Schwiegereltern",
                    "health": "healthy",
                    "imagePath": "cucumber",
                    "size": "big",
                    "position": "bottom",
                },
            ],
        },
        {
            "id": "hobbies",
            "name": "Hobbies",
            "horizontalPos": "right",
            "verticalPos": "top",
            "size": "small",
            "plants": [
                {
                    "name": "Magic",
                    "health": "dead",
                    "imagePath": "black-lotus",
                    "size": "small",
                    "position": "bottom",
                },
                {
                    "name": "Schach",
                    "health": "okay",
                    "imagePath": "cypress",
                    "size": "medium",
                    "position": "center",
                },
            ],
        },
        {
            "id": "work",
            "name": "Work",
            "horizontalPos": "left",
            "verticalPos": "top",
            "size": "small",
            "plants": [
                {
                    "name": "Spaß bei der Arbeit",
                    "health": "okay",
                    "imagePath": "dandelion",
                    "size": "medium",
                    "position": "center",
                },
                {
                    "name": "Sinn in der Arbeit",
                    "health": "dead",
                    "imagePath": "oak",
                    "size": "small",
                    "position": "bottom",
                },
            ],
        },
    ]
}


@app.get("/")
def read_root():
    return {"message": "Life as a Garden API is running"}


@app.get("/api/garden")
def get_garden_data():
    """Get the complete garden data with all areals and plants"""
    return garden_data


@app.get("/api/garden/print")
def print_garden():
    output_path = Path("output/example.pdf").resolve()

    # Set up headless Chrome with PDF printing enabled
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Start browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Load the website
    driver.get("http://localhost:5173/")

    # --- Wait until body is fully loaded (customize if needed) ---
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)  # Optional: extra delay for JS-heavy pages
    except Exception as e:
        print("Warning: Timeout waiting for page to load:", e)

    # --- Generate PDF via DevTools Protocol ---
    pdf_data = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,  # A4 size
            "paperHeight": 11.69,
        },
    )

    # --- Write to file ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(pdf_data["data"]))

    driver.quit()
    print(f"✅ PDF saved to {output_path}")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
