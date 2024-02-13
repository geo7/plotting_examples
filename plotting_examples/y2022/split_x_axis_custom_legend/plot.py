# pylint: disable=duplicate-code
"""
Example of creating multiple x-axis in order to plot year / months.

The fig size needs to be pretty large in order to squeeze all the month names etc in
here. Generated data looks a mess on these plots.

Example of:

- Custom legend
- generating random date data
- multiple x-axis to display years / months
"""
from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

np_rnd = np.random.Generator(np.random.MT19937(seed=0))


def random_dates(
    start: pd._libs.tslibs.timestamps.Timestamp,
    end: pd._libs.tslibs.timestamps.Timestamp,
    n_days: int,
    unit: str = "D",
) -> pd.Series:
    """
    Generate random dates.

    >>> start = pd.to_datetime('2015-01-01')
    >>> end = pd.to_datetime('2018-01-01')

    Found on a SO post, can't remember where now though.
    """
    ndays = (end - start).days + 1
    return pd.to_timedelta(np_rnd.random(n_days) * ndays, unit=unit) + start


def main() -> mpl.figure.Figure:
    """Main."""
    n = 10_000
    # generate sample data
    df = pd.DataFrame(
        {
            "location": np_rnd.choice(
                ["UK", "US", "FR", "JP", "DE"],
                size=n,
            ),
            "song": np_rnd.choice(
                [
                    "one two three",
                    "four five six",
                    "seven eight nine",
                    "ten eleven twelve",
                    "thirteen",
                    "fourteen",
                    "fifteen sixteen",
                ],
                size=n,
            ),
            "streams": np_rnd.integers(1_000, 10_000, size=n),
            "date": random_dates(
                start=pd.to_datetime("2020-01-01"),
                end=pd.to_datetime("2022-03-01"),
                n_days=n,
            ),
        },
    )
    # aggregate for plotting
    df = (
        df.groupby(["location", "song", pd.Grouper(key="date", freq="ME")])["streams"]
        .sum()
        .reset_index()
        # Aggregated to months so don't need date names here.
        .assign(
            date_name=df.date.dt.month_name() + " " + df.date.dt.year.astype(str),
            # Color mapping for song names to use in plotting
            color=lambda df: df["song"].map(
                {
                    "fifteen sixteen": metadata.color.TAN,
                    "four five six": metadata.color.PURPLEY,
                    "fourteen": "black",
                    "one two three": metadata.color.PINK_COLOUR,
                    "seven eight nine": metadata.color.DEEPER_GREEN,
                    "ten eleven twelve": metadata.color.BLUE,
                    "thirteen": metadata.color.BROWNY_RED,
                },
            ),
        )
    )

    def format_axis(ax: plt.Axes) -> None:
        """Format axis."""
        ax.grid(alpha=0.2)

    def stream_plot(df: pd.DataFrame, country: str, ax: plt.Axes) -> None:
        for _, song_data in df.groupby("song"):
            ax.plot(
                song_data["date"],
                song_data["streams"],
                color=song_data["color"].to_list().pop(),
                alpha=0.7,
                linewidth=3,
            )
            format_axis(ax=ax)
            ax.set_title(
                country,
                fontsize=20,
            )

            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha("right")

            ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

        # want to format 1000 -> 1,000
        ax.get_yaxis().set_major_formatter(
            mpl.ticker.FuncFormatter(lambda x, _: format(int(x), ",")),
        )
        # reduce some noise
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fmt_month = mdates.MonthLocator(interval=1)
        fmt_year = mdates.YearLocator()
        ax.xaxis.set_minor_locator(fmt_month)
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
        ax.xaxis.set_ticks([])

        ax.tick_params(axis="x", which="minor", labelsize=8)

        sec_xaxis = ax.secondary_xaxis(-0.1)
        sec_xaxis.xaxis.set_major_locator(fmt_year)
        sec_xaxis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        sec_xaxis.spines["bottom"].set_visible(False)
        sec_xaxis.tick_params(length=0, labelsize=12)

    color_dict = df.drop_duplicates("song").set_index("song")["color"].to_dict()

    fig, axis = plt.subplots(
        ncols=3,
        nrows=2,
        figsize=(35, 20),
    )
    plt.subplots_adjust(
        left=None,
        bottom=None,
        right=None,
        top=None,
        wspace=None,
        hspace=0.5,
    )

    axis = axis.flatten()
    iter(axis.flatten())

    plt.suptitle(
        "Streaming across different countries for different songs",
        fontsize=25,
    )

    stream_plot(
        df=df.loc[df["location"].eq("DE")],
        country="DE",
        ax=axis[0],
    )

    stream_plot(
        df=df.loc[df["location"].eq("FR")],
        country="FR",
        ax=axis[1],
    )

    stream_plot(
        df=df.loc[df["location"].eq("JP")],
        country="JP",
        ax=axis[2],
    )

    stream_plot(
        df=df.loc[df["location"].eq("UK")],
        country="UK",
        ax=axis[3],
    )

    stream_plot(
        df=df.loc[df["location"].eq("US")],
        country="US",
        ax=axis[5],
    )

    # Plot legend

    ax = axis[4]
    custom_lines = [Line2D([0], [0], color=x, lw=6) for x in color_dict.values()]
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    ax.legend(
        custom_lines,
        list(color_dict.keys()),
        loc="center",
        fontsize=16,
        frameon=False,
        borderpad=2,
    )

    for spine in ax.spines:
        ax.spines[spine].set_visible(False)

    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])

    fig.supylabel(
        "Something about the y-axis",
        x=0.09,
        fontsize=20,
    )

    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
        save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
