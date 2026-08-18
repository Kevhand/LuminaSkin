from PIL import Image
import numpy as np
import requests
import os
from django.core.files.base import ContentFile
# Different skin concerns can be added with different colors and alpha values for overlay
SKIN_CONCERNS = {
    "dark_circle_v2": {
        "color": (52, 152, 219, 120),   # Blue
        "display_name": "Dark Circles"
    },
    "acne": {
        "color": (231, 76, 60, 120),    # Red
        "display_name": "Acne"
    },
    "wrinkle": {
        "color": (243, 156, 18, 100),   # Orange
        "display_name": "Wrinkles"
    },
    "droopy_lower_eyelid": {
        "color": (155, 89, 182, 120),   # Purple
        "display_name": "Droopy Lower Eyelid"
    },
    "droopy_upper_eyelid": {
        "color": (46, 204, 113, 120),   # Green
        "display_name": "Droopy Upper Eyelid"
    },
    "eye_bag":{
        "color": (26, 188, 156, 120),   # Teal
        "display_name": "Eye Bags"
    },
    "redness":{
        "color": (255, 99, 132, 100),    # pink-red
        "display_name": "Redness"
    },
    "pore":{
        "color": (52, 73, 94, 90),   # Slate
        "display_name": "Pores"
    },
    "firmness":{
        "color": (142, 68, 173, 90),   # Violet
        "display_name": "Firmness"
    },
    "oiliness":{
        "color": (241, 196, 15, 100),   # Yellow
        "display_name": "Oiliness"
    },
    "age_spot":{
        "color": (160, 82, 45, 110),   # Brown
        "display_name": "Age Spots"
    },
    "tear_trough":{
        "color": (41, 128, 185, 100),   # Deep Blue
        "display_name": "Tear Trough"
    },
}


def overlay_images(original_image_path, mask_image_path, output_image_path, skin_concern):
    """
    Creates a semi-transparent overlay for a given skin concern.

    Args:
        original_image_path: Path to original image.
        mask_image_path: Path to binary mask.
        output_image_path: Output file path.
        skin_concern: API concern key.

    Returns:
        Path to generated overlay image.

    """


    original_image = Image.open(original_image_path).convert("RGBA")
    mask_image = Image.open(mask_image_path).convert("L")

    if original_image.size != mask_image.size:
        raise ValueError("The original image and mask image must have the same dimensions.")

    original_np = np.array(original_image)
    mask_np = np.array(mask_image)

    overlay = np.zeros_like(original_np)

    overlay[mask_np > 0] = SKIN_CONCERNS.get(skin_concern, {"color": (255, 255, 255, 120)})["color"]  # Default to white if skin concern not found

    overlay_img = Image.fromarray(overlay, 'RGBA')

    result = Image.alpha_composite(original_image, overlay_img)

    result.save(output_image_path)

    return {
        "overlay_path": output_image_path,
        "display_name": SKIN_CONCERNS[skin_concern]["display_name"]
    }



def download_image(image_url):
    """
    Downloads an mask image and resized image from URL.

    Args:
        image_url: URL of the image to download.
    """

    response = requests.get(image_url, stream=True)

    response.raise_for_status()  # Raise an error for bad responses

    return ContentFile(response.content)  # Return the image content as a Django ContentFile