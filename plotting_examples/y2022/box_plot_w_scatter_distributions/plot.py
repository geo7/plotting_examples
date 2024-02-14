# pylint: disable=duplicate-code,too-many-locals
"""
Bar plot with distributions.

Thought I'd create a bar plot with scatter plots of the distributions adjacent to the
bars, it was based off something else but I can't remember what. Bar plots are created
from scratch using hlines etc, for no particular reason.

Data was from tidy tuesday.
"""
from __future__ import annotations

import pathlib
from typing import TypeVar

import attr
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

np_rnd = np.random.Generator(np.random.MT19937(1))

T = TypeVar("T")

WEEK = "week42"

DATA_URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/"
    "master/data/2021/2021-10-19/pumpkins.csv"
)

BACKGROUND_COLOUR = "#f2f2f2"
# https://mycolor.space/?hex=%23FF69B4&sub=1
PINK_COLOUR = "#ff69b4"
LABEL_FONTSIZE = 12


def clean_comma(df: pd.DataFrame, *, column: str) -> pd.DataFrame:
    """Replace commas in series with empty strings."""
    df = df.copy()
    row_mask = df[column].astype(str).str.contains(",")
    df.loc[row_mask, column] = (
        df.loc[row_mask, column].str.replace(",", "").astype(float)
    )
    return df


def drop_rows_by_match_on_column(
    df: pd.DataFrame,
    *,
    column: str,
    regexp: str,
) -> pd.DataFrame:
    """Drop rows based on regex on a particular column."""
    df = df.copy()
    return df.loc[~df[column].astype(str).str.contains(regexp, regex=True)]


def top_n_groups(
    df: pd.DataFrame,
    *,
    column: str,
    n: int,
    rename: str = "Other",
) -> pd.DataFrame:
    """Get top n groups for a given column, re-write rest to other."""
    df = df.copy()
    top_n = df[column].value_counts(dropna=False).head(n).index
    df.loc[~df[column].isin(top_n), column] = rename
    return df


def clean(
    *,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Initial cleaning for all columns."""
    df = df.copy()
    return (
        df.pipe(
            drop_rows_by_match_on_column,
            column="country",
            regexp=".*Entries.*",
        )
        .pipe(clean_comma, column="weight_lbs")
        .assign(weight_lbs=lambda x: x["weight_lbs"].astype(float))
        .pipe(clean_comma, column="est_weight")
        .assign(est_weight=lambda x: x["est_weight"].astype(float))
        .assign(ott=lambda x: x["ott"].astype(float))
        .assign(pct_chart=lambda x: x["pct_chart"].astype(float))
    )


@attr.frozen(kw_only=True)
class PlotData:
    # pylint: disable=too-few-public-methods

    """Data for use in both box and scatter plotting."""

    box: pd.DataFrame
    scatter: list[float]


def plot_data_for_weight_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """Generate plot data."""
    df = df.copy()
    df = top_n_groups(df=df, column="country", n=9, rename="Other")
    df = df[["country", "weight_lbs"]]
    df = pd.concat(
        [
            df[["country", "weight_lbs"]],
            df[["country", "weight_lbs"]].assign(country="All Countries"),
        ],
        axis=0,
    )
    # we want to order the countries by the median of the weights for each group.
    sorting = list(
        df.groupby("country")["weight_lbs"].median().sort_values().index,
    )
    df = df.iloc[pd.Categorical(df["country"], sorting).argsort()]

    country_data = {}
    for g, dfg in df.groupby("country"):
        country_data[g] = PlotData(
            box=dfg.describe(),
            scatter=dfg["weight_lbs"].to_list(),
        )
    return country_data


# --------------------------------------------------------------------------------------

# PLOTTING METHODS


def top_bottom_whisker_y_values(*, values: list[float]) -> tuple[float, float]:
    """Get top/bottom for boxplot whiskers."""
    series = pd.Series(values)
    quant_1 = series.describe().get("25%")
    quant_3 = series.describe().get("75%")
    iqr = quant_3 - quant_1
    top_range = quant_3 + 1.5 * (iqr)
    bottom_range = quant_3 - 1.5 * iqr
    # top of the boxplot
    box_plot_top = series[series.lt(top_range)].max()
    # bottom of the box_plot
    box_plot_bottom = series[series.gt(bottom_range)].min()
    return box_plot_bottom, box_plot_top


def boxp_hline(
    *,
    ax: plt.Axes,  # type: ignore[name-defined]
    x_center: float,
    y_value: float,
    box_width: float,
    linewidth: float,
    box_colour: str,
) -> None:
    """Plot top/bottom of box."""
    ax.hlines(
        y=y_value,
        xmin=x_center - box_width * 0.5,
        xmax=x_center + box_width * 0.5,
        linewidth=linewidth,
        color=box_colour,
        zorder=3,
        capstyle="round",
    )


def boxp_vline(
    ax: plt.Axes,  # type: ignore[name-defined]
    x: float,
    ymin: float,
    ymax: float,
    color: str,
    linewidth: float,
) -> None:
    """Plot sides of box."""
    ax.vlines(
        x=x,
        ymin=ymin,
        ymax=ymax,
        color=color,
        linewidth=linewidth,
        zorder=3,
        capstyle="round",
    )


def whisker_tops(
    *,
    ax: plt.Axes,  # type: ignore[name-defined]
    whisker_top: float,
    whisker_bottom: float,
    xmin: float,
    xmax: float,
    color: str,
) -> None:
    """Plot tops of the whiskers."""
    ax.hlines(
        y=whisker_top,
        xmin=xmin,
        xmax=xmax,
        color=color,
        zorder=1,
    )
    ax.hlines(
        y=whisker_bottom,
        xmin=xmin,
        xmax=xmax,
        color=color,
        zorder=1,
    )


def make_single_box(
    *,
    ax: plt.Axes,  # type: ignore[name-defined]
    values: list[float],
    x_center: float,
    scatter_color: str,
    linewidth: float = 5,
    box_width: float = 0.14,
    box_colour: str = "#000000",
    whisker_color: str = "#000000",
    median_colour: str = "#000000",
    outlier_colour: str = "#000000",
) -> None:
    """Add boxplot to given axis."""
    plotting_data = pd.Series(values).describe().to_dict()

    # ----------------------------------------------------------------------------------
    # create the box - there's not _really_ any reason for this other than being
    # curious at the time about creating a boxplot from scratch... it'd be a better
    # idea i think to just create a rectangle instead.
    boxp_hline(
        ax=ax,
        x_center=x_center,
        y_value=plotting_data["25%"],
        box_width=box_width,
        linewidth=linewidth,
        box_colour=box_colour,
    )
    boxp_hline(
        ax=ax,
        x_center=x_center,
        y_value=plotting_data["75%"],
        box_width=box_width,
        linewidth=linewidth,
        box_colour=box_colour,
    )
    boxp_vline(
        ax=ax,
        x=x_center + box_width * 0.5,
        ymin=plotting_data["25%"],
        ymax=plotting_data["75%"],
        color=box_colour,
        linewidth=linewidth,
    )
    boxp_vline(
        ax=ax,
        x=x_center - box_width * 0.5,
        ymin=plotting_data["25%"],
        ymax=plotting_data["75%"],
        color=box_colour,
        linewidth=linewidth,
    )

    # ----------------------------------------------------------------------------------
    # create the median line

    ax.hlines(
        y=plotting_data["50%"],
        xmin=x_center - box_width * 0.5,
        xmax=x_center + box_width * 0.5,
        color=median_colour,
        zorder=1,
        linewidth=linewidth,
    )

    # ----------------------------------------------------------------------------------
    # create top/bottom of whiskers
    whisker_bottom, whisker_top = top_bottom_whisker_y_values(values=values)

    # ----------------------------------------------------------------------------------
    # plot vertial whisker lines

    # create vertical lines
    ax.vlines(
        x=x_center,
        ymin=plotting_data["75%"],
        ymax=whisker_top,
        color=whisker_color,
        capstyle="round",
    )
    ax.vlines(
        x=x_center,
        ymin=plotting_data["25%"],
        ymax=whisker_bottom,
        color=whisker_color,
        capstyle="round",
    )

    # ----------------------------------------------------------------------------------
    # plot the outliers

    # plot outliers
    series = pd.Series(values)
    outliers = series[series.lt(whisker_bottom) | series.gt(whisker_top)]
    ax.scatter(
        x=[x_center for _ in outliers],
        y=list(outliers),
        color=outlier_colour,
        s=5,
        alpha=0.8,
        edgecolors=None,
    )

    # ----------------------------------------------------------------------------------
    # plot the scatter of values

    x_values = np_rnd.normal(
        loc=x_center + 0.2,
        scale=0.03,
        size=len(values),
    )
    ax.scatter(
        x=x_values,
        y=values,
        alpha=0.1,
        s=10,
        zorder=-1,
        color=scatter_color,
        edgecolors=None,
    )


def example(*, df: pd.DataFrame) -> mpl.figure.Figure:
    """Generate example plot."""
    country_data = plot_data_for_weight_by_country(df=df)
    fig, ax = plt.subplots(figsize=(20, 8))

    country_metadata: dict[str, dict[str, str]] = {
        "France": {},
        "Japan": {},
        "Canada": {},
        "Germany": {},
        "United Kingdom": {},
        "Italy": {},
        "United States": {},
        "Austria": {},
        "Belgium": {},
        "Other": {"scatter_color": "#919191"},
        "All Countries": {"scatter_color": "#919191"},
    }
    xpos = 1.0
    xpos_inc = 0.5

    for country in country_metadata:
        data = country_data[country]
        color = "#919191" if country in ["Other", "All Countries"] else PINK_COLOUR
        make_single_box(
            ax=ax,
            values=data.scatter,
            x_center=xpos,
            linewidth=1.5,
            scatter_color=color,
            outlier_colour="#000000",
        )
        xpos += xpos_inc

    # ----------------------------------------------------------------------------------
    # format tick labels

    ax.set_xticks(np.arange(1, xpos, xpos_inc))
    ax.set_xticklabels(list(country_metadata.keys()))

    # ----------------------------------------------------------------------------------
    # plot formatting / spines / background.

    ax.tick_params(axis="both", which="both", length=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    ax.grid(alpha=0.15, axis="y", zorder=0)

    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    # ----------------------------------------------------------------------------------
    # titles and axis labels
    ax.set_title(
        "This is something about pumpkin competitions or something like that.",
        color="#919191",
        fontsize=LABEL_FONTSIZE,
    )
    fig.suptitle(
        "Data Visualization of Competitive Pumpkin Sport 2013-2021",
        fontsize=20,
    )
    ax.set_ylabel("Weight lbs", fontsize=LABEL_FONTSIZE)
    ax.yaxis.set_label_coords(-0.05, 0.5)
    return fig


def main() -> mpl.figure.Figure:
    """Main."""
    df = pd.read_parquet(pathlib.Path(__file__).parent / "data.parquet")
    df = clean(df=df)

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        return example(df=df)


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
