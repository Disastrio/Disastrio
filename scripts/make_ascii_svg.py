from pathlib import Path
import html

import numpy as np
from PIL import Image


INPUT = Path("source-photo-prepped.png")
OUTPUT = Path("avi-ascii.svg")

WIDTH = 100
HEIGHT = 53

# Bright (sparse) -> dark (dense)
RAMP = " .:-=+*cs#%@"

FONT_SIZE = 10
CHAR_WIDTH = 6.0
LINE_HEIGHT = 11.0

FG = "#d0d0d0"


def image_to_ascii(path):
    image = Image.open(path).convert("L")

    # Force the character grid shown in the tutorial.
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    pixels = np.asarray(image, dtype=np.uint8)

    lines = []

    for row in pixels:
        line = ""

        for value in row:
            # White -> space, black -> dense character.
            index = int((255 - int(value)) / 255 * (len(RAMP) - 1))
            line += RAMP[index]

        lines.append(line)

    return lines


def make_svg(lines):
    svg_width = WIDTH * CHAR_WIDTH
    svg_height = HEIGHT * LINE_HEIGHT + 20

    parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg"
             width="{svg_width:.0f}"
             height="{svg_height:.0f}"
             viewBox="0 0 {svg_width:.0f} {svg_height:.0f}">
          <rect width="100%" height="100%" fill="white"/>
          <style>
            text {{
              font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
              font-size: {FONT_SIZE}px;
              font-weight: 600;
              fill: {FG};
              white-space: pre;
            }}
          </style>
        '''
    ]

    total_duration = HEIGHT * 0.055 + 0.9

    for row_number, line in enumerate(lines):
        y = (row_number + 1) * LINE_HEIGHT

        # Each row gets its own clipping rectangle.
        clip_id = f"clip-{row_number}"

        start = row_number * 0.055

        parts.append(
            f'''
            <clipPath id="{clip_id}">
              <rect x="0" y="{y - FONT_SIZE:.1f}"
                    width="0" height="{LINE_HEIGHT + 3:.1f}">
                <animate
                  attributeName="width"
                  from="0"
                  to="{svg_width:.1f}"
                  begin="{start:.3f}s"
                  dur="0.9s"
                  fill="freeze"
                  calcMode="spline"
                  keySplines="0.2 0.8 0.2 1"
                  keyTimes="0;1"/>
              </rect>
            </clipPath>
            '''
        )

        escaped = html.escape(line)

        parts.append(
            f'''
            <g clip-path="url(#{clip_id})">
              <text x="0" y="{y:.1f}">{escaped}</text>

              <rect
                x="0"
                y="{y - FONT_SIZE:.1f}"
                width="5"
                height="{LINE_HEIGHT + 2:.1f}"
                fill="{FG}">
                <animate
                  attributeName="x"
                  from="0"
                  to="{svg_width:.1f}"
                  begin="{start:.3f}s"
                  dur="0.9s"
                  fill="freeze"/>
              </rect>
            </g>
            '''
        )

    parts.append(
        f'''
        </svg>
        '''
    )

    return "".join(parts)


def main():
    if not INPUT.exists():
        raise SystemExit(
            f"Input not found: {INPUT}\n"
            f"Run Step 3a first to create source-photo-prepped.png."
        )

    lines = image_to_ascii(INPUT)
    svg = make_svg(lines)

    OUTPUT.write_text(svg, encoding="utf-8")

    print(f"Created: {OUTPUT}")
    print(f"Grid: {WIDTH} x {HEIGHT}")


if __name__ == "__main__":
    main()
