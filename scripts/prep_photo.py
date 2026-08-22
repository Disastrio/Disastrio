from pathlib import Path
import io
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prepare(input_path):
    input_path = Path(input_path)

    if not input_path.exists():
        raise SystemExit(f"File not found: {input_path}")

    with input_path.open("rb") as f:
        source = f.read()

    result = remove(source)

    image = Image.open(io.BytesIO(result)).convert("RGBA")

    # Extract the foreground using alpha.
    rgba = np.array(image)
    alpha = rgba[:, :, 3]

    ys, xs = np.where(alpha > 20)

    if len(xs) == 0:
        raise SystemExit("Could not detect the subject.")

    left = xs.min()
    right = xs.max()
    top = ys.min()
    bottom = ys.max()

    # Keep a modest amount of padding.
    w = right - left
    h = bottom - top

    pad_x = int(w * 0.06)
    pad_y = int(h * 0.04)

    left = max(0, left - pad_x)
    right = min(image.width, right + pad_x)
    top = max(0, top - pad_y)
    bottom = min(image.height, bottom + pad_y)

    image = image.crop(
        (left, top, right + 1, bottom + 1)
    )

    # Composite on black.
    black = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 255),
    )

    composited = Image.alpha_composite(
        black,
        image,
    ).convert("L")

    gray = np.array(composited)

    # Increase local contrast.
    clahe = cv2.createCLAHE(
        clipLimit=2.2,
        tileGridSize=(8, 8),
    )

    gray = clahe.apply(gray)

    # Slightly increase contrast.
    gray = cv2.normalize(
        gray,
        None,
        20,
        245,
        cv2.NORM_MINMAX,
    )

    output = input_path.with_name(
        f"{input_path.stem}-prepped.png"
    )

    cv2.imwrite(
        str(output),
        gray,
    )

    print(f"Created: {output}")
    print(f"Crop: {image.width} x {image.height}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: "
            "python scripts/prep_photo.py source-photo.jpg"
        )
        sys.exit(1)

    prepare(sys.argv[1])
