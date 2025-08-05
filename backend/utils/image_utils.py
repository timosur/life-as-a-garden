import base64
import os
from typing import List, Optional


def get_image_path(input_path: str, page_number: int = 1) -> Optional[str]:
    """Get the path to a specific page PNG file."""
    possible_image_paths = [
        os.path.join(input_path, f"Lebensgarten-{page_number - 1}.png"),  # 0-indexed
    ]

    for path in possible_image_paths:
        if os.path.exists(path):
            return path
    return None


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64."""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        return base64.b64encode(image_bytes).decode("utf-8")


def find_png_files(input_path: str) -> List[str]:
    """Find all PNG files in the input directory."""
    try:
        all_files = os.listdir(input_path)
        png_files = [f for f in all_files if f.endswith(".png")]
        return png_files
    except Exception:
        return []


def list_directory_contents(input_path: str) -> List[str]:
    """List all files in the input directory for debugging."""
    try:
        return os.listdir(input_path)
    except Exception:
        return []
