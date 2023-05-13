# pylint: disable=duplicate-code
"""
Edit SNS violin plot.

Simple example of adjusting the output of a sns plot - I don't typically use sns, but
ofc the objects can be accessed/iterated/edited over as with any other mpl axis.

What's here doesn't look good - just an example of changing defaults.
"""
from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def main() -> mpl.figure.Figure:
    """Main."""
    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, axis = plt.subplots(
            figsize=(10, 5),
            constrained_layout=False,
        )
        df = pd.read_parquet(pathlib.Path(__file__).parent / "data.parquet")

        vio = sns.violinplot(
            data=df,
            x="species",
            y="flipper_length_mm",
            scale="count",
            inner="box",
            linewidth=4,
            ax=axis,
            color=metadata.color.PINK_COLOUR,
        )

        vio.grid(alpha=0.2)
        # What size to increase/decreate the central boxplot section to.
        new_width = 30

        # adjust the size of the boxplot - which of these list elements to edit is just
        # guess and check.
        for vio_line in vio.lines[1::2]:
            vio_line.set_linewidth(new_width)

        #  adjust the median point markers within the boxplot.
        for child in vio.get_children()[1:6:2]:
            child.set_linewidth(5)

        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
        vio.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit()
