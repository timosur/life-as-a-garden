import os
import shutil
import subprocess
from typing import Dict, Any
from utils.rmapi_client import RmapiClient


def download_from_remarkable() -> Dict[str, Any]:
    """Download latest Lebensgarten from reMarkable using rmapi client."""
    print("📥 Downloading latest Lebensgarten from reMarkable...")

    try:
        client = RmapiClient()
        result = client.geta("Journal/Lebensgarten/Lebensgarten")

        print(f"📊 Download result: {result.get('success', False)}")
        if result.get("local_file_path"):
            print(f"📁 File saved to: {result['local_file_path']}")
        if result.get("error"):
            print(f"📥 Error: {result['error']}")

        if not result.get("success"):
            print("❌ Download failed, cannot proceed with analysis")
            return {
                "success": False,
                "error": f"Failed to download file from reMarkable: {result.get('error', 'Unknown error')}",
            }

        print("✅ Download completed successfully")
        return {"success": True, "local_file_path": result.get("local_file_path")}
    except Exception as e:
        print(f"⏰ Download failed: {str(e)}")
        return {"success": False, "error": f"Failed to download file: {str(e)}"}


def clean_and_prepare_input_directory() -> str:
    """Clean input directory and prepare it for fresh start."""
    print("🧹 Cleaning up input directory for fresh start...")

    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(backend_path, "input")

    try:
        if os.path.exists(input_path):
            # Remove all files and subdirectories in the input directory
            for filename in os.listdir(input_path):
                file_path = os.path.join(input_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"⚠️ Failed to delete {file_path}: {e}")
            print("✅ Input directory cleanup completed")
        else:
            print("ℹ️ Input directory does not exist, will be created")

        # Ensure input directory exists
        os.makedirs(input_path, exist_ok=True)
        return input_path
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")
        # Don't raise the exception, just log it since cleanup failure shouldn't break the main functionality
        os.makedirs(input_path, exist_ok=True)
        return input_path


def extract_zip_file(downloaded_file_path: str, input_path: str) -> Dict[str, Any]:
    """Extract zip file if the downloaded file is a zip."""
    print("📂 Preparing input directory and extracting files...")

    if downloaded_file_path and downloaded_file_path.endswith(".zip"):
        print(f"🔍 Extracting zip file: {downloaded_file_path}")

        # Check if the downloaded file exists
        if not os.path.exists(downloaded_file_path):
            print(f"❌ Downloaded file not found: {downloaded_file_path}")
            return {
                "success": False,
                "error": f"Downloaded file not found: {downloaded_file_path}",
            }

        cleanup_cmd = f"unzip -o '{downloaded_file_path}' -d '{input_path}'"

        cleanup_result = subprocess.run(
            cleanup_cmd, shell=True, capture_output=True, text=True
        )
        print(f"📊 Extraction exit code: {cleanup_result.returncode}")
        if cleanup_result.stdout:
            print(f"📤 Extraction stdout: {cleanup_result.stdout}")
        if cleanup_result.stderr:
            print(f"📥 Extraction stderr: {cleanup_result.stderr}")

        if cleanup_result.returncode == 0:
            print("✅ Files extracted to input directory")
            return {"success": True}
        else:
            print(f"⚠️ Extraction failed with exit code {cleanup_result.returncode}")
            return {
                "success": False,
                "error": f"Extraction failed: {cleanup_result.stderr}",
            }
    else:
        print("ℹ️ Downloaded file is not a zip, exiting")
        return {"success": False, "error": "Downloaded file is not a zip"}
