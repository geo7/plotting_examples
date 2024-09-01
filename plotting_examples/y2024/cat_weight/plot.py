"""
Timeseries of the cats diet.

Cat was getting a little chunky towards the end of 2023 so had a resolution made for
them to lose a bit of weight. Data collection is just a daily weigh, the average of
this is taken (as there are sometimes multiple entries in a day) and then plotted along
with a ten day rolling average. Most days were covered, where there are missing days
they're imputed using the average of the days either side, eg `(a, nan, b) -> (a,
(a+b)/2, b)` though this is just a plot...
"""

from __future__ import annotations

import datetime as dt
import pathlib
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2024 import metadata

np_rnd = np.random.Generator(np.random.MT19937(0))

LAYOUT = [
    ["title", "title", "title", "title", "top_right_corner", "top_right_corner"],
    ["main", "main", "main", "main", "side", "side"],
    ["main", "main", "main", "main", "side", "side"],
    ["main", "main", "main", "main", "side", "side"],
    ["main", "main", "main", "main", "side", "side"],
]
FONTSIZE_TITLE = 25
FONTSIZE_SUBTITLE = 15
COLOR_SUBTITLE_TEXT = "#808080"


def get_xlsx_from_downloads() -> Path:
    """
    Get xlsx file from Downloads.

    Pretty janky approach but it's near enough whilst doing this - workflow is just to
    download the xlsx file containing the gform responses from gsheets then this will
    pick it up and move it to this project as a parquet file. Wasn't worth using the
    API for it.
    """
    output_name = Path(__file__).parent / "data" / "weight_data.parquet"
    xlsx_files = sorted((pathlib.Path.home() / "Downloads").glob("*espon*xlsx"))

    if len(xlsx_files) == 0:
        # Most likely this is re-running and has already been moved so just use
        # whatever's already in data/.
        return output_name

    if len(xlsx_files) > 1:
        msg = "Expected a single file: "
        raise ValueError(msg, xlsx_files)

    # Get response data from xlsx sheet, pull out required columns and create date
    # column for grouping on
    df_response = (
        pd.ExcelFile(xlsx_files[0])
        .parse("Form responses 1")
        .rename(columns=lambda x: x.lower())
        .assign(
            timestamp=lambda x: pd.to_datetime(
                x["timestamp"],
                format="%d/%m/%Y %H:%M:%S",
            ),
            # Some of the days have multiple weigh-ins so want datestamp to group by on
            # in those days.
            datestamp=lambda x: pd.to_datetime(
                x["timestamp"].apply(lambda x: x.date())
            ),
            mish_weight=lambda x: x["with_mish"].sub(x["without_mish"]),
        )
        .loc[:, ["timestamp", "datestamp", "mish_weight"]]
    ).rename(columns={"mish_weight": "cat_weight"})

    df_response.to_parquet(output_name)
    return output_name


def load_data(*, data_path: Path) -> pd.DataFrame:
    """Get response dataframe from downloaded xlsx file."""
    response_data = pd.read_parquet(data_path)
    return (
        response_data
        # Only need these two columns.
        .groupby("datestamp")["cat_weight"]
        # Sometimes there are multiple readings in a day
        .mean()
        .reset_index()
        .rename(columns={"cat_weight": "cat_daily_avg"})
    )


def main() -> mpl.figure.Figure:
    """
    Main.

    I did consider adding some figure shapes along the lines of:

    >>> for _ in range(1, 30):
    >>>     factor = 20
    >>>     radius = np_rnd.random() / factor
    >>>     alpha = ((1 / factor) - radius) + 0.1
    >>>     circ = patches.Circle(
    >>>         (np_rnd.random(), np_rnd.random()),
    >>>         radius=radius,
    >>>         zorder=1,
    >>>         color=color.PINK_COLOUR,
    >>>         alpha=alpha,
    >>>     )
    >>>     circ.set_transform(fig.transFigure)
    >>>     fig.patches.append(circ)

    But left it.
    """
    df = load_data(data_path=get_xlsx_from_downloads())
    df_dates = pd.DataFrame(
        {
            "dates": pd.date_range(
                df["datestamp"].min(),
                df["datestamp"].max(),
            )
        }
    ).assign(month_name=lambda x: x["dates"].dt.strftime("%B"))

    # Ensure that all dates are represented (in case there's missed weigh-in days).
    df = (
        pd.merge(
            df, df_dates[["dates"]], left_on="datestamp", right_on="dates", how="right"
        )
        .drop(columns="datestamp")
        .rename(columns={"dates": "datestamp"})
        .set_index("datestamp")
        .reset_index()
        .assign(imputed=lambda x: x["cat_daily_avg"].isna())
    )
    # Handle missing data - only expecting there to be a day of missing data at
    # most!
    df["cat_daily_avg"] = df.assign(
        ff=df["cat_daily_avg"].ffill(),
        bf=df["cat_daily_avg"].bfill(),
        filled=lambda x: x["ff"].add(x["bf"]).div(2),
    )["filled"]

    df = df.assign(r10=lambda x: x["cat_daily_avg"].rolling(10).mean())

    color = metadata.color

    # Create some columns for styling the scatter points - mainly in order to
    # differentiate between imputed days and actual days.
    df["scatter_color"] = color.GREY
    df.loc[df["imputed"], "scatter_color"] = color.GREY
    df["scatter_size"] = 10
    df.loc[df["imputed"], "scatter_size"] = 0

    with plt.rc_context(
        {
            "xtick.major.pad": 5,
            "font.family": "monospace",
        },
    ):
        fig = plt.figure(figsize=(28, 10))
        ax_dict = fig.subplot_mosaic(LAYOUT)  # type: ignore[arg-type]

        # Plot rolling average
        ax_dict["main"].plot(
            df["datestamp"],
            df["r10"],
            color=color.PINK_COLOUR,
            lw=3,
            zorder=10,
        )

        # Want to ensure that no daily lines are drawn where data has been imputed -
        # will still create the rolling average line here.
        for _, data in df.assign(groups=df["imputed"].cumsum()).groupby("groups"):
            ax_dict["main"].plot(
                data["datestamp"].loc[~data["imputed"]],
                data["cat_daily_avg"].loc[~data["imputed"]],
                color=color.GREY,
                lw=1,
                zorder=5,
            )

        ax_dict["main"].scatter(
            df["datestamp"],
            df["cat_daily_avg"],
            color=df["scatter_color"],
            s=df["scatter_size"],
            zorder=5,
        )

        ax_dict["main"].set_ylabel("Weight kg")
        ax_dict["main"].xaxis.set_major_locator(mdates.DayLocator(interval=7))  # type: ignore[no-untyped-call]

        for label in ax_dict["main"].get_xticklabels():
            label.set_rotation(80)
            label.set_ha("center")  # type: ignore[attr-defined]

        # Remove spines for top/right
        ax_dict["main"].spines["top"].set_visible(False)
        ax_dict["main"].spines["right"].set_visible(False)

        # Set x-axis dates to just be day/month instead of year day month.
        ax_dict["main"].xaxis.set_major_locator(mdates.DayLocator(interval=7))  # type: ignore[no-untyped-call]
        ax_dict["main"].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))  # type: ignore[no-untyped-call]

        for label in ax_dict["main"].get_xticklabels():
            label.set_rotation(80)
            label.set_ha("center")

        heaviest_idx = df["cat_daily_avg"].idxmax()
        _ = ax_dict["main"].annotate(
            f"{df['cat_daily_avg'].loc[heaviest_idx].round(2)} kg",
            # where the arrow should end up
            xy=(
                df["datestamp"].iloc[heaviest_idx],
                df["cat_daily_avg"].iloc[heaviest_idx],
            ),
            # where the text should be
            xytext=(
                df["datestamp"].iloc[heaviest_idx + 5],
                df["cat_daily_avg"].iloc[heaviest_idx + 1] + 0.25,
            ),
            ha="center",
            va="bottom",
            arrowprops={
                "arrowstyle": "->",
                "connectionstyle": "arc3,rad=0.2",
                "color": color.PINK_COLOUR,
            },
        )

        lightest_idx = df["cat_daily_avg"].idxmin()
        _ = ax_dict["main"].annotate(
            f"{df['cat_daily_avg'].loc[lightest_idx].round(2)} kg",
            # where the arrow should end up
            xy=(
                df["datestamp"].iloc[lightest_idx],
                df["cat_daily_avg"].iloc[lightest_idx],
            ),
            # where the text should be
            xytext=(
                df["datestamp"].iloc[lightest_idx - 5],
                df["cat_daily_avg"].iloc[lightest_idx],
            ),
            ha="center",
            va="bottom",
            arrowprops={
                "arrowstyle": "->",
                "connectionstyle": "arc3,rad=0.35",
                "color": color.PINK_COLOUR,
            },
        )

        ax_dict["main"].grid(linewidth=0.2, which="major", axis="y")

        # Put cat picture in top left
        img_path = Path(__file__).parent / "data" / "cat_looking_to_side.jpeg"
        cat_img = Image.open(img_path)
        ax_dict["side"].imshow(cat_img, zorder=10)
        ax_dict["side"].axis("off")

        # Remove axis from particular layouts
        for section in {
            x
            for lst in LAYOUT
            for x in lst
            if x
            not in [
                "main",
            ]
        }:
            ax_dict[section].axis("off")

        # Add Title
        data_from = dt.datetime(
            df["datestamp"].min().year,
            df["datestamp"].min().month,
            df["datestamp"].min().day,
            tzinfo=dt.UTC,
        ).strftime("%Y-%m-%d")
        data_to = dt.datetime(
            df["datestamp"].max().year,
            df["datestamp"].max().month,
            df["datestamp"].max().day,
            tzinfo=dt.UTC,
        ).strftime("%Y-%m-%d")

        diff = 0.3
        title_x = 0.1
        title_x = 0.0
        ax_dict["title"].text(
            s="Cat Weight",
            x=title_x,
            y=0.5,
            fontsize=FONTSIZE_TITLE,
            horizontalalignment="left",
            verticalalignment="bottom",
        )

        ax_dict["title"].text(
            s=f"{data_from} -> {data_to}",
            x=title_x,
            y=0.5 - diff,
            fontsize=FONTSIZE_SUBTITLE,
            horizontalalignment="left",
            verticalalignment="bottom",
            color=COLOR_SUBTITLE_TEXT,
        )

        for axis in {x for lst in LAYOUT for x in lst}:
            ax_dict[axis].set_facecolor(metadata.color.BACKGROUND_COLOUR)

        fig.set_tight_layout(True)  # type: ignore[attr-defined]
        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)

        return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
