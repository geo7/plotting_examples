# pylint: disable=duplicate-code
"""
Histogram created from scratch using matplotlib.

There are custom bar's created for each bin, instead of using ax.bar, I think it was
originally based on something but i can't find the original / reference now so am just
left with this.

The result is pretty rubbish :)
"""
from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patches, ticker

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def gen_data() -> tuple[pd.DataFrame, dict[str, str]]:
    """
    Generate sample data for plotting.

    Return data as:

    >>>     male  female  row_min  row_max    color  pain_scale
    >>> 0   6.8     0.8      0.8      6.8  #9A7AA0           1
    >>> 1  10.7     1.0      1.0     10.7  #9A7AA0           2
    >>> 2  14.8     4.3      4.3     14.8  #9A7AA0           3
    >>> 3  18.9    10.5     10.5     18.9  #9A7AA0           4
    >>> 4  19.3    14.0     14.0     19.3  #9A7AA0           5
    >>> 5  16.9    19.9     16.9     19.9  #B4EDD2           6
    >>> 6   6.8    16.6      6.8     16.6  #B4EDD2           7
    >>> 7   3.9    16.2      3.9     16.2  #B4EDD2           8
    >>> 8   1.3     9.3      1.3      9.3  #B4EDD2           9
    >>> 9   0.6     7.4      0.6      7.4  #B4EDD2          10

    """
    rng = np.random.default_rng(1)
    n = 1_000
    df = pd.DataFrame(
        {
            "male": np.digitize(
                np.clip(rng.normal(loc=4, scale=2, size=n), 0, 10),
                range(10),
            ),
            "female": np.digitize(
                np.clip(rng.normal(loc=6, scale=2, size=n), 0, 10),
                range(10),
            ),
        },
    )
    # https://coolors.co/b4edd2-a0cfd3-8d94ba-9a7aa0-87677b
    colour_map = {
        "male": metadata.color.PINK_COLOUR,
        "female": metadata.color.LIGHT_GREEN,
    }

    # https://coolors.co/b4edd2-a0cfd3-8d94ba-9a7aa0-87677b
    plot_data = (
        df.apply(lambda x: x.value_counts(normalize=True).mul(100))
        .assign(
            row_min=lambda df: df.apply(lambda dt: min(dt.to_list()), axis=1),
            row_max=lambda df: df.apply(lambda dt: max(dt.to_list()), axis=1),
            # want to use this to determine colours
            color=lambda df: df.idxmax(axis=1).map(colour_map),
            pain_scale=lambda df: df.index,
        )
        .reset_index(drop=True)
    )
    return plot_data, colour_map


def main() -> mpl.figure.Figure:
    """Create plot."""
    plot_data, colour_map = gen_data()

    plt.style.use("./plotting_examples/rc.mplstyle")

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, ax = plt.subplots(figsize=(15, 5))

        # ensure that axis area covers data.
        ax.set_xlim(left=0, right=11)
        ax.set_ylim(
            bottom=0,
            top=plot_data["row_max"].max() + 5,
        )

        def add_bar(
            ax: plt.Axes,  # type: ignore[name-defined]
            x: int,
            y1: float,
            y2: float,
            facecolor: str,
            alpha: float,
            outline: bool,
        ) -> None:
            """Add a bar to the given ax object."""
            width = 1
            rect = patches.Rectangle(
                xy=(x - 0.5 * width, y1),
                width=width,
                height=y2,
                linewidth=1,
                edgecolor="none",
                facecolor=facecolor,
                alpha=alpha,
            )
            ax.add_patch(rect)
            if outline:
                ax.hlines(
                    y=y2,
                    xmin=x - 0.5 * width,
                    xmax=x + 0.5 * width,
                )

        for row in plot_data.itertuples():
            # plot the diffs
            add_bar(
                ax=ax,
                x=row.pain_scale,
                y1=row.row_min,
                y2=(row.row_max - row.row_min),
                facecolor=row.color,
                alpha=0.8,
                outline=False,
            )
            # plot beneath the diffs
            add_bar(
                ax=ax,
                x=row.pain_scale,
                y1=0,
                y2=row.row_min,
                facecolor=metadata.color.GREY,
                alpha=0.2,
                outline=False,
            )

        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        label_fontsize = 15
        ax.set_ylabel("Percentage of respondents", fontsize=label_fontsize)
        ax.set_xlabel(
            "Some scale (1 least, 10 greatest)",
            fontsize=label_fontsize,
        )
        ax.set_title(
            "Reporting of something for male, female respondents",
            fontsize=20,
        )

        legend_elements = [
            patches.Patch(
                facecolor=colour_map["male"],
                edgecolor="none",
                label="male",
            ),
            patches.Patch(
                facecolor=colour_map["female"],
                edgecolor="none",
                label="female",
            ),
        ]
        ax.legend(
            handles=legend_elements,
            frameon=False,
            fontsize=15,
        )

        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d%%"))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
        ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
