import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from database import GardenDatabase
from utils.image_analysis import analyze_checklist_and_notes_image
from utils.pdf_generator import (
    print_garden_to_pdf_sync as print_garden_to_pdf,
    print_notes_to_pdf_sync,
)
from utils.rmapi_client import (
    archive_and_upload_garden_remarkable,
    delete_and_upload_garden_remarkable,
)
from settings import settings
from health_check import create_health_checker
from utils.email_service import email_service


class WateringLimitUpdate(BaseModel):
    new_limit: int


class DownloadRequest(BaseModel):
    remote_path: str
    local_path: Optional[str] = None


class PlantUpdate(BaseModel):
    name: Optional[str] = None
    health: Optional[str] = None
    size: Optional[str] = None
    image_path: Optional[str] = None
    position: Optional[str] = None
    areal_id: Optional[str] = None
    last_watered: Optional[str] = None
    days_without_water: Optional[int] = None
    water_streak: Optional[int] = None
    total_water_count: Optional[int] = None


class PlantCreate(BaseModel):
    areal_id: str
    name: str
    health: str = "healthy"
    image_path: str = ""
    size: str = "small"
    position: str = ""
    days_without_water: int = 0
    water_streak: int = 1
    total_water_count: int = 20
    last_watered: Optional[str] = None


class ArealCreate(BaseModel):
    id: str
    name: str
    horizontal_pos: str
    vertical_pos: str
    size: str


class ArealUpdate(BaseModel):
    name: Optional[str] = None
    horizontal_pos: Optional[str] = None
    vertical_pos: Optional[str] = None
    size: Optional[str] = None


app = FastAPI(
    title="Life as a Garden API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

# Initialize the database
garden_db = GardenDatabase()

# Initialize health checker
health_checker = create_health_checker(garden_db)

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


@app.get("/api/garden/plants")
def get_all_plants():
    """Get all plants with their complete information"""
    return garden_db.get_all_plants()


@app.put("/api/garden/plants/{plant_id}")
def update_plant(plant_id: int, plant_data: PlantUpdate):
    """Update plant information (all supported fields)"""
    try:
        # Convert Pydantic model to dict and filter None values
        update_data = {
            k: v for k, v in plant_data.model_dump().items() if v is not None
        }

        if not update_data:
            return {"error": "No fields provided for update"}

        success = garden_db.update_plant(plant_id, update_data)
        if success:
            return {"message": f"Plant {plant_id} updated successfully"}
        else:
            return {"error": f"Failed to update plant {plant_id} - plant may not exist"}
    except Exception as e:
        return {"error": f"Failed to update plant: {str(e)}"}


@app.post("/api/garden/plants")
def create_plant(plant_data: PlantCreate):
    """Create a new plant"""
    try:
        # Convert Pydantic model to dict
        plant_dict = plant_data.model_dump()
        areal_id = plant_dict.pop("areal_id")

        created_plant = garden_db.insert_plant(areal_id, plant_dict)
        if created_plant:
            return {
                "message": f"Plant '{plant_data.name}' created successfully",
                "plant": created_plant,
            }
        else:
            return {"error": f"Failed to create plant '{plant_data.name}'"}
    except Exception as e:
        return {"error": f"Failed to create plant: {str(e)}"}


@app.delete("/api/garden/plants/{plant_id}")
def delete_plant(plant_id: int):
    """Delete a plant"""
    try:
        success = garden_db.delete_plant(plant_id)
        if success:
            return {"message": f"Plant {plant_id} deleted successfully"}
        else:
            return {"error": f"Failed to delete plant {plant_id} - plant may not exist"}
    except Exception as e:
        return {"error": f"Failed to delete plant: {str(e)}"}


@app.get("/api/garden/plants/{plant_id}")
def get_plant_by_id(plant_id: int):
    """Get a specific plant by ID"""
    try:
        plant = garden_db.get_plant_by_id(plant_id)
        if plant:
            return plant
        else:
            return {"error": f"Plant {plant_id} not found"}
    except Exception as e:
        return {"error": f"Failed to get plant: {str(e)}"}


@app.post("/api/garden/areals")
def create_areal(areal_data: ArealCreate):
    """Create a new areal"""
    try:
        # Convert Pydantic model to dict
        areal_dict = {
            "id": areal_data.id,
            "name": areal_data.name,
            "horizontalPos": areal_data.horizontal_pos,
            "verticalPos": areal_data.vertical_pos,
            "size": areal_data.size,
        }

        success = garden_db.insert_areal(areal_dict)
        if success:
            return {"message": f"Areal '{areal_data.name}' created successfully"}
        else:
            return {"error": f"Failed to create areal '{areal_data.name}'"}
    except Exception as e:
        return {"error": f"Failed to create areal: {str(e)}"}


@app.put("/api/garden/areals/{areal_id}")
def update_areal(areal_id: str, areal_data: ArealUpdate):
    """Update areal information"""
    try:
        # Convert Pydantic model to dict and filter None values
        update_data = {
            k: v for k, v in areal_data.model_dump().items() if v is not None
        }

        if not update_data:
            return {"error": "No fields provided for update"}

        success = garden_db.update_areal(areal_id, update_data)
        if success:
            return {"message": f"Areal {areal_id} updated successfully"}
        else:
            return {"error": f"Failed to update areal {areal_id} - areal may not exist"}
    except Exception as e:
        return {"error": f"Failed to update areal: {str(e)}"}


@app.delete("/api/garden/areals/{areal_id}")
def delete_areal(areal_id: str):
    """Delete an areal and all its plants"""
    try:
        success = garden_db.delete_areal(areal_id)
        if success:
            return {
                "message": f"Areal {areal_id} and all its plants deleted successfully"
            }
        else:
            return {"error": f"Failed to delete areal {areal_id} - areal may not exist"}
    except Exception as e:
        return {"error": f"Failed to delete areal: {str(e)}"}


@app.get("/api/garden/areals/{areal_id}")
def get_areal_by_id(areal_id: str):
    """Get a specific areal by ID"""
    try:
        areal = garden_db.get_areal_by_id(areal_id)
        if areal:
            return areal
        else:
            return {"error": f"Areal {areal_id} not found"}
    except Exception as e:
        return {"error": f"Failed to get areal: {str(e)}"}


@app.get("/api/garden/print")
def print_garden():
    """Print the garden to PDF"""
    try:
        garden_pdf_path = print_garden_to_pdf()
        notes_pdf_path = print_notes_to_pdf_sync()

        # Upload to reMarkable
        upload_result = delete_and_upload_garden_remarkable(garden_pdf_path)

        return {
            "success": True,
            "message": "Garden printed successfully",
            "garden_pdf_path": garden_pdf_path,
            "notes_pdf_path": notes_pdf_path,
            "upload_result": upload_result,
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to print garden: {str(e)}"}


@app.get("/api/garden/analyze")
def analyze_garden():
    """Analyze the garden checklist image and notes"""

    try:
        print("🔍 Analyzing checklist image and notes...")
        result = analyze_checklist_and_notes_image()
        print("✅ Analysis completed")

        # Save notes if extracted from analysis
        notes_save_result = None
        if hasattr(result, "notes") and result.notes:
            try:
                from datetime import date

                today = date.today()

                # Check if notes already exist for today
                if not garden_db.note_exists_for_date(today):
                    note_id = garden_db.create_note(result.notes, today)
                    notes_save_result = {
                        "success": True,
                        "note_id": note_id,
                        "message": "Notes saved successfully",
                    }
                else:
                    notes_save_result = {
                        "success": False,
                        "message": "Notes already exist for today, skipping save",
                    }
            except Exception as e:
                notes_save_result = {
                    "success": False,
                    "error": f"Failed to save notes: {str(e)}",
                }

        # Include notes save result in response
        if isinstance(result, dict) and "error" in result:
            return result
        else:
            response = result.to_json()
            if notes_save_result:
                response["notes_save_result"] = notes_save_result
            return response

    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return {"error": f"Failed to analyze garden: {str(e)}"}


@app.post("/api/garden/water")
def water_plants_from_analysis(watering_date: Optional[str] = None):
    """
    Analyze the garden checklist image and notes, then water the checked plants.
    Updates plant status based on watering algorithm.
    After watering, prints the garden to PDF and uploads to reMarkable.

    Args:
        watering_date: Optional date string (YYYY-MM-DD) to set as last watered date for
                       all watered plants. If not provided, uses today's date.
    Returns:
        A dictionary with analysis results, watering results, garden stats, and upload status.
    """
    try:
        # First, analyze the checklist image and notes
        analysis_result = analyze_checklist_and_notes_image()

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
        watering_result = garden_db.water_plants(
            checked_plants, watering_date=watering_date
        )

        # Save notes if extracted from analysis
        notes_save_result = None
        if hasattr(analysis_result, "notes") and analysis_result.notes:
            try:
                my_date = date.today()
                if watering_date:
                    my_date = datetime.strptime(watering_date, "%Y-%m-%d").date()

                # Check if notes already exist for today
                if not garden_db.note_exists_for_date(my_date):
                    note_id = garden_db.create_note(analysis_result.notes, my_date)
                    notes_save_result = {
                        "success": True,
                        "note_id": note_id,
                        "message": "Notes saved successfully",
                    }
                else:
                    notes_save_result = {
                        "success": False,
                        "message": f"Notes already exist for {my_date}, skipping save",
                    }
            except Exception as e:
                notes_save_result = {
                    "success": False,
                    "error": f"Failed to save notes: {str(e)}",
                }

        # Get updated garden stats
        stats = garden_db.get_database_stats()
        daily_stats = garden_db.get_daily_watering_stats()

        # Print and upload garden after watering
        try:
            # Generate PDF
            pdf_path = print_garden_to_pdf()

            # Upload to reMarkable
            upload_result = archive_and_upload_garden_remarkable(pdf_path)

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

        # Send email notification for successful analysis run
        try:
            email_service.send_analysis_success_notification(
                analysis_result.to_json(), stats
            )
        except Exception as e:
            # Don't let email failures affect the main operation
            print(f"Failed to send analysis success notification: {str(e)}")

        return {
            "success": True,
            "analysis": analysis_result.to_json(),
            "watering_result": watering_result,
            "garden_stats": stats,
            "daily_watering_stats": daily_stats,
            "print_result": print_result,
            "notes_save_result": notes_save_result,
        }

    except Exception as e:
        # Send email notification for analysis failure
        try:
            email_service.send_analysis_failure_notification(
                str(e), garden_db.get_database_stats()
            )
        except Exception as email_error:
            print(f"Failed to send analysis failure notification: {str(email_error)}")

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


@app.get("/api/garden/watering/last-session")
def get_last_watering_session():
    """Get detailed information about the last watering session including plant changes"""
    try:
        result = garden_db.get_last_watering_details()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get last watering details: {str(e)}",
        }


@app.get("/api/garden/plant-status-changes")
def get_plant_status_changes(plant_id: int = None, limit: int = None):
    """Get history of plant status changes"""
    try:
        result = garden_db.get_plant_status_changes(plant_id, limit)
        return {"success": True, "status_changes": result}
    except Exception as e:
        return {"success": False, "error": f"Failed to get status changes: {str(e)}"}


@app.get("/api/garden/plant-status-changes/today")
def get_todays_plant_status_changes():
    """Get plant status changes for today only"""
    try:
        from datetime import date

        today = date.today().strftime("%Y-%m-%d")

        # Get today's changes directly from repository with SQL filtering
        todays_changes = garden_db.get_todays_plant_status_changes()

        return {
            "success": True,
            "status_changes": todays_changes,
            "date": today,
            "count": len(todays_changes),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get today's status changes: {str(e)}",
        }


@app.post("/api/garden/update-daily-status")
def update_daily_plant_status():
    """Update status of all plants for daily maintenance (manually trigger)"""
    try:
        result = garden_db.update_daily_plant_status()
        return result
    except Exception as e:
        return {"success": False, "error": f"Failed to update daily status: {str(e)}"}


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


@app.get("/api/garden/watering/calendar/{start_date}/{end_date}")
def get_watering_calendar(start_date: str, end_date: str):
    """Get watering history for calendar display within a date range."""
    try:
        from datetime import datetime

        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        history = garden_db.get_watering_history_by_date_range(start_date, end_date)

        return {
            "success": True,
            "watering_history": history,
            "start_date": start_date,
            "end_date": end_date,
            "count": len(history),
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get watering calendar: {str(e)}"}


@app.get("/api/garden/watering/history")
def get_all_watering_history():
    """Debug endpoint to get all watering history."""
    try:
        from database.repositories.watering import WateringRepository

        watering_repo = WateringRepository()
        history = watering_repo.get_watering_history()

        return {
            "success": True,
            "watering_history": history,
            "count": len(history),
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get watering history: {str(e)}"}


# Notes API endpoints
@app.get("/api/notes")
def get_all_notes():
    """Get all notes ordered by extraction date."""
    try:
        notes = garden_db.get_all_notes()
        return {"success": True, "notes": notes}
    except Exception as e:
        return {"success": False, "error": f"Failed to get notes: {str(e)}"}


@app.get("/api/notes/date/{date_str}")
def get_notes_by_date(date_str: str):
    """Get notes for a specific date (YYYY-MM-DD format)."""
    try:
        from datetime import datetime

        # Parse the date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        notes = garden_db.get_notes_by_date(date_obj)
        return {"success": True, "notes": notes, "date": date_str}
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get notes: {str(e)}"}


@app.get("/api/notes/range/{start_date}/{end_date}")
def get_notes_by_date_range(start_date: str, end_date: str):
    """Get notes within a date range (YYYY-MM-DD format)."""
    try:
        from datetime import datetime

        # Parse the date strings
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        notes = garden_db.get_notes_by_date_range(start_date_obj, end_date_obj)
        return {
            "success": True,
            "notes": notes,
            "start_date": start_date,
            "end_date": end_date,
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get notes: {str(e)}"}


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int):
    """Delete a specific note."""
    try:
        success = garden_db.delete_note(note_id)
        if success:
            return {"success": True, "message": f"Note {note_id} deleted successfully"}
        else:
            return {"success": False, "error": f"Note {note_id} not found"}
    except Exception as e:
        return {"success": False, "error": f"Failed to delete note: {str(e)}"}


@app.put("/api/notes/{note_id}")
def update_note(note_id: int, note_data: dict):
    """Update a specific note's content."""
    try:
        content = note_data.get("content", "").strip()
        if not content:
            return {"success": False, "error": "Content cannot be empty"}

        success = garden_db.update_note(note_id, content)
        if success:
            return {"success": True, "message": f"Note {note_id} updated successfully"}
        else:
            return {"success": False, "error": f"Note {note_id} not found"}
    except Exception as e:
        return {"success": False, "error": f"Failed to update note: {str(e)}"}


@app.post("/api/notes")
def create_note(note_data: dict):
    """Create a new note."""
    try:
        extracted_at = note_data.get("extracted_at", "").strip()
        content = note_data.get("content", "").strip()

        if not extracted_at:
            return {"success": False, "error": "extracted_at is required"}
        if not content:
            return {"success": False, "error": "Content cannot be empty"}

        # Validate date format
        from datetime import datetime

        try:
            date_obj = datetime.strptime(extracted_at, "%Y-%m-%d").date()
        except ValueError:
            return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}

        # Create the note
        note_id = garden_db.create_note(content, date_obj)
        if note_id:
            # Fetch the created note to return complete data
            note = garden_db.get_note_by_id(note_id)
            if note:
                return {
                    "success": True,
                    "message": "Note created successfully",
                    "note": note,
                }
            else:
                return {"success": False, "error": "Failed to retrieve created note"}
        else:
            return {"success": False, "error": "Failed to create note"}
    except Exception as e:
        return {"success": False, "error": f"Failed to create note: {str(e)}"}


@app.get("/api/health")
async def health_check():
    """
    Comprehensive health check for all system components.

    Checks:
    1. Database connectivity
    2. OpenAI API availability and credits
    3. Frontend service availability
    4. rmapi-wrapper service availability
    5. File system permissions
    6. System resources (if available)
    """
    return await health_checker.check()


@app.post("/api/notifications/test-email")
def test_email_configuration():
    """Test the email notification configuration by sending a test email."""
    try:
        from utils.email_service import email_service

        result = email_service.test_email_configuration()
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to test email configuration: {str(e)}",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
