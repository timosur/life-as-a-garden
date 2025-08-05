import json
import openai
from typing import Union

from garden_types.analysis import AnalysisData
from utils.file_operations import download_from_remarkable, clean_and_prepare_input_directory, extract_zip_file
from utils.pdf_png_converter import convert_to_pdf, convert_to_png
from utils.image_utils import get_image_path, encode_image_to_base64, find_png_files, list_directory_contents


def _prepare_files() -> Union[str, dict]:
    """Common file preparation steps for both analysis functions."""
    # Step 1: Clean and prepare input directory
    input_path = clean_and_prepare_input_directory()
    
    # Step 2: Download latest Lebensgarten from reMarkable
    download_result = download_from_remarkable()
    if not download_result["success"]:
        return {"error": download_result["error"]}
    
    # Step 3: Extract zip file if needed
    extract_result = extract_zip_file(download_result["local_file_path"], input_path)
    if not extract_result["success"]:
        return {"error": extract_result["error"]}
    
    # Step 4: Convert to PDF
    pdf_result = convert_to_pdf(input_path)
    if not pdf_result["success"]:
        return {"error": pdf_result["error"]}
    
    # Step 5: Convert to PNG
    png_result = convert_to_png(input_path)
    if not png_result["success"]:
        return {"error": png_result["error"]}
    
    return input_path


def analyze_checklist_image(
    openai_client: openai.OpenAI = None,
    input_path: str = None,
) -> Union[AnalysisData, dict]:
    """Analyze checklist image from the second page."""
    try:
        # Prepare files if input_path not provided
        if input_path is None:
            result = _prepare_files()
            if isinstance(result, dict) and "error" in result:
                return result
            input_path = result
        
        # Step 6: Analyze the second page PNG for checklist
        image_file_path = get_image_path(input_path, page_number=2)
        
        if not image_file_path:
            # List all files in input directory for debugging
            all_files = list_directory_contents(input_path)
            png_files = find_png_files(input_path)
            print(f"📁 All files in input directory: {all_files}")
            print(f"🖼️ PNG files found: {png_files}")
            
            return {
                "error": f"No PNG image file found. Available files: {all_files}, PNG files: {png_files}"
            }

        print(f"� Using image file: {image_file_path}")
        encoded_image = encode_image_to_base64(image_file_path)

        # Define the prompt for checklist analysis
        checklist_prompt = """
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

        # Send the request to GPT-4o with image and prompt for checklist analysis
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": checklist_prompt},
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

        # Extract the checklist result
        checklist_result = response.choices[0].message.content
        print("✅ Checklist analysis result:", checklist_result)

        # Clean up the response (remove markdown formatting if present)
        if checklist_result.startswith("```json"):
            checklist_result = checklist_result[8:].strip()
        if checklist_result.endswith("```"):
            checklist_result = checklist_result[:-3].strip()

        # Parse and return the JSON result
        try:
            parsed_checklist = json.loads(checklist_result)
            return AnalysisData(parsed_checklist, None)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {
                "error": "Invalid JSON format in response",
                "raw_response": checklist_result,
            }

    except Exception as e:
        print(f"Error analyzing checklist image: {e}")
        return {"error": f"Failed to analyze checklist image: {str(e)}"}


def analyze_notes_image(
    openai_client: openai.OpenAI = None,
    input_path: str = None,
) -> Union[str, dict]:
    """Analyze handwritten notes from the third page."""
    try:
        # Prepare files if input_path not provided
        if input_path is None:
            result = _prepare_files()
            if isinstance(result, dict) and "error" in result:
                return result
            input_path = result
        
        # Step 6: Analyze the third page PNG for handwritten text (page 3 = index 2)
        image_file_path = get_image_path(input_path, page_number=3)
        
        if not image_file_path:
            print("ℹ️ Third page PNG not found, skipping text extraction")
            return {"error": "Third page PNG not found"}

        print(f"� Analyzing handwritten text from: {image_file_path}")
        encoded_text_image = encode_image_to_base64(image_file_path)

        # Define the prompt for text extraction
        text_extraction_prompt = """
You are given an image containing **handwritten freeform text**.
Your task is to extract all clearly readable text and return it **exclusively in Markdown format**.

**Instructions:**

* Preserve the original **structure** of the text (e.g., bullet points, paragraphs, line breaks, emojis).
* Return **only the extracted text** – do **not** add any explanations, metadata, or formatting beyond standard Markdown.
* Do **not** add headings or titles unless they are explicitly present in the handwriting.
* Maintain a clean and minimal style that matches the tone of the original handwriting.
"""

        # Use the provided client or the global openai instance
        client = openai_client if openai_client else openai

        # Send the request to GPT-4o for text extraction
        text_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_extraction_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_text_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=2000,
        )

        text_analysis_result = text_response.choices[0].message.content
        print("✅ Text analysis result:", text_analysis_result)
        
        return text_analysis_result

    except Exception as e:
        print(f"Error analyzing notes image: {e}")
        return {"error": f"Failed to analyze notes image: {str(e)}"}


def analyze_checklist_and_notes_image(
    openai_client: openai.OpenAI = None,
) -> Union[AnalysisData, dict]:
    """Analyze both checklist and notes images and return combined result."""
    try:
        # Prepare files once for both analyses
        result = _prepare_files()
        if isinstance(result, dict) and "error" in result:
            return result
        
        input_path = result
        
        # Analyze checklist using existing function (pass input_path to avoid re-preparation)
        checklist_result = analyze_checklist_image(openai_client, input_path)
        
        # Check if checklist analysis failed
        if isinstance(checklist_result, dict) and "error" in checklist_result:
            return checklist_result
        
        # Analyze notes using existing function (pass input_path to avoid re-preparation)
        notes_result = analyze_notes_image(openai_client, input_path)
        
        # Handle notes analysis result (can be error dict or string)
        notes_text = None
        if isinstance(notes_result, dict) and "error" in notes_result:
            print(f"Notes analysis failed: {notes_result['error']}")
        else:
            notes_text = notes_result
        
        # Create combined AnalysisData with both checklist and notes
        # Extract the checklist data from the AnalysisData object
        if hasattr(checklist_result, 'items'):
            # Convert back to dict format for AnalysisData constructor
            checklist_data = {
                "content": [{"label": item.label, "checkboxIsFilled": item.checkboxIsFilled} 
                           for item in checklist_result.items]
            }
            return AnalysisData(checklist_data, notes_text)
        else:
            return {"error": "Failed to extract checklist data"}
        
    except Exception as e:
        print(f"Error analyzing images: {e}")
        return {"error": f"Failed to analyze images: {str(e)}"}
