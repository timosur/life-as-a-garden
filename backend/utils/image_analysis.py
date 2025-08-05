import base64
import json
import openai
import os
import platform
import subprocess
import shutil
from pathlib import Path

from garden_types.analysis import AnalysisData
from utils.rmapi_client import RmapiClient

from typing import Union


def analyze_checklist_image(
    openai_client: openai.OpenAI = None,
) -> Union[AnalysisData, dict]:
    # Step 1: Download latest Lebensgarten from reMarkable using rmapi client
    print("📥 Downloading latest Lebensgarten from reMarkable...")

    # Define paths for cleanup
    backend_path = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(backend_path, "input")
    image_file_path = None  # Initialize to avoid UnboundLocalError

    # Step 0: Clean input directory at the beginning for a fresh start
    print("🧹 Cleaning up input directory for fresh start...")
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
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")
        # Don't raise the exception, just log it since cleanup failure shouldn't break the main functionality

    try:
        # Use the rmapi client to download the file (it will be saved to input directory automatically)
        client = RmapiClient()
        result = client.geta("Journal/Lebensgarten/Lebensgarten")

        print(f"📊 Download result: {result.get('success', False)}")
        if result.get("local_file_path"):
            print(f"� File saved to: {result['local_file_path']}")
        if result.get("error"):
            print(f"📥 Error: {result['error']}")

        if not result.get("success"):
            print("❌ Download failed, cannot proceed with analysis")
            return {
                "error": f"Failed to download file from reMarkable: {result.get('error', 'Unknown error')}"
            }

        downloaded_file_path = result.get("local_file_path")
        print("✅ Download completed successfully")
    except Exception as e:
        print(f"⏰ Download failed: {str(e)}")
        return {"error": f"Failed to download file: {str(e)}"}

    try:
        # Step 2: Clean input directory (except the downloaded file) and unzip if it's a zip file
        print("📂 Preparing input directory and extracting files...")

        # Ensure input directory exists
        os.makedirs(input_path, exist_ok=True)

        # If the downloaded file is a zip, extract it
        if downloaded_file_path and downloaded_file_path.endswith(".zip"):
            print(f"🔍 Extracting zip file: {downloaded_file_path}")
            cleanup_cmd = f"cd {input_path} && unzip -o '{downloaded_file_path}'"

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
            else:
                print("⚠️ Extraction has issues, exiting")
                return {"error": "Extraction has issues"}
        else:
            print("ℹ️ Downloaded file is not a zip, exiting")
            return {"error": "Downloaded file is not a zip"}

        # Step 3: Convert reMarkable files to PDF using remarks
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
            return {"error": error_msg}

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
        else:
            print("⚠️ PDF conversion may have issues")
            # Check if any PDF was actually created despite the error
            pdf_files_after_remarks = [
                f for f in os.listdir(input_path) if f.endswith(".pdf")
            ]
            if not pdf_files_after_remarks:
                print("❌ No PDF files were created by remarks")
                return {
                    "error": f"Remarks failed to convert files. Exit code: {remarks_result.returncode}. Check if Inkscape is available and the reMarkable files are in a supported format."
                }
            else:
                print(f"✅ Found PDF files despite error: {pdf_files_after_remarks}")

        # List files after PDF conversion for debugging
        try:
            files_after_pdf = os.listdir(input_path)
            print(
                f"📁 Files in input directory after PDF conversion: {files_after_pdf}"
            )
        except Exception as list_error:
            print(f"⚠️ Could not list files: {list_error}")

        print("✅ PDF conversion completed")

        # Step 4: Convert PDF to PNG using ImageMagick
        print("🖼️ Converting PDF to PNG...")
        pdf_path = os.path.join(input_path, "Lebensgarten _remarks.pdf")
        png_path = os.path.join(input_path, "Lebensgarten.png")

        # Check if PDF file exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            # Try to find any PDF files in the directory
            pdf_files = [f for f in os.listdir(input_path) if f.endswith(".pdf")]
            print(f"📄 PDF files found: {pdf_files}")
            raise FileNotFoundError(
                f"Lebensgarten _remarks.pdf not found for conversion. Available files: {os.listdir(input_path)}"
            )

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
            except FileNotFoundError:
                raise FileNotFoundError(
                    "Neither 'convert' nor 'magick' commands are available. Please install ImageMagick in the Docker container."
                )
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
            raise magick_error

        print("✅ PNG conversion completed")

        # Step 5: Analyze the first page PNG
        # Load and encode the image
        possible_image_paths = [
            os.path.join(input_path, "Lebensgarten-1.png"),
        ]

        image_file_path = None
        for path in possible_image_paths:
            if os.path.exists(path):
                image_file_path = path
                break

        if not image_file_path:
            # List all files in input directory for debugging
            try:
                all_files = os.listdir(input_path)
                png_files = [f for f in all_files if f.endswith(".png")]
                print(f"📁 All files in input directory: {all_files}")
                print(f"🖼️ PNG files found: {png_files}")
                print(
                    f"🔍 Searched for: {[os.path.basename(path) for path in possible_image_paths]}"
                )
            except Exception as list_error:
                print(f"⚠️ Could not list files in input directory: {list_error}")
                all_files = []
                png_files = []

            return {
                "error": f"No PNG image file found. Available files: {all_files}, PNG files: {png_files}"
            }

        print(f"📷 Using image file: {image_file_path}")
        with open(image_file_path, "rb") as image_file:
            image_bytes = image_file.read()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # Define the prompt
        prompt = """
You are given an image containing **only a checklist**, where each item consists of a label and a checkbox.

The checkboxes can appear in two states:

* ☐ or empty → "checkboxIsFilled": false
* ☒, marked, crossed, filled, or circled → "checkboxIsFilled": true

Your task is to extract each checklist item and return it in the following JSON format:

{
  "content": [
    {
      "label": "Partnerschaft",
      "checkboxIsFilled": true
    },
    {
      "label": "Kinder",
      "checkboxIsFilled": false
    }
  ]
}

Be robust: if a checkbox is clearly marked in any way (checked, crossed, filled, or circled), treat it as "checkboxIsFilled": true.

**Only return the JSON.** Ignore anything else.
"""

        # Use the provided client or the global openai instance
        client = openai_client if openai_client else openai

        # Send the request to GPT-4o with image and prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        # Extract the result
        result = response.choices[0].message.content
        print("✅ Analysis result:", result)

        # Clean up the response (remove markdown formatting if present)
        if result.startswith("```json"):
            result = result[8:].strip()
        if result.endswith("```"):
            result = result[:-3].strip()

        # Parse and return the JSON result
        try:
            parsed_result = json.loads(result)
            return AnalysisData(parsed_result)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {"error": "Invalid JSON format in response", "raw_response": result}

    except FileNotFoundError as e:
        return {
            "error": f"File not found during analysis: {str(e)}",
        }
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return {"error": f"Failed to analyze image: {str(e)}"}
