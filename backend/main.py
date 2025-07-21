import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import GardenDatabase
from utils.image_analysis import analyze_checklist_image
from utils.pdf_generator import print_garden_to_pdf_sync as print_garden_to_pdf
from utils.rmapi_client import archive_and_upload_remarkable
from settings import settings


class WateringLimitUpdate(BaseModel):
    new_limit: int


app = FastAPI(title="Life as a Garden API", version="1.0.0")

# Initialize the database
garden_db = GardenDatabase("db/garden.db")

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
    """Print the garden to PDF"""
    try:
        pdf_path = print_garden_to_pdf()
        return {
            "success": True,
            "message": "Garden printed successfully",
            "pdf_path": pdf_path,
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to print garden: {str(e)}"}


@app.get("/api/garden/analyze")
def analyze_garden():
    """Analyze the garden checklist image"""

    try:
        print("🔍 Analyzing checklist image...")
        result = analyze_checklist_image()
        print("✅ Analysis completed")

        return result

    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return {"error": f"Failed to analyze garden: {str(e)}"}


@app.post("/api/garden/water")
def water_plants_from_analysis():
    """
    Analyze the garden checklist image and water the checked plants.
    Updates plant status based on watering algorithm.
    After watering, prints the garden to PDF and uploads to reMarkable.
    """
    try:
        # First, analyze the checklist image
        analysis_result = analyze_checklist_image()

        # Check if analysis_result is a dictionary with an error (error case)
        if isinstance(analysis_result, dict) and "error" in analysis_result:
            return {"success": False, "error": analysis_result["error"]}

        # Extract checked plant names from analysis
        checked_plants = analysis_result.get_checked_items()

        if not checked_plants:
            return {
                "success": True,
                "message": "No plants were checked for watering",
                "analysis": analysis_result.to_json(),
                "watering_result": None,
            }

        # Water the checked plants
        watering_result = garden_db.water_plants(checked_plants)

        # Get updated garden stats
        stats = garden_db.get_database_stats()
        daily_stats = garden_db.get_daily_watering_stats()

        # Print and upload garden after watering
        try:
            # Generate PDF
            pdf_path = print_garden_to_pdf()

            # Upload to reMarkable
            upload_result = archive_and_upload_remarkable(pdf_path)

            print_result = {
                "success": True,
                "pdf_path": pdf_path,
                "uploaded_to_remarkable": upload_result["uploaded_to_remarkable"],
                "message": "Garden printed and uploaded successfully"
                if upload_result["success"]
                else "Garden printed but upload failed",
                "upload_details": upload_result,
            }
        except Exception as e:
            print_result = {
                "success": False,
                "error": f"Failed to print and upload garden: {str(e)}",
            }

        return {
            "success": True,
            "analysis": analysis_result.to_json(),
            "watering_result": watering_result,
            "garden_stats": stats,
            "daily_watering_stats": daily_stats,
            "print_result": print_result,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to process watering: {str(e)}"}


@app.get("/api/garden/watering/stats")
def get_watering_stats():
    """Get current watering statistics and daily limits"""
    daily_stats = garden_db.get_daily_watering_stats()
    plants_needing_water = garden_db.get_plants_needing_water()

    return {
        "daily_stats": daily_stats,
        "plants_needing_water": plants_needing_water,
    }


@app.put("/api/garden/watering/limit")
def update_watering_limit(request: WateringLimitUpdate):
    """Update the daily watering limit"""
    if request.new_limit < 1 or request.new_limit > 50:
        return {"success": False, "error": "Limit must be between 1 and 50"}

    success = garden_db.set_daily_watering_limit(request.new_limit)
    if success:
        return {
            "success": True,
            "message": f"Daily watering limit updated to {request.new_limit}",
        }
    else:
        return {"success": False, "error": "Failed to update watering limit"}


@app.post("/api/garden/water/{plant_identifier}")
def water_single_plant(plant_identifier: str, by_id: bool = False):
    """
    Water a specific plant by name or ID.

    Args:
        plant_identifier: Plant name or ID
        by_id: Query parameter - if true, treat plant_identifier as ID, otherwise as name
    """
    try:
        result = garden_db.water_single_plant(plant_identifier, by_id=by_id)

        if result["success"]:
            # Get updated garden stats
            stats = garden_db.get_database_stats()
            daily_stats = garden_db.get_daily_watering_stats()

            return {
                **result,
                "garden_stats": stats,
                "daily_watering_stats": daily_stats,
            }
        else:
            return result

    except Exception as e:
        return {"success": False, "error": f"Failed to water plant: {str(e)}"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
