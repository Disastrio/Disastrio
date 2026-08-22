from pathlib import Path
import json
from datetime import date, timedelta


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

LEFT = 42
TOP = 32

WEEKS = 53
DAYS = 7

WIDTH = LEFT + WEEKS * (CELL + GAP) + 15
HEIGHT = TOP + DAYS * (CELL + GAP) + 65


def load():

    return json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )


def main():

    data = load()

    days = data["days"]
    stats = data["stats"]

    by_date = {
        x["date"]: x
        for x in days
    }

    newest = date.fromisoformat(
        days[-1]["date"]
    )

    start = newest - timedelta(days=364)

    # Align the first date to Sunday.
    start -= timedelta(
        days=(start.weekday() + 1) % 7
    )

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
            fill="#0d1117"/>

          <style>
            .title {{
              fill: #c9d1d9;
              font-family: sans-serif;
              font-size: 13px;
              font-weight: 600;
            }}

            .label {{
              fill: #8b949e;
              font-family: sans-serif;
              font-size: 9px;
            }}
          </style>

          <text
            x="18"
            y="19"
            class="title">
            CONTRIBUTIONS
          </text>
        '''
    ]

    # Weekday labels.
    for row, label in [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]:

        y = TOP + row * (CELL + GAP) + 9

        parts.append(
            f'''
            <text
              x="2"
              y="{y}"
              class="label">
              {label}
            </text>
            '''
        )

    # Grid.
    for index in range(WEEKS * DAYS):

        current = (
            start
            + timedelta(days=index)
        )

        week = index // DAYS
        weekday = index % DAYS

        item = by_date.get(
            current.isoformat(),
            {
                "count": 0,
                "level": 0,
            },
        )

        level = max(
            0,
            min(
                5,
                int(item["level"]),
            ),
        )

        x = (
            LEFT
            + week * (CELL + GAP)
        )

        y = (
            TOP
            + weekday * (CELL + GAP)
        )

        parts.append(
            f'''
            <rect
              x="{x}"
              y="{y}"
              width="{CELL}"
              height="{CELL}"
              rx="3"
              fill="{PALETTE[level]}">

              <title>
                {current.isoformat()}:
                {item["count"]} contributions
              </title>

            </rect>
            '''
        )

    legend_y = (
        TOP
        + DAYS * (CELL + GAP)
        + 14
    )

    parts.append(
        f'''
        <text
          x="18"
          y="{legend_y + 10}"
          class="label">
          Less
        </text>
        '''
    )

    for level, color in enumerate(PALETTE):

        x = (
            48
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
              fill="{color}"/>
            '''
        )

    parts.append(
        f'''
        <text
          x="{48 + 6 * (CELL + GAP) + 4}"
          y="{legend_y + 10}"
          class="label">
          More
        </text>

        <text
          x="18"
          y="{legend_y + 32}"
          class="label">
          {stats["total"]:,} contributions
          · streak {stats["current_streak"]}
          · best {stats["longest_streak"]}
        </text>

        </svg>
        '''
    )

    OUTPUT.write_text(
        "".join(parts),
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
