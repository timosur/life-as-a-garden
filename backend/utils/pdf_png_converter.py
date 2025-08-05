import os
import platform
import subprocess
from typing import Dict, Any


def convert_to_pdf(input_path: str) -> Dict[str, Any]:
    """Convert reMarkable files to PDF using remarks."""
    print("🔄 Converting reMarkable files to PDF...")

    # Get the path to the remarks binary based on platform
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Determine the correct binary based on platform
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin" and "arm" in machine:
        binary_name = "remarks-darwin-arm64"
    elif system == "linux":
        binary_name = "remarks-linux-arm64"

    remarks_binary = os.path.join(backend_dir, "bin", binary_name)

    # Check if the binary exists
    if not os.path.exists(remarks_binary):
        error_msg = f"Remarks binary not found: {remarks_binary}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

    # Make sure the binary is executable
    os.chmod(remarks_binary, 0o755)

    remarks_cmd = [
        remarks_binary,
        input_path,
        input_path,
    ]

    # Run remarks with proper error handling and debugging
    remarks_result = subprocess.run(remarks_cmd, capture_output=True, text=True)
    print(f"📊 Remarks exit code: {remarks_result.returncode}")
    if remarks_result.stdout:
        print(f"📤 Remarks stdout: {remarks_result.stdout}")
    if remarks_result.stderr:
        print(f"📥 Remarks stderr: {remarks_result.stderr}")

    if remarks_result.returncode == 0:
        print("✅ PDF conversion completed successfully")
        return {"success": True}
    else:
        print("⚠️ PDF conversion may have issues")
        # Check if any PDF was actually created despite the error
        pdf_files_after_remarks = [
            f for f in os.listdir(input_path) if f.endswith(".pdf")
        ]
        if not pdf_files_after_remarks:
            print("❌ No PDF files were created by remarks")
            return {
                "success": False,
                "error": f"Remarks failed to convert files. Exit code: {remarks_result.returncode}. Check if Inkscape is available and the reMarkable files are in a supported format.",
            }
        else:
            print(f"✅ Found PDF files despite error: {pdf_files_after_remarks}")
            return {"success": True}


def convert_to_png(input_path: str) -> Dict[str, Any]:
    """Convert PDF to PNG using ImageMagick."""
    print("🖼️ Converting PDF to PNG...")
    pdf_path = os.path.join(input_path, "Lebensgarten _remarks.pdf")
    png_path = os.path.join(input_path, "Lebensgarten.png")

    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        # Try to find any PDF files in the directory
        pdf_files = [f for f in os.listdir(input_path) if f.endswith(".pdf")]
        print(f"📄 PDF files found: {pdf_files}")
        return {
            "success": False,
            "error": f"Lebensgarten _remarks.pdf not found for conversion. Available files: {os.listdir(input_path)}",
        }

    magick_cmd = [
        "convert",
        "-density",
        "300",
        pdf_path,
        "-quality",
        "100",
        png_path,
    ]

    # Run ImageMagick with proper error handling and debugging
    try:
        magick_result = subprocess.run(magick_cmd, capture_output=True, text=True)
        print(f"📊 ImageMagick exit code: {magick_result.returncode}")
        if magick_result.stdout:
            print(f"📤 ImageMagick stdout: {magick_result.stdout}")
        if magick_result.stderr:
            print(f"📥 ImageMagick stderr: {magick_result.stderr}")

        if magick_result.returncode == 0:
            print("✅ PNG conversion completed successfully")
            return {"success": True}
        else:
            print("⚠️ PNG conversion may have issues")
            # List files after conversion attempt for debugging
            try:
                files_after_conversion = os.listdir(input_path)
                print(
                    f"📁 Files in input directory after ImageMagick: {files_after_conversion}"
                )
            except Exception as list_error:
                print(f"⚠️ Could not list files: {list_error}")
            return {"success": False, "error": "PNG conversion failed"}
    except FileNotFoundError:
        print(
            "❌ ImageMagick 'convert' command not found. Trying alternative approaches..."
        )
        # Try with 'magick convert' as fallback
        try:
            magick_cmd_alt = [
                "magick",
                "convert",
                "-density",
                "300",
                pdf_path,
                "-quality",
                "100",
                png_path,
            ]
            magick_result = subprocess.run(
                magick_cmd_alt, capture_output=True, text=True
            )
            print(
                f"📊 ImageMagick (magick convert) exit code: {magick_result.returncode}"
            )
            if magick_result.stdout:
                print(f"📤 ImageMagick stdout: {magick_result.stdout}")
            if magick_result.stderr:
                print(f"📥 ImageMagick stderr: {magick_result.stderr}")

            if magick_result.returncode == 0:
                print("✅ PNG conversion completed successfully")
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "PNG conversion failed with magick convert",
                }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Neither 'convert' nor 'magick' commands are available. Please install ImageMagick in the Docker container.",
            }
    except Exception as magick_error:
        print(f"❌ ImageMagick command failed: {magick_error}")
        # List files for debugging
        try:
            files_after_error = os.listdir(input_path)
            print(
                f"📁 Files in input directory after ImageMagick error: {files_after_error}"
            )
        except Exception as list_error:
            print(f"⚠️ Could not list files: {list_error}")
        return {"success": False, "error": str(magick_error)}
