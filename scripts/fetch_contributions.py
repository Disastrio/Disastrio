from pathlib import Path
import json
import re

import requests
from bs4 import BeautifulSoup


USERNAME = "Disastrio"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path("data/contributions.json")


def get_count(text):
    match = re.search(
        r"^\s*(\d[\d,]*)\s+contributions?",
        text,
        re.IGNORECASE,
    )

    if match:
        return int(
            match.group(1).replace(",", "")
        )

    return 0


def fetch():
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # Current GitHub has the day cells in the table.
    cells = soup.select(
        "td.ContributionCalendar-day[data-date]"
    )

    if not cells:
        raise RuntimeError(
            "No contribution cells found."
        )

    # Current GitHub keeps the tooltip text separately.
    # Each tool-tip's 'for' attribute points to the
    # corresponding contribution-day cell ID.
    tooltips = {}

    for tooltip in soup.select(
        ".js-calendar-graph tool-tip"
    ):
        target = tooltip.get("for")

        if target:
            tooltips[target] = tooltip.get_text(
                " ",
                strip=True,
            )

    days = []

    for cell in cells:

        raw_date = cell.get("data-date")

        if not raw_date:
            continue

        level = int(
            cell.get(
                "data-level",
                "0",
            )
        )

        cell_id = cell.get("id")

        tooltip_text = ""

        if cell_id:
            tooltip_text = tooltips.get(
                cell_id,
                "",
            )

        count = get_count(
            tooltip_text
        )

        days.append(
            {
                "date": raw_date,
                "count": count,
                "level": level,
            }
        )

    days.sort(
        key=lambda item: item["date"]
    )

    return days


def calculate_stats(days):

    total = sum(
        day["count"]
        for day in days
    )

    best_day = max(
        days,
        key=lambda day: day["count"],
    )

    longest_streak = 0
    streak = 0

    for day in days:

        if day["count"] > 0:
            streak += 1
            longest_streak = max(
                longest_streak,
                streak,
            )
        else:
            streak = 0

    current_streak = 0

    for day in reversed(days):

        if day["count"] > 0:
            current_streak += 1
        else:
            break

    monthly = {}

    for day in days:

        month = day["date"][:7]

        monthly[month] = (
            monthly.get(month, 0)
            + day["count"]
        )

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


def main():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    days = fetch()

    stats = calculate_stats(days)

    payload = {
        "username": USERNAME,
        "days": days,
        "stats": stats,
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Fetched {len(days)} contribution days."
    )

    print(
        f"Total contributions: "
        f"{stats['total']}"
    )

    print(
        f"Current streak: "
        f"{stats['current_streak']}"
    )

    print(
        f"Longest streak: "
        f"{stats['longest_streak']}"
    )

    print(
        f"Best day: "
        f"{stats['best_day']['date']} "
        f"({stats['best_day']['count']})"
    )

    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
