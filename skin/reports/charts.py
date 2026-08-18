import matplotlib

# PDF/server environment — do not use a GUI backend
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import os
import tempfile

from datetime import datetime
from zoneinfo import ZoneInfo


def parse_date(date_string):
    """
    Convert ISO timestamp to local Indian time.
    """

    if not date_string:
        return None

    try:
        date = datetime.fromisoformat(date_string)

        if date.tzinfo is not None:
            date = date.astimezone(
                ZoneInfo("Asia/Kolkata")
            )

        return date

    except (ValueError, TypeError):
        return None


def create_line_chart(chart_data, title, ylabel):

    raw_labels = chart_data.get("labels", [])
    values = chart_data.get("values", [])

    if not raw_labels or not values:
        return None

    dates = []

    for label in raw_labels:

        date = parse_date(label)

        if date:
            dates.append(date)

    if not dates:
        return None

    fig, ax = plt.subplots(
        figsize=(8, 3.5)
    )

    ax.plot(
        dates,
        values,
        marker="o",
        linewidth=2,
        color="#4a7c73",
        markerfacecolor="#ffffff",
        markeredgecolor="#4a7c73",
        markeredgewidth=2,
        markersize=6,
    )

    ax.set_title(title, fontsize=13, fontweight="bold", color="#1e293b")
    ax.set_ylabel(ylabel, fontsize=10, color="#475569")

    ax.grid(
        axis="y",
        alpha=0.2
    )

    # Match the app's card look — no heavy chart border
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#e2e8f0")

    # -----------------------------------------
    # X AXIS
    # -----------------------------------------

    first_date = min(dates)
    last_date = max(dates)

    same_calendar_day = first_date.date() == last_date.date()

    if same_calendar_day:

        # All scans happened on the same calendar day.
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%I:%M %p",
                tz=ZoneInfo("Asia/Kolkata")
            )
        )

    else:

        # Scans span multiple calendar days.
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d %b\n%I:%M %p",
                tz=ZoneInfo("Asia/Kolkata")
            )
        )

    ax.xaxis.set_major_locator(
        mdates.AutoDateLocator(
            minticks=4,
            maxticks=8
        )
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=0,
        ha="center"
    )

    fig.tight_layout()

    # -----------------------------------------
    # CREATE TEMP FILE
    # -----------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".png",
        prefix="lumina_",
        delete=False
    )

    path = temp_file.name

    temp_file.close()

    fig.savefig(
        path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    return path