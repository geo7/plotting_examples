# pylint: disable=duplicate-code
"""
Visualise time tracking, how much over/under time.

Mainly serves as an example of plotting with dates, and filling above / below
particular values on a plot.

Example of:

- plotting with dates
- different fonts
- filling between lines
"""

from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

PINK_COLOUR = "#ff69b4"


def main() -> mpl.figure.Figure:
    """Main."""
    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, ax = plt.subplots(
            figsize=(15, 5),
            ncols=1,
            nrows=1,
            sharey=True,
            constrained_layout=False,
        )

        df = (
            pd.read_csv(
                "./plotting_examples/y2022/line_plot_fill_between/data.csv",
            )
            .rename(columns=lambda x: x.lower().replace(" ", "_").strip())
            .assign(y=lambda df: df["amount"])
        )

        # Create date column from separate columns in sheet data.
        df["date"] = pd.to_datetime(
            df["day"].astype(str)
            + "/"
            + df["month"].astype(str)
            + "/"
            + df["year"].astype(str),
            format="%d/%m/%Y",
        )

        # Interested in the cumulative sum either way.
        df["y_cumsum"] = df["y"].cumsum()

        # For creating the plot title.
        date_min = df["date"].min().date().strftime("%d/%m/%Y")
        date_max = df["date"].max().date().strftime("%d/%m/%Y")

        # highlight break.
        up_to_break = df["month"].le(3) & df["day"].le(28)
        past_break = df["month"].ge(4) & df["day"].ge(11)

        fig, ax = plt.subplots(figsize=(25, 15))

        # before break
        ax.plot(
            df.loc[up_to_break, "date"],
            df.loc[up_to_break, "y_cumsum"],
            color="black",
            linewidth=2,
        )
        # after break
        ax.plot(
            df.loc[past_break, "date"],
            df.loc[past_break, "y_cumsum"],
            color="black",
            linewidth=2,
        )

        # Put black points on values which were over 60.
        ax.scatter(
            x=df.loc[df["y"].gt(60), "date"],
            y=df.loc[df["y"].gt(60), "y_cumsum"],
            s=100,
            color="black",
            zorder=3,
        )

        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # type: ignore[no-untyped-call]
        ax.grid(alpha=0.15)

        # labels
        ax.set_ylabel(
            "Units over/under",
            fontsize=15,
        )
        ax.set_title(
            f"Information about something useful, from {date_min} to {date_max}",
            fontsize=25,
        )

        # Text
        ax.text(
            x=df["date"].to_list()[2],
            y=1500,
            s=(
                "Shows information about something for some time which was interesting."
                " \nBlack points indicate something of particular note."
            ),
            fontsize=25,
        )

        # Color beneath plot based on whether it's over or under 0.
        # Before holiday.
        ax.fill_between(
            df.loc[up_to_break, "date"],
            0,
            df.loc[up_to_break, "y_cumsum"],
            alpha=0.5,
            color=metadata.color.PINK_COLOUR,
            where=df.loc[up_to_break, "y_cumsum"] >= 0,
        )
        ax.fill_between(
            df.loc[up_to_break, "date"],
            0,
            df.loc[up_to_break, "y_cumsum"],
            alpha=0.5,
            color=metadata.color.GREY,
            where=df.loc[up_to_break, "y_cumsum"] <= 0,
        )

        # Past holiday
        ax.fill_between(
            df.loc[past_break, "date"],
            0,
            df.loc[past_break, "y_cumsum"],
            alpha=0.5,
            color=metadata.color.PINK_COLOUR,
            where=df.loc[past_break, "y_cumsum"] >= 0,
        )
        ax.fill_between(
            df.loc[past_break, "date"],
            0,
            df.loc[past_break, "y_cumsum"],
            alpha=0.5,
            color=metadata.color.GREY,
            where=df.loc[past_break, "y_cumsum"] <= 0,
        )

        # Format default axis to just show the month/day.
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # type: ignore[no-untyped-call]
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))  # type: ignore[no-untyped-call]

        for label in ax.get_xticklabels():
            label.set_rotation(80)
            label.set_ha("center")

    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    fig.set_tight_layout(True)  # type: ignore[attr-defined]
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
