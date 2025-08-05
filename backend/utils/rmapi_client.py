import requests
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional
from settings import settings


class RmapiClient:
    """
    Client for communicating with the rmapi-wrapper REST API service.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the rmapi client.

        Args:
            base_url: Base URL of the rmapi-wrapper service.
                     Defaults to RMAPI_SERVICE_URL environment variable or settings configuration.
        """
        self.base_url = base_url or settings.rmapi_service_url
        self.timeout = 60  # 60 seconds timeout for operations

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Make a request to the rmapi-wrapper service.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests

        Returns:
            dict: Response data

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request to rmapi service failed: {str(e)}")

    def geta(self, remote_path: str, local_path: Optional[str] = None) -> dict:
        """
        Download a file from reMarkable device.

        Args:
            remote_path: Path on reMarkable device
            local_path: Optional local path to save file

        Returns:
            dict: Operation result with file content and local file path
        """
        data = {"remote_path": remote_path}
        if local_path:
            data["local_path"] = local_path

        try:
            response = self._make_request("POST", "/api/rmapi/geta", json=data)

            # If the response contains file content, save it locally
            if response.get("success") and response.get("file_content"):
                # Decode the base64 file content
                file_content = base64.b64decode(response["file_content"])

                # Determine local file path
                if not local_path:
                    # Use input folder in backend
                    input_dir = Path(__file__).parent.parent / "input"
                    input_dir.mkdir(exist_ok=True)

                    filename = response.get("filename", "downloaded_file")
                    local_path = str(input_dir / filename)

                # Save file locally
                with open(local_path, "wb") as f:
                    f.write(file_content)

                # Add local file path to response
                response["local_file_path"] = local_path
                response["file_saved"] = True

            return response

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to download file: {str(e)}",
                "file_saved": False,
            }

    def mv(self, source_path: str, destination_path: str) -> dict:
        """
        Move/rename a file or folder on reMarkable device.

        Args:
            source_path: Current path on reMarkable device
            destination_path: New path on reMarkable device

        Returns:
            dict: Operation result
        """
        data = {"source_path": source_path, "destination_path": destination_path}
        return self._make_request("POST", "/api/rmapi/mv", json=data)

    def put(self, file_path: str, destination_path: str) -> dict:
        """
        Upload a file to reMarkable device.

        Args:
            file_path: Local path to file to upload
            destination_path: Destination path on reMarkable device

        Returns:
            dict: Operation result
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content and encode as base64
        with open(file_path, "rb") as f:
            file_content = f.read()
            file_content_b64 = base64.b64encode(file_content).decode("utf-8")

        # Prepare request body with base64 encoded file content
        data = {
            "file_content": file_content_b64,
            "filename": Path(file_path).name,
            "destination_path": destination_path,
        }

        return self._make_request("POST", "/api/rmapi/put", json=data)

    def ls(self, path: str = "/") -> dict:
        """
        List files and folders in the specified path on reMarkable device.

        Args:
            path: Path to list (default: root)

        Returns:
            dict: Directory listing
        """
        return self._make_request("GET", "/api/rmapi/ls", params={"path": path})

    def health_check(self) -> dict:
        """
        Check if rmapi service is accessible and working.

        Returns:
            dict: Health status
        """
        return self._make_request("GET", "/api/rmapi/health")


def upload_pdf_to_remarkable(pdf_path: str) -> bool:
    """
    Upload a PDF to reMarkable tablet using the rmapi REST API service.

    Args:
        pdf_path: Path to the PDF file to upload

    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        client = RmapiClient()

        # Get current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Step 1: Rename the existing Lebensgarten to include current date
        print(f"🔄 Renaming existing Lebensgarten to {current_date}...")

        try:
            mv_result = client.mv(
                "Journal/Lebensgarten/Lebensgarten",
                f"Journal/Lebensgarten/Archiv/{current_date}",
            )

            if mv_result.get("success"):
                print("✅ Existing file renamed successfully")
            else:
                print(
                    f"⚠️  Warning: Could not rename existing file (might not exist): {mv_result.get('error', 'Unknown error')}"
                )
        except Exception as e:
            print(
                f"⚠️  Warning: Could not rename existing file (might not exist): {str(e)}"
            )

        # Step 2: Upload the new PDF
        print("📤 Uploading new PDF to reMarkable...")

        put_result = client.put(pdf_path, "/Journal/Lebensgarten")

        if put_result.get("success"):
            print("✅ PDF uploaded successfully to reMarkable!")
            return True
        else:
            print(
                f"❌ Failed to upload PDF: {put_result.get('error', 'Unknown error')}"
            )
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
