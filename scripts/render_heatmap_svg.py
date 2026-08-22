from pathlib import Path
from datetime import date, timedelta
import json
import html


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")


PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


CELL = 12
GAP = 3

LEFT = 36
TOP = 28

WIDTH = LEFT + (53 * (CELL + GAP)) + 20
HEIGHT = TOP + (7 * (CELL + GAP)) + 55


def esc(value):
    return html.escape(str(value))


def load_data():
    if not INPUT.exists():
        raise SystemExit(
            "Missing data/contributions.json. "
            "Run fetch_contributions.py first."
        )

    return json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )


def make_grid(days):
    by_date = {
        day["date"]: day
        for day in days
    }

    if not days:
        return []

    first = date.fromisoformat(
        days[0]["date"]
    )

    # Start on Sunday.
    start = first - timedelta(
        days=(first.weekday() + 1) % 7
    )

    cells = []

    for index in range(53 * 7):
        current = start + timedelta(
            days=index
        )

        key = current.isoformat()

        item = by_date.get(
            key,
            {
                "date": key,
                "count": 0,
                "level": 0,
            },
        )

        week = index // 7
        weekday = index % 7

        cells.append(
            {
                **item,
                "week": week,
                "weekday": weekday,
            }
        )

    return cells


def make_svg(data):
    days = data["days"]
    stats = data["stats"]

    cells = make_grid(days)

    parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg"
          width="{WIDTH}"
          height="{HEIGHT}"
          viewBox="0 0 {WIDTH} {HEIGHT}">

          <rect
            width="100%"
            height="100%"
            rx="12"
            fill="#0d1117"/>

          <style>
            text {{
              font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            }}

            .month {{
              fill: #8b949e;
              font-size: 10px;
            }}

            .day {{
              fill: #8b949e;
              font-size: 9px;
            }}

            .stat {{
              fill: #8b949e;
              font-size: 9px;
            }}
          </style>

          <text
            x="{LEFT}"
            y="15"
            class="month">
            CONTRIBUTIONS
          </text>
        '''
    ]

    # Weekday labels.
    labels = [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]

    for row, label in labels:
        y = TOP + row * (CELL + GAP) + 9

        parts.append(
            f'''
            <text
              x="2"
              y="{y}"
              class="day">
              {label}
            </text>
            '''
        )

    # Contribution cells.
    for cell in cells:

        x = (
            LEFT
            + cell["week"]
            * (CELL + GAP)
        )

        y = (
            TOP
            + cell["weekday"]
            * (CELL + GAP)
        )

        level = max(
            0,
            min(
                5,
                int(cell["level"])
            ),
        )

        color = PALETTE[level]

        parts.append(
            f'''
            <rect
              x="{x}"
              y="{y}"
              width="{CELL}"
              height="{CELL}"
              rx="3"
              fill="{color}">
              <title>
                {esc(cell["date"])}:
                {cell["count"]} contributions
              </title>
            </rect>
            '''
        )

    # Legend.
    legend_y = TOP + 7 * (CELL + GAP) + 10

    parts.append(
        f'''
        <text
          x="{LEFT}"
          y="{legend_y + 10}"
          class="stat">
          Less
        </text>
        '''
    )

    for level in range(6):
        x = (
            LEFT
            + 30
            + level * (CELL + GAP)
        )

        parts.append(
            f'''
            <rect
              x="{x}"
              y="{legend_y}"
              width="{CELL}"
              height="{CELL}"
              rx="3"
              fill="{PALETTE[level]}"/>
            '''
        )

    parts.append(
        f'''
        <text
          x="{LEFT + 30 + 6 * (CELL + GAP) + 4}"
          y="{legend_y + 10}"
          class="stat">
          More
        </text>
        '''
    )

    # Stats footer.
    footer_y = legend_y + 28

    parts.append(
        f'''
        <text
          x="{LEFT}"
          y="{footer_y}"
          class="stat">
          {stats["total"]:,} contributions
          · current streak {stats["current_streak"]}
          · longest streak {stats["longest_streak"]}
        </text>
        '''
    )

    parts.append("</svg>")

    return "".join(parts)


def main():
    data = load_data()

    svg = make_svg(data)

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
