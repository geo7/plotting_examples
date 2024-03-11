# pylint: disable=duplicate-code
"""
Hex map for the UK constituencies.

Some meaningless generated data - small multiples with hex maps can be useful sometimes
though. Could be good to add in the geographically accurate version as well.
"""

from __future__ import annotations

import pathlib

import geopandas
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

random_choice = np.random.Generator(np.random.MT19937(1)).choice


def main() -> mpl.figure.Figure:
    """Main."""
    election_data = (
        pathlib.Path(__file__).parent
        / "data/gb_hex_cartogram/GB_Hex_Cartogram_Const.shp"
    )
    gdf = geopandas.read_file(election_data)

    # Set up color maps by party
    partycolors = {
        "A": metadata.color.DEEPER_GREEN,
        "B": metadata.color.PINK_COLOUR,
        "C": metadata.color.TAN,
    }

    parties = ["A", "B", "C"]
    pcols = {c: partycolors[c] for c in parties}
    colors = [pcols[k] for k in sorted(pcols.keys())]
    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, axes = plt.subplots(
            nrows=1,
            ncols=3,
            figsize=(15, 5),
        )

        font_size = 15
        edgecolor = "black"
        edge_width = 0.5

        ax = axes[0]
        gdf["Party"] = list(
            random_choice(
                parties,
                size=len(gdf),
                replace=True,
                p=[0.4, 0.3, 0.3],
            ),
        )
        gdf.plot(
            ax=ax,
            column="Party",
            cmap=ListedColormap(colors),
            edgecolor=edgecolor,
            linewidth=edge_width,
        )
        _ = ax.axis("off")
        _ = ax.set_title("Current", fontsize=font_size, loc="left")

        ax = axes[1]
        gdf["Party"] = list(
            random_choice(
                parties,
                size=len(gdf),
                replace=True,
                p=[0.3, 0.6, 0.1],
            ),
        )
        gdf.plot(
            ax=ax,
            column="Party",
            cmap=ListedColormap(colors),
            edgecolor=edgecolor,
            linewidth=edge_width,
        )
        _ = ax.axis("off")
        _ = ax.set_title("Scenario A", fontsize=font_size, loc="left")

        ax = axes[2]
        gdf["Party"] = list(
            random_choice(
                parties,
                size=len(gdf),
                replace=True,
                p=[0.1, 0.8, 0.1],
            ),
        )
        gdf.plot(
            ax=ax,
            column="Party",
            cmap=ListedColormap(colors),
            edgecolor=edgecolor,
            linewidth=edge_width,
        )
        _ = ax.axis("off")
        _ = ax.set_title("Scenario B", fontsize=font_size, loc="left")

        # Create legend.
        custom_lines = [
            mpl.lines.Line2D([0], [0], color=x, lw=6) for x in partycolors.values()
        ]
        ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
        ax.legend(
            custom_lines,
            list(partycolors.keys()),
            loc=(0.7, 0.7),
            fontsize=12,
            frameon=False,
            borderpad=2,
        )

        # The dataframe seems to assign items to categories based on the selected column
        # sort order We can define a color map with a similar sorting
        colors = [partycolors[k] for k in sorted(partycolors.keys())]

    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    fig.set_tight_layout(True)  # type: ignore[attr-defined]
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
