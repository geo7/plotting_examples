# pylint: disable=duplicate-code
"""
Some random points.

No real meaning to this - was messing about with some bokeh style bits (the effect, not
the python library), so dumping here. Not sure I'm mad on the output - it's also slow
as hell.
"""

from __future__ import annotations

import itertools
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

np_rnd = np.random.Generator(np.random.MT19937())


def main() -> mpl.figure.Figure:
    """Main."""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor("black")

    def make_point(
        *,
        x: float,
        y: float,
        con_min: int = 10,
        con_max: int = 10_000,
        num_cont: int = 20,
        alpha_mult: float = 0.2,
        color: str = "black",
    ) -> None:
        concentric = np.flip(np.linspace(con_min, con_max, num=num_cont))
        alphas = np.flip(concentric / con_max) * alpha_mult
        for con, alph in zip(concentric, alphas):
            ax.scatter(
                x=x,
                y=y,
                color=color,
                s=con,
                alpha=alph,
            )

    colors = itertools.cycle(
        [
            metadata.color.PINK_COLOUR,
            metadata.color.LIGHT_GREEN,
            metadata.color.BLUE,
            metadata.color.DEEPER_GREEN,
        ],
    )

    plot_params = [
        # size, alpha_mult, con_max, num_cont
        (2, 0.3, 8_00, 50),
        (2, 0.35, 2_00, 5),
        (5, 0.05, 5_00, 9),
        (4, 0.15, 5_00, 9),
        (5, 0.1, 2_000, 50),
        (3, 0.1, 3_000, 50),
        (2, 0.1, 6_000, 50),
        (2, 0.09, 5_000, 50),
        (5, 0.008, 15_000, 150),
        (3, 0.08, 2000, 20),
    ]
    rng = np.random.default_rng(2)

    for size, alpha_mult, con_max, num_cont in plot_params:
        xs = rng.random(size=size)
        ys = xs + rng.random(size=size)
        for x, y in zip(xs, ys):
            color = next(colors)
            make_point(
                x=x,
                y=y,
                color=color,
                alpha_mult=alpha_mult,
                con_max=con_max,
                num_cont=num_cont,
            )

    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_yticks([])
    ax.set_yticks([], minor=True)

    fig.tight_layout()

    fig.patch.set_facecolor("black")

    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
