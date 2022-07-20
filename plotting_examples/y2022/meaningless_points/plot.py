# pylint: disable=duplicate-code
"""
Some random points.

No real meaning to this - was messing about with some bokeh style bits (the effect, not the python
library), so dumping here. Didn't really end up as I'd have liked.
"""
from __future__ import annotations

import pathlib
import itertools

import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def main() -> mpl.figure.Figure:
    """Main."""
    fig, ax = plt.subplots(figsize=(20, 5))
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
        ]
    )

    plot_params = [
        # size, alpha_mult, con_max, num_cont
        #     (2, 0.1, 10_000, 10),
        #     (2, 0.02, 3_500, 50),
        #     (2, 0.02, 4_500, 8),
        (2, 0.3, 8_00, 50),
        #     (3, 0.35, 5_00, 6),
        #     (2, 0.35, 2_00, 6),
        (2, 0.35, 2_00, 2),
        (9, 0.3, 5_00, 2),
        (5, 0.2, 2_000, 50),
        (2, 0.09, 5_000, 50),
        (2, 0.008, 15_000, 150),
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
    raise SystemExit()
