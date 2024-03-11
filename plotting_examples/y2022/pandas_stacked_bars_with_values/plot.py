# pylint: disable=duplicate-code
"""
Horizontal stacked bars, based off of pandas.

Could do these from scratch - pandas makes things a bit more straightforward though.

Example of:

- fixed formatting - setting categorical ticks at particular positions.
"""

from __future__ import annotations

import io
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def sample_data() -> tuple[pd.DataFrame, dict[int, dict[str, str]]]:
    """Generate sample data."""
    csv = """\
    Column A,Column B,Column C,Column D
    22.9,21.4,26.6,27.1
    40.0,28.9,38.1,40.9
    20.9,22.0,18.7,15.3
    10.5,18.9,8.5,8.4
    5.7,8.8,8.1,8.3
    """
    df_plot: pd.DataFrame = pd.read_csv(io.StringIO(csv))
    index_labels = {
        0: "Something",
        1: "Another",
        2: "This Thing",
        3: "Thai Food",
        4: "Finally",
    }
    index_colours = {
        0: metadata.color.TAN,
        1: metadata.color.DEEPER_GREEN,
        2: metadata.color.PINK_COLOUR,
        3: metadata.color.BLUE,
        4: metadata.color.PURPLEY,
    }

    plot_metadata = {}
    for x in index_labels:
        plot_metadata[x] = {
            "colour": index_colours[x],
            "label": index_labels[x],
        }

    # Plot metadata has this form:
    # >>> {
    # >>>     0: {"colour": "red", "label": "Something"},
    # >>>     1: {"colour": "grey", "label": "Another"},
    # >>>     2: {"colour": "pink", "label": "This Thing"},
    # >>>     3: {"colour": "blue", "label": "Thai Food"},
    # >>>     4: {"colour": "green", "label": "Finally"},
    # >>> }

    return df_plot, plot_metadata


def main() -> mpl.figure.Figure:
    """Main."""
    df_plot, plot_metadata = sample_data()

    # Reverse columns as want to plot A as first bar.
    df_plot = df_plot.loc[:, df_plot.columns[::-1]]

    # If you want to rename the axis y-labels it's easiest to just rename them in the
    # dataframe columns.

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

        df_plot.T.plot.barh(
            stacked=True,
            ax=ax,
            color=[value["colour"] for value in plot_metadata.values()],
        )

        handles = [
            Line2D(
                [0],
                [0],
                color=value["colour"],
                label=value["label"],
                markersize=12,
                linewidth=7,
            )
            for value in plot_metadata.values()
        ]

        ax.legend(
            handles=handles,
            frameon=False,
            ncol=1,
            bbox_to_anchor=(1.01, 0.7),
            fontsize=12,
        )

        ax.set_title("This Is A Title", fontsize=20, y=1.05)
        ax.set_xlabel("%", fontsize=15)
        ax.grid(linewidth=0.2)
        ax.set_axisbelow(True)

        # Iterate over the data values, and patches of the axis, and plot the data
        # value over the relevant patch.
        data_matrix = df_plot.to_numpy().flatten()

        min_bar_size = 3
        for i, patch in enumerate(ax.patches):
            width = patch.get_width()
            height = patch.get_height()
            x, y = patch.get_xy()
            data_i = data_matrix[i] if data_matrix[i] >= min_bar_size else "-"
            ax.annotate(
                f"{data_i}",
                (x + width * 0.5, y + height * 0.5),
                ha="center",
                va="center",
                fontsize=12,
            )

        _ = [ax.spines[x].set_visible(False) for x in ax.spines]

        loc = mpl.ticker.MultipleLocator(base=5.0)
        ax.set_xlim(0, 100)
        ax.xaxis.set_major_locator(loc)

    fig.set_tight_layout(True)  # type: ignore[attr-defined]
    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))

    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
