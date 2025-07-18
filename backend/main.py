import base64
import time
import openai
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
from pydantic_settings import BaseSettings, SettingsConfigDict

from database.garden_db import GardenDatabase
from utils.image_analysis import analyze_checklist_image

app = FastAPI(title="Life as a Garden API", version="1.0.0")

# Initialize the database
garden_db = GardenDatabase("garden.db")


class Settings(BaseSettings):
    openai_api_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

openai.api_key = settings.openai_api_key


# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Life as a Garden API is running"}


@app.get("/api/garden")
def get_garden_data():
    """Get the complete garden data with all areals and plants"""
    return garden_db.get_garden_data()


@app.get("/api/garden/stats")
def get_garden_stats():
    """Get basic statistics about the garden database"""
    return garden_db.get_database_stats()


@app.get("/api/garden/areals")
def get_areals():
    """Get all areals"""
    return garden_db.get_all_areals()


@app.get("/api/garden/areals/{areal_id}/plants")
def get_plants_by_areal(areal_id: str):
    """Get all plants for a specific areal"""
    return garden_db.get_plants_by_areal(areal_id)


@app.get("/api/garden/plants/health/{health}")
def get_plants_by_health(health: str):
    """Get all plants with a specific health status (healthy, okay, dead)"""
    return garden_db.get_plants_by_health(health)


@app.put("/api/garden/plants/{plant_id}/health")
def update_plant_health(plant_id: int, health: str):
    """Update the health status of a plant"""
    success = garden_db.update_plant_health(plant_id, health)
    if success:
        return {"message": f"Plant {plant_id} health updated to {health}"}
    else:
        return {"error": f"Failed to update plant {plant_id}"}


@app.get("/api/garden/print")
def print_garden():
    output_path = Path("output/Lebensgarten.pdf").resolve()

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


@app.get("/api/garden/analyze")
def analyze_garden():
    """Analyze the garden checklist image"""
    image_path = "input/output-1.png"
    return analyze_checklist_image(image_path)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
