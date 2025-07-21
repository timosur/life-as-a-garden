import base64
import json
import openai
import os
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

    try:
        # Use the rmapi client to download the file
        client = RmapiClient()
        result = client.geta("Lebensgarten/Lebensgarten")

        print(f"📊 Download result: {result.get('success', False)}")
        if result.get("output"):
            print(f"📤 Output: {result['output']}")
        if result.get("error"):
            print(f"📥 Error: {result['error']}")
        print("✅ Download completed (ignoring any errors as expected)")
    except Exception as e:
        print(f"⏰ Download failed: {str(e)}")
        # Continue anyway, we might still have a zip file from previous runs

    try:
        # Step 2: Clean input directory and unzip the downloaded file
        print("📂 Cleaning input directory and extracting files...")
        home_path = os.path.expanduser("~")

        # Ensure input directory exists
        os.makedirs(input_path, exist_ok=True)

        # Clean directory and unzip
        cleanup_cmd = f"cd {input_path} && rm -rf * 2>/dev/null || true && unzip {home_path}/rmapi/Lebensgarten.zip"
        print(f"🔍 Running cleanup command: {cleanup_cmd}")

        cleanup_result = subprocess.run(
            cleanup_cmd, shell=True, capture_output=True, text=True
        )
        print(f"📊 Cleanup exit code: {cleanup_result.returncode}")
        if cleanup_result.stdout:
            print(f"📤 Cleanup stdout: {cleanup_result.stdout}")
        if cleanup_result.stderr:
            print(f"📥 Cleanup stderr: {cleanup_result.stderr}")
        print("✅ Files extracted to input directory")

        # Step 3: Convert reMarkable files to PDF using remarks
        print("🔄 Converting reMarkable files to PDF...")
        remarks_cmd = [
            f"{os.path.expanduser('~')}/code/remarks/.venv/bin/python",
            "-m",
            "remarks",
            input_path,
            input_path,
        ]
        subprocess.run(remarks_cmd, capture_output=True, text=True)
        print("✅ PDF conversion completed")

        # Step 4: Convert PDF to PNG using ImageMagick
        print("🖼️ Converting PDF to PNG...")
        pdf_path = os.path.join(input_path, "Lebensgarten _remarks.pdf")
        png_path = os.path.join(input_path, "Lebensgarten.png")

        magick_cmd = [
            "magick",
            "-density",
            "300",
            pdf_path,
            "-quality",
            "100",
            png_path,
        ]
        subprocess.run(magick_cmd, capture_output=True, text=True)

        print("✅ PNG conversion completed")

        # Step 5: Analyze the first page PNG
        """
        Analyze a checklist image using GPT-4o vision model.

        Args:
            image_path (str): Path to the image file to analyze
            openai_client (openai.OpenAI, optional): OpenAI client instance. If None, uses the global openai instance.

        Returns:
            Dict[str, Any]: Analysis result containing the checklist items or error information
        """
        # Load and encode the image
        image_file_path = Path("input/Lebensgarten-1.png")
        if not image_file_path.exists():
            return {"error": f"Image file not found: {image_file_path}"}

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

    except FileNotFoundError:
        return {"error": f"Image file not found: {image_file_path}"}
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return {"error": f"Failed to analyze image: {str(e)}"}
    finally:
        # Step 6: Cleanup - Remove all files from input directory
        print("🧹 Cleaning up input directory...")
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
                print("ℹ️ Input directory does not exist, no cleanup needed")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
            # Don't raise the exception, just log it since cleanup failure shouldn't break the main functionality
