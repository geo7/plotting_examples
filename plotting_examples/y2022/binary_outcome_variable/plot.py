# pylint: disable=duplicate-code
"""
Plot dichotomous variable.

Simple dots with median lines - might be nice to add a kde to this as well.

The y-axis is redundant here as there are only two options (`0.6` doesn't make any sense).
"""

from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def make_data() -> pd.DataFrame:
    """Generate some sample data for testing with."""
    np.random.seed(1)
    N = 1_00
    y = np.random.choice([0, 1], N)
    x = np.random.normal(0, 1, N) + np.random.normal(2, 1, N) * y
    return pd.DataFrame(np.array([x, y]).T, columns=["x", "y"])


def binary_outcome_plot(
    data: pd.DataFrame,
    x_var: str = "x",
    y: str = "y",
    # ax: plt.Axes | None = None,
    fig: mpl.figure.Figure | None = None,
) -> mpl.figure.Figure:
    """
    Create plot of continuous var by binary outcome.

    This is just pulled straight from a notebook so is pretty loose. Could improve the typing of
    this function, as well as it's name, and the use of mpl objects within it.
    """
    # if ax is None:
    fig, ax = plt.subplots(figsize=(20, 3))

    colors = {
        0: metadata.color.PINK_COLOUR,
        # 1: "green",
        1: metadata.color.DEEPER_GREEN,
    }
    for g, dfg in data.groupby([y]):
        ax.scatter(
            x=dfg[x_var],
            y=dfg[y],
            color=colors[g],
        )

        med = dfg[x_var].median()
        ax.scatter(
            x=med,
            y=g,
            s=90,
            color=colors[g],
        )
        ax.vlines(
            x=med,
            ymin=min(g, 0.5),
            ymax=max(g, 0.5),
            color=colors[g],
        )

        ax.text(
            x=med + 0.5,
            y=abs(g - 0.15),
            s=f"Median {g} : {round(med,2)}",
            fontsize=15,
        )
    ax.set_title(
        f"{x_var} x {y}",
        fontsize=20,
    )
    ax.grid(alpha=0.2)

    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


def main() -> mpl.figure.Figure:
    """Plot."""

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig = binary_outcome_plot(data=make_data())
        fig.set_tight_layout(True)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit()
