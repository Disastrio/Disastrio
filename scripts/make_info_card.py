from pathlib import Path
import os
import html


OUTPUT = Path("info-card.svg")

STATIC = os.getenv("STATIC") == "1"

WIDTH = 430
HEIGHT = 330


ROWS = [
    ("OS", "Linux"),
    ("Shell", "bash"),
    ("Focus", "Python / GitHub"),
    ("Stack", "Python · Git · Linux"),
    ("Build", "Automation · SVG"),
    ("Status", "Learning & building"),
]


def esc(value):
    return html.escape(str(value))


def make_svg():

    parts = [
        f'''<svg
          xmlns="http://www.w3.org/2000/svg"
          width="{WIDTH}"
          height="{HEIGHT}"
          viewBox="0 0 {WIDTH} {HEIGHT}">

          <rect
            width="100%"
            height="100%"
            rx="14"
            fill="#0b0f14"/>

          <rect
            x="1"
            y="1"
            width="{WIDTH - 2}"
            height="{HEIGHT - 2}"
            rx="14"
            fill="none"
            stroke="#30363d"/>

          <rect
            x="0"
            y="0"
            width="{WIDTH}"
            height="42"
            rx="14"
            fill="#161b22"/>

          <rect
            x="0"
            y="28"
            width="{WIDTH}"
            height="14"
            fill="#161b22"/>

          <circle
            cx="20"
            cy="21"
            r="6"
            fill="#ff5f56"/>

          <circle
            cx="39"
            cy="21"
            r="6"
            fill="#ffbd2e"/>

          <circle
            cx="58"
            cy="21"
            r="6"
            fill="#27c93f"/>

          <text
            x="80"
            y="26"
            font-family="monospace"
            font-size="14"
            fill="#8b949e">
            neofetch
          </text>

          <style>
            .key {{
              font-family: monospace;
              font-size: 14px;
              font-weight: 700;
              fill: #58a6ff;
            }}

            .value {{
              font-family: monospace;
              font-size: 14px;
              fill: #c9d1d9;
            }}

            .prompt {{
              font-family: monospace;
              font-size: 12px;
              fill: #8b949e;
            }}
          </style>

          <text
            x="24"
            y="70"
            class="prompt">
            avi@github ~ $ whoami
          </text>
        '''
    ]

    y = 105

    for index, (key, value) in enumerate(ROWS):

        delay = index * 0.10

        if STATIC:
            animation = ""
            opacity = "1"
        else:
            animation = f'''
              <animate
                attributeName="opacity"
                from="0"
                to="1"
                begin="{delay:.2f}s"
                dur="0.30s"
                fill="freeze"/>

              <animateTransform
                attributeName="transform"
                type="translate"
                from="-8 0"
                to="0 0"
                begin="{delay:.2f}s"
                dur="0.30s"
                fill="freeze"/>
            '''

            opacity = "0"

        parts.append(
            f'''
            <g opacity="{opacity}">
              {animation}

              <text
                x="28"
                y="{y}"
                class="key">
                {esc(key)}
              </text>

              <text
                x="150"
                y="{y}"
                class="value">
                {esc(value)}
              </text>
            </g>
            '''
        )

        y += 36

    parts.append("</svg>")

    return "".join(parts)


def main():

    OUTPUT.write_text(
        make_svg(),
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT}"
    )

    print(
        "Mode:",
        "static" if STATIC else "animated",
    )


if __name__ == "__main__":
    main()
