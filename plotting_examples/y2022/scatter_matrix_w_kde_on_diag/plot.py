# pylint: disable=duplicate-code
"""
Scatter matrix with kde instead of histogram on the diagonal.

Could probably adapt pd.scatter_matrix instead of doing it from scratch. Though with
this approach the non-diagonal plots could be whatever instead of a scatter plot I
guess...

Would be good to make the upper diagonals differ from the lower diagonals a bit... maybe
some sort of table from pd.cut on the others or whatever.

I'd probably just use subplot_mosaic as well now - that's grown on me a lot since this.
"""

from __future__ import annotations

import itertools
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

np_rnd = np.random.Generator(np.random.MT19937(1977))


def main() -> mpl.figure.Figure:
    """Main."""
    numvars, numdata = 4, 50

    data = 10 * np_rnd.chisquare(df=4, size=(numvars, numdata))

    names = ["mpg", "disp", "drat", "wt"]

    numvars, numdata = data.shape

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, axes = plt.subplots(
            nrows=numvars,
            ncols=numvars,
            figsize=(15, 15),
            constrained_layout=True,
        )

        for ax in axes.flat:
            # Hide all ticks and labels
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)

        # Plot the data.
        for i, j in zip(*np.triu_indices_from(axes, k=1)):
            for x, y in [(i, j), (j, i)]:
                axes[x, y].scatter(
                    data[x],
                    data[y],
                    color=metadata.color.PINK_COLOUR,
                )
                axes[x, y].set_facecolor(metadata.color.BACKGROUND_COLOUR)
                axes[x, y].grid(linestyle=":", alpha=0.2)

        # Label the diagonal subplots...
        for i, label in enumerate(names):
            axes[i, i].annotate(
                label,
                (0.5, 0.5),
                xycoords="axes fraction",
                ha="center",
                va="center",
                fontsize=15,
                fontweight="bold",
            )

        rotate = 45

        for i, j in itertools.product(range(numvars), range(numvars)):
            if i != j:
                axes[i, j].xaxis.set_visible(True)
                for tick in axes[i, j].get_xticklabels():
                    tick.set_rotation(rotate)

        # plot the densities on the diagonal
        for i, j in zip(range(numvars), range(numvars)):
            ax = axes[i, j]
            sns.kdeplot(
                x=data[i],
                ax=ax,
                alpha=0.1,
                fill=True,
                color=metadata.color.PINK_COLOUR,
            )
            ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

        for i, j in zip(range(1, numvars), itertools.cycle([0])):
            axes[i, j].yaxis.set_visible(True)

        _ = fig.suptitle("Example Scatterplots", fontsize=20)
        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
