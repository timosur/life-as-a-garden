from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from pathlib import Path
import base64
from typing import Optional, List


class MoveRequest(BaseModel):
    source_path: str
    destination_path: str


class GetRequest(BaseModel):
    remote_path: str
    local_path: Optional[str] = None


class PutRequest(BaseModel):
    file_content: str  # Base64 encoded file content
    filename: str
    destination_path: str = "/"


class RmapiResponse(BaseModel):
    success: bool
    message: str
    output: Optional[str] = None
    error: Optional[str] = None
    file_content: Optional[str] = None  # Base64 encoded file content
    filename: Optional[str] = None  # Original filename


app = FastAPI(title="reMarkable API Wrapper", version="1.0.0")


def run_rmapi_command(command: List[str]) -> RmapiResponse:
    """
    Execute an rmapi command using the local binary.

    Args:
        command: List of command arguments to pass to rmapi

    Returns:
        RmapiResponse with success status and output
    """
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent

        # Determine which binary to use based on the system
        import platform

        if platform.machine() == "arm64" and platform.system() == "Darwin":
            # For Apple Silicon Macs, use the macOS arm64 binary
            rmapi_binary = script_dir / "bin" / "rmapi-darwin-arm64"
        else:
            rmapi_binary = script_dir / "bin" / "rmapi-arm64"

        # Build the command with the local binary
        full_cmd = [str(rmapi_binary)] + command

        print(f"Executing command: {' '.join(full_cmd)}")

        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return RmapiResponse(
                success=True,
                message="Command executed successfully",
                output=result.stdout.strip(),
            )
        else:
            return RmapiResponse(
                success=False, message="Command failed", error=result.stderr.strip()
            )

    except subprocess.TimeoutExpired:
        return RmapiResponse(
            success=False,
            message="Command timed out",
            error="Operation timed out after 60 seconds",
        )
    except Exception as e:
        return RmapiResponse(
            success=False, message="Command execution failed", error=str(e)
        )


@app.get("/")
def read_root():
    return {"message": "reMarkable API Wrapper is running"}


@app.post("/api/rmapi/geta", response_model=RmapiResponse)
def geta(request: GetRequest):
    """
    Download a file from reMarkable device.

    Args:
        request: GetRequest containing remote_path and optional local_path

    Returns:
        RmapiResponse with operation result and file content
    """
    try:
        # Extract filename from remote path for the expected download file
        expected_filename = Path(request.remote_path).name
        if not expected_filename or expected_filename == ".":
            expected_filename = "downloaded_file"

        # Add .zip extension if not present (rmapi typically creates zip files)
        if not expected_filename.endswith(".zip"):
            expected_filename += ".zip"

        # Get current working directory where geta will download the file
        current_dir = Path.cwd()
        expected_file_path = current_dir / expected_filename

        # Remove existing file if it exists to avoid confusion
        if expected_file_path.exists():
            expected_file_path.unlink()

        # Download file (geta downloads to current directory)
        command = ["geta", request.remote_path]
        result = run_rmapi_command(command)

        # Check if the file was downloaded even if rmapi reported an error
        # (rmapi often fails with annotation errors but still downloads the file)
        file_downloaded = (
            expected_file_path.exists() and expected_file_path.stat().st_size > 0
        )

        # If the command failed but no file was downloaded, return the error
        if not result.success and not file_downloaded:
            # Check if it's just the annotation error we can ignore
            if result.error and "Failed to generate annotations" in result.error:
                # Even with annotation error, if no file was created, it's a real problem
                return RmapiResponse(
                    success=False,
                    message="File download failed",
                    error=result.error,
                )
            return result

        # Read the downloaded file and encode it as base64
        if file_downloaded:
            with open(expected_file_path, "rb") as f:
                file_content = f.read()
                file_content_b64 = base64.b64encode(file_content).decode("utf-8")

            # Clean up downloaded file
            expected_file_path.unlink()

            # Determine success message based on whether there were warnings
            message = "File downloaded successfully"
            if (
                not result.success
                and result.error
                and "Failed to generate annotations" in result.error
            ):
                message = "File downloaded successfully (ignoring annotation generation error)"

            return RmapiResponse(
                success=True,
                message=message,
                output=result.output,
                file_content=file_content_b64,
                filename=expected_filename,
            )
        else:
            return RmapiResponse(
                success=False,
                message="File was not downloaded properly",
                error="Downloaded file not found in current directory",
            )

    except Exception as e:
        # Clean up downloaded file on error if it exists
        try:
            if expected_file_path.exists():
                expected_file_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors

        return RmapiResponse(success=False, message="Download failed", error=str(e))


@app.post("/api/rmapi/mv", response_model=RmapiResponse)
def mv(request: MoveRequest):
    """
    Move/rename a file or folder on reMarkable device.

    Args:
        request: MoveRequest containing source_path and destination_path

    Returns:
        RmapiResponse with operation result
    """
    command = ["mv", request.source_path, request.destination_path]
    return run_rmapi_command(command)


@app.post("/api/rmapi/put", response_model=RmapiResponse)
def put_upload(request: PutRequest):
    """
    Upload a file to reMarkable device via request body.

    Args:
        request: PutRequest containing base64 encoded file content, filename, and destination path

    Returns:
        RmapiResponse with operation result
    """
    # Create a temporary directory for uploads
    temp_dir = Path("/tmp/rmapi-uploads")
    temp_dir.mkdir(exist_ok=True)

    temp_file_path = temp_dir / request.filename

    try:
        # Decode base64 file content
        file_content = base64.b64decode(request.file_content)

        # Save decoded file content to temp directory
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)

        # Use the local file path directly with rmapi
        command = ["put", str(temp_file_path), request.destination_path]
        result = run_rmapi_command(command)

        # Clean up temp file
        if temp_file_path.exists():
            temp_file_path.unlink()

        return result

    except Exception as e:
        # Clean up temp file on error
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@app.get("/api/rmapi/ls")
def ls(path: str = "/"):
    """
    List files and folders in the specified path on reMarkable device.

    Args:
        path: Path to list (default: root)

    Returns:
        RmapiResponse with directory listing
    """
    command = ["ls", path]
    return run_rmapi_command(command)


@app.get("/api/rmapi/validate")
def validate_rmapi():
    """
    Validate that the rmapi binary is available and accessible.

    Returns:
        Validation status of the rmapi binary setup
    """
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent

        # Determine which binary to use based on the system
        import platform

        if platform.machine() == "arm64":
            rmapi_binary = script_dir / "bin" / "rmapi-arm64"
        else:
            rmapi_binary = script_dir / "bin" / "rmapi-macos"

        # Check if the binary exists and is executable
        if not rmapi_binary.exists():
            return {
                "status": "error",
                "message": f"rmapi binary not found at {rmapi_binary}",
                "rmapi_available": False,
            }

        if not rmapi_binary.is_file():
            return {
                "status": "error",
                "message": f"rmapi binary path is not a file: {rmapi_binary}",
                "rmapi_available": False,
            }

        # Try a simple rmapi command to validate everything works
        test_result = run_rmapi_command(["--help"])

        return {
            "status": "valid" if test_result.success else "error",
            "message": "rmapi binary setup is valid"
            if test_result.success
            else "rmapi validation failed",
            "rmapi_available": test_result.success,
            "binary_path": str(rmapi_binary),
            "details": test_result.output if test_result.success else test_result.error,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Validation failed: {str(e)}",
            "rmapi_available": False,
        }


@app.get("/health")
def health_check():
    """
    Check if rmapi service is accessible and working.

    Returns:
        Health status of the rmapi service
    """
    try:
        result = run_rmapi_command(["ls", "/"])
        return {
            "status": "healthy" if result.success else "unhealthy",
            "rmapi_accessible": result.success,
            "message": result.message if result.success else result.error,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "rmapi_accessible": False,
            "message": f"Health check failed: {str(e)}",
        }
