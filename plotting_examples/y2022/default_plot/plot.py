# pylint: disable=duplicate-code
"""Default for plotting example - just to base others off."""
from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def get_sample_data() -> pd.DataFrame:
    """Sample data."""
    return pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [1, 2, 2, 3, 8],
        },
    )


def main() -> mpl.figure.Figure:
    """Main."""
    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, ax = plt.subplots(
            figsize=(10, 10),
        )
        df = get_sample_data()

        ax.scatter(x=df["x"], y=df["y"])
        ax.set_title("Default plotting.")

        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
        ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
