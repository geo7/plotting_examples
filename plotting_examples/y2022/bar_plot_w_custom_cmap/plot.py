# pylint: disable=duplicate-code
"""
Bar plot with custom cmap.

Based on this tweet: https://twitter.com/ryanburge/status/1505602885215834112 - wanted
to create something with a similar effect using mpl.

Example of:

- Different font types (using monospace font)
- using different colours for bars depending on their values (custom cmap).
- padding around the axis using rc parameters
"""
from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

np_rnd = np.random.Generator(np.random.MT19937(0))


def generate_data() -> pd.DataFrame:
    """Create sample data."""
    n = 1_000
    return pd.DataFrame(
        {
            "race": np_rnd.choice(
                ["White", "Black", "Hispanic", "Asian", "All Others"],
                size=n,
            ),
            "church_attendance": np_rnd.choice(
                ["Never", "Seldom", "Yearly", "Monthly", "Weekly", "Weekly+"],
                size=n,
                p=[
                    0.1,
                    0.1,
                    0.1,
                    0.15,
                    0.25,
                    0.3,
                ],
            ),
        },
    ).sort_values("race")


def main() -> mpl.figure.Figure:
    """Main."""
    data = generate_data()

    ordering = [
        "Never",
        "Seldom",
        "Yearly",
        "Monthly",
        "Weekly",
        "Weekly+",
    ]

    loc = plticker.MultipleLocator(
        base=20.0,
    )  # this locator puts ticks at regular intervals

    with plt.rc_context(
        {
            "xtick.major.pad": 20,
            "font.family": "monospace",
        },
    ):
        fig, axis = plt.subplots(
            figsize=(30, 12),
            ncols=3,
            nrows=2,
            sharey=True,
            constrained_layout=False,
        )
        fig.tight_layout(h_pad=10, w_pad=10)

        axis = axis.flatten()

        # Style plots.
        for ax in axis:
            ax.grid(alpha=0.2, zorder=0)
            for x in ["top", "right", "left", "bottom"]:
                ax.spines[x].set_visible(False)
            ax.tick_params(axis="both", which="both", length=0, labelsize=18)

        fig.suptitle(
            "The Relationship Between Church Attendence and a Republican Vote by Race",
            fontsize=30,
            y=1.1,
            x=0.0,
            horizontalalignment="left",
        )
        # needs mpl version >= 3.4
        fig.supylabel(
            "Vote for Trump in 2020",
            fontsize=25,
            x=-0.02,
        )

        axis = iter(axis)

        for g, dfg in data.groupby("race"):
            color_map = mpl.colormaps["cool"].resampled(100)

            ax = next(axis)
            ax.yaxis.set_major_locator(loc)
            group_bar_values_unordered = (
                dfg["church_attendance"].value_counts().to_dict()
            )
            group_bar_values = {x: group_bar_values_unordered[x] for x in ordering}

            barplot = ax.bar(
                x=list(group_bar_values.keys()),
                height=list(group_bar_values.values()),
                zorder=3,
            )
            ax.set_title(g, fontsize=25, y=1.0)
            ax.set_ylim(bottom=0, top=90)
            ax.set_yticks([], minor=True)

            def fmt(x: float, _pos: int) -> str:
                # Not _too_ sure what this is about - think it's just what
                # set_major_formatter applies? It passes two arguments though - the
                # tick value (x) and the position (pos)...
                return f"{int(x)}"

            ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(fmt))

            for bar in barplot:
                # Set the bar color by bar height.
                bar.set_color(color_map(bar.get_height()))
                ax.text(
                    x=bar.get_x() + 0.5 * (bar.get_width()),
                    y=bar.get_y() + 2.5,
                    s=f"{bar.get_height()}%",
                    fontsize=20,
                    ha="center",
                )
                ax.vlines(
                    x=bar.get_x() + 0.5 * (bar.get_width()),
                    ymin=bar.get_height() - 5,
                    ymax=bar.get_height() + 5,
                    linewidth=4,
                    zorder=5,
                    color="#404040",
                )
                ax.hlines(
                    y=bar.get_height() - 5,
                    xmin=(bar.get_x() + 0.5 * (bar.get_width())) - 0.1,
                    xmax=(bar.get_x() + 0.5 * (bar.get_width())) + 0.1,
                    zorder=5,
                    linewidth=4,
                    color="#404040",
                )
                ax.hlines(
                    y=bar.get_height() + 5,
                    xmin=(bar.get_x() + 0.5 * (bar.get_width())) - 0.1,
                    xmax=(bar.get_x() + 0.5 * (bar.get_width())) + 0.1,
                    zorder=5,
                    linewidth=4,
                    color="#404040",
                )

            ax.tick_params(axis="y", colors="grey")
            ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

        # Just format the final plot - it's blank - to just get rid of all plot params
        # here. If there was more than one would need to handle a bit differently here.
        ax = next(axis)
        ax.grid(alpha=0)
        ax.set_xticks([])
        for x in ["top", "right", "left", "bottom"]:
            ax.spines[x].set_visible(False)

        ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    fig.set_tight_layout(True)
    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
