import subprocess
from datetime import datetime
from pathlib import Path


def upload_pdf_to_remarkable(pdf_path: str) -> bool:
    """
    Upload a PDF to reMarkable tablet using rmapi Docker container.

    Args:
        pdf_path: Path to the PDF file to upload

    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Get current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Step 1: Rename the existing Lebensgarten to include current date
        rename_cmd = [
            "docker",
            "run",
            "-v",
            f"{Path.home()}/.config/rmapi/:/home/app/.config/rmapi/",
            "-v",
            f"{Path.home()}/rmapi:/tmp/rmapi/",
            "-v",
            f"{Path(pdf_path).parent}:/tmp/rmapi/output",
            "rmapi",
            "mv",
            "Lebensgarten/Lebensgarten",
            f"Lebensgarten/{current_date}",
        ]

        print(f"🔄 Renaming existing Lebensgarten to {current_date}...")
        result = subprocess.run(rename_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(
                f"⚠️  Warning: Could not rename existing file (might not exist): {result.stderr}"
            )
        else:
            print("✅ Existing file renamed successfully")

        # Step 2: Upload the new PDF
        upload_cmd = [
            "docker",
            "run",
            "-v",
            f"{Path.home()}/.config/rmapi/:/home/app/.config/rmapi/",
            "-v",
            f"{Path.home()}/rmapi:/tmp/rmapi/",
            "-v",
            f"{Path(pdf_path).parent}:/tmp/rmapi/output",
            "rmapi",
            "put",
            f"/tmp/rmapi/output/{Path(pdf_path).name}",
            "/Lebensgarten",
        ]

        print("📤 Uploading new PDF to reMarkable...")
        result = subprocess.run(upload_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ PDF uploaded successfully to reMarkable!")
            return True
        else:
            print(f"❌ Failed to upload PDF: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error during reMarkable upload: {str(e)}")
        return False


def archive_and_upload_remarkable(pdf_path: str) -> dict:
    """
    Archive existing file and upload new PDF to reMarkable with detailed result.

    Args:
        pdf_path: Path to the PDF file to upload

    Returns:
        dict: Detailed result containing success status and operation details
    """
    try:
        upload_success = upload_pdf_to_remarkable(pdf_path)

        return {
            "success": upload_success,
            "uploaded_to_remarkable": upload_success,
            "message": "PDF uploaded successfully to reMarkable"
            if upload_success
            else "Failed to upload PDF to reMarkable",
        }

    except Exception as e:
        return {
            "success": False,
            "uploaded_to_remarkable": False,
            "error": f"Failed to upload to reMarkable: {str(e)}",
        }
