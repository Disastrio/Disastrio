import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path):
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Photo not found: {input_path}")

    # Remove the background.
    with open(input_path, "rb") as f:
        original = f.read()

    foreground = remove(original)

    # Open the resulting image with its alpha channel.
    image = Image.open(__import__("io").BytesIO(foreground)).convert("RGBA")

    # Composite the subject onto pure white.
    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, image).convert("L")

    # Boost local contrast with CLAHE.
    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    output_path = input_path.with_name(
        f"{input_path.stem}-prepped.png"
    )

    cv2.imwrite(str(output_path), enhanced)

    print(f"Created: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    prep_photo(sys.argv[1])
