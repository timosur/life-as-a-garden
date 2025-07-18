import base64
import json
import openai
from typing import Dict, Any
from pathlib import Path

from garden_types.analysis import AnalysisData


def analyze_checklist_image(
    image_path: str, openai_client: openai.OpenAI = None
) -> AnalysisData:
    """
    Analyze a checklist image using GPT-4o vision model.

    Args:
        image_path (str): Path to the image file to analyze
        openai_client (openai.OpenAI, optional): OpenAI client instance. If None, uses the global openai instance.

    Returns:
        Dict[str, Any]: Analysis result containing the checklist items or error information
    """
    try:
        # Load and encode the image
        image_file_path = Path(image_path)
        if not image_file_path.exists():
            return {"error": f"Image file not found: {image_path}"}

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
        return {"error": f"Image file not found: {image_path}"}
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return {"error": f"Failed to analyze image: {str(e)}"}
