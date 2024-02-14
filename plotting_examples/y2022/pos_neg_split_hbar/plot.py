# pylint: disable=duplicate-code
"""
Create split horizontal bar chart.

Split by dichotomous variable, with bar classifications.

Can be a bit messy - not sure I'm much of a fan - but wanted to re-create anyway.
"""
from __future__ import annotations

import io
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as plt_ticker
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

# This the dichotomy - could be anything though, eg good/bad, old/young or whatever.
LEVEL_0 = "good"
LEVEL_1 = "bad"


def sample_data() -> tuple[pd.DataFrame, dict[int, str], dict[str, str]]:
    """
    Return sample dataframe.

    Dogs are taken from here : https://dogtime.com/dog-breeds/profiles
    """
    df = pd.read_csv(
        io.StringIO(
            (
                f"{LEVEL_0},{LEVEL_1},nr,{LEVEL_0}_colour,{LEVEL_1}_colour,meaning\n"
                "47.303474,51.18364658,1.51287942,med,med,Akita\n"
                "34.10226721,44.76493548,21.13279731,med,med,Basset Hound\n"
                "12.08045446,69.67354868,18.24599686,low,med,Cavapoo\n"
                "60.91476132,22.71988935,16.36534934,med,low,Doberdor\n"
                "19.43282773,56.88924657,23.67792571,low,med,Greyhound\n"
                "54.05072885,29.96153606,15.98773508,med,low,Irish Terrier\n"
                "53.096035,35.37625972,11.52770528,med,med,Poodle\n"
                "78.23942162,17.26331569,4.497262699,high,low,Sloughi\n"
                "51.68818968,38.14985888,10.16195143,med,med,Whippet\n"
                "38.14462181,39.1176673,22.73771089,med,med,Xoloitzcuintli\n"
            ),
        ),
    )
    index_to_meaning_map: dict[int, str] = df["meaning"].to_dict()
    # high/med/low represent some pretend classifications for this example.
    colour_map = {
        "high": metadata.color.PINK_COLOUR,
        "med": metadata.color.TAN,
        "low": metadata.color.LIGHT_GREEN,
    }
    return df, index_to_meaning_map, colour_map


def plot_bar_percentages(df: pd.DataFrame, ax: plt.Axes) -> plt.Axes:  # type: ignore[name-defined]
    """Plot percentages next to bars."""
    # Plot the percentages.
    for i, patch in enumerate(ax.patches):
        width = patch.get_width()
        height = patch.get_height()
        x, y = patch.get_xy()
        # Shifting is different depending on whether it's a +ve of -ve
        val = round(patch.get_width() * 0.01, 2)

        nudge = 8
        if i <= df.index.max():
            # Printing to the left
            ann = f"{-val:.0%}"
            ax.annotate(
                ann,
                ((x + width) - nudge, y + height * 0.5),
                ha="center",
                va="center",
            )
        else:
            # Printing to the right
            ann = f"{val:.0%}"
            ax.annotate(
                ann,
                ((x + width) + nudge, y + height * 0.5),
                ha="center",
                va="center",
            )
    return ax


def main() -> mpl.figure.Figure:
    """Main."""
    df, index_to_meaning_map, colour_map = sample_data()

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        # Create plot.
        fig, ax = plt.subplots(figsize=(15, 6))

        ax.set_axisbelow(True)

        ax.barh(
            df.index,
            width=-df[LEVEL_0],
            height=0.8,
            color=df[f"{LEVEL_0}_colour"].map(colour_map),
            edgecolor="black",
        )
        ax.barh(
            df.index,
            width=df[LEVEL_1],
            height=0.8,
            color=df[f"{LEVEL_1}_colour"].map(colour_map),
            edgecolor="black",
        )

        ax = plot_bar_percentages(df=df, ax=ax)

        # remove spines for top/right
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Set axis limits
        ax.set_ylim(bottom=-1, top=df.index.max() + 1)
        ax.set_xlim(left=-109, right=109)

        # Reformat tick frequency for x,y axis
        # x
        loc = plt_ticker.MultipleLocator(base=10)
        ax.xaxis.set_major_locator(loc)
        # y
        loc = plt_ticker.MultipleLocator(base=1)
        ax.yaxis.set_major_locator(loc)

        # Functions for reformatting plot tick values
        def x_fmt(x: float, _y: int) -> str:
            fmt = f"{int(x)} %"
            return fmt.replace("-", "")

        def y_fmt(_x: float, y: int) -> str:
            diff = -2
            return index_to_meaning_map.get(y + diff, "")

        ax.xaxis.set_major_formatter(plt_ticker.FuncFormatter(x_fmt))
        ax.yaxis.set_major_formatter(plt_ticker.FuncFormatter(y_fmt))

        # Plot text for Agree / Disagree
        agree_disagree_txt_height = 1.1
        ax.text(
            0.48,
            agree_disagree_txt_height,
            s=LEVEL_0,
            transform=ax.transAxes,
            ha="right",
            fontsize=20,
        )
        ax.text(
            0.52,
            agree_disagree_txt_height,
            s=LEVEL_1,
            transform=ax.transAxes,
            ha="left",
            fontsize=20,
        )

        for tick in ax.get_xticklabels():
            tick.set_rotation(45)

        ax.grid(linewidth=0.2, which="major", axis="y")

        fig.set_tight_layout(True)  # type: ignore[attr-defined]
        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
        ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
