from pathlib import Path
import os


OUTPUT = Path("info-card.svg")

STATIC = os.getenv("STATIC") == "1"

WIDTH = 420
HEIGHT = 220


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def make_svg():
    rows = [
        ("Now", "Building my GitHub profile"),
        ("Prev", "Learning Python & Git"),
        ("Stack", "Python · GitHub · Linux"),
        ("Highlights", "Automation · ASCII · SVG"),
    ]

    parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg"
             width="{WIDTH}"
             height="{HEIGHT}"
             viewBox="0 0 {WIDTH} {HEIGHT}">

          <rect
            width="100%"
            height="100%"
            rx="12"
            fill="#111111"/>

          <rect
            x="1"
            y="1"
            width="{WIDTH - 2}"
            height="{HEIGHT - 2}"
            rx="12"
            fill="none"
            stroke="#333333"/>

          <rect
            x="0"
            y="0"
            width="{WIDTH}"
            height="36"
            rx="12"
            fill="#1c1c1c"/>

          <rect
            x="0"
            y="24"
            width="{WIDTH}"
            height="12"
            fill="#1c1c1c"/>

          <circle cx="18" cy="18" r="5" fill="#ff5f56"/>
          <circle cx="34" cy="18" r="5" fill="#ffbd2e"/>
          <circle cx="50" cy="18" r="5" fill="#27c93f"/>

          <text
            x="70"
            y="23"
            font-family="monospace"
            font-size="14"
            fill="#cccccc">neofetch</text>

          <style>
            .key {{
              font-family: monospace;
              font-size: 14px;
              font-weight: 700;
              fill: #6fb3ff;
            }}

            .value {{
              font-family: monospace;
              font-size: 14px;
              fill: #dddddd;
            }}
          </style>
        '''
    ]

    y = 72

    for index, (key, value) in enumerate(rows):

        delay = index * 0.12

        if STATIC:
            animation = ""
        else:
            animation = f'''
              <animate
                attributeName="opacity"
                from="0"
                to="1"
                begin="{delay:.2f}s"
                dur="0.35s"
                fill="freeze"/>

              <animateTransform
                attributeName="transform"
                type="translate"
                from="-12 0"
                to="0 0"
                begin="{delay:.2f}s"
                dur="0.35s"
                fill="freeze"/>
            '''

        parts.append(
            f'''
            <g opacity="{"1" if STATIC else "0"}">
              {animation}

              <text
                class="key"
                x="24"
                y="{y}">{esc(key)}:</text>

              <text
                class="value"
                x="115"
                y="{y}">{esc(value)}</text>
            </g>
            '''
        )

        y += 38

    parts.append("</svg>")

    return "".join(parts)


def main():
    OUTPUT.write_text(
        make_svg(),
        encoding="utf-8",
    )

    mode = "static" if STATIC else "animated"

    print(f"Created: {OUTPUT}")
    print(f"Mode: {mode}")


if __name__ == "__main__":
    main()
