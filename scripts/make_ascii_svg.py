from pathlib import Path
import html

import numpy as np
from PIL import Image


INPUT = Path("source-photo-prepped.png")
OUTPUT = Path("avi-ascii.svg")

WIDTH = 92

# Characters from bright areas to dark areas.
RAMP = " .,:;irsXA253hMHGS#9B&@"

CHAR_W = 7
CHAR_H = 11

TEXT = "#d7d7d7"
BACKGROUND = "#050505"


def make_ascii():

    image = Image.open(INPUT).convert("L")

    source_w, source_h = image.size

    # Character cells are taller than they are wide.
    height = round(
        WIDTH
        * source_h
        / source_w
        * CHAR_W
        / CHAR_H
    )

    height = max(45, min(height, 70))

    image = image.resize(
        (WIDTH, height),
        Image.Resampling.LANCZOS,
    )

    pixels = np.asarray(image)

    lines = []

    for row in pixels:

        line = []

        for value in row:

            # Dark pixels become dense characters.
            darkness = 255 - int(value)

            index = int(
                darkness
                / 255
                * (len(RAMP) - 1)
            )

            line.append(
                RAMP[index]
            )

        lines.append(
            "".join(line).rstrip()
        )

    return lines


def svg(lines):

    width = WIDTH * CHAR_W
    height = len(lines) * CHAR_H + 20

    parts = [
        f'''<svg
          xmlns="http://www.w3.org/2000/svg"
          width="{width}"
          height="{height}"
          viewBox="0 0 {width} {height}">

          <rect
            width="100%"
            height="100%"
            fill="{BACKGROUND}"/>

          <style>
            text {{
              font-family:
                "DejaVu Sans Mono",
                "Liberation Mono",
                monospace;
              font-size: 10px;
              font-weight: 600;
              fill: {TEXT};
            }}
          </style>
        '''
    ]

    for row, line in enumerate(lines):

        y = 12 + row * CHAR_H

        escaped = html.escape(line)

        # Each row reveals itself from left to right.
        clip_id = f"row{row}"

        delay = row * 0.035

        parts.append(
            f'''
            <clipPath id="{clip_id}">
              <rect
                x="0"
                y="{y - 10}"
                width="0"
                height="{CHAR_H + 2}">

                <animate
                  attributeName="width"
                  from="0"
                  to="{width}"
                  begin="{delay:.3f}s"
                  dur="0.55s"
                  fill="freeze"/>
              </rect>
            </clipPath>

            <g clip-path="url(#{clip_id})">
              <text
                x="0"
                y="{y}">
                {escaped}
              </text>
            </g>
            '''
        )

    parts.append("</svg>")

    return "".join(parts)


def main():

    if not INPUT.exists():
        raise SystemExit(
            f"Missing {INPUT}. "
            "Run prep_photo.py first."
        )

    lines = make_ascii()

    OUTPUT.write_text(
        svg(lines),
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT}"
    )

    print(
        f"Grid: {WIDTH} x {len(lines)}"
    )


if __name__ == "__main__":
    main()
