# pylint: disable=duplicate-code
"""
Distributions of multiple variables.

For a set of variables, each with an accompanying continuous variable on the same scale,
plot the distributions of the continuous variable. Might be useful to have a kde
overlaid here.

Example of:

- fixed formatting
- setting categorical ticks at particular positions.

"""
from __future__ import annotations

import itertools
import pathlib
import re
import textwrap
from collections.abc import Mapping
from typing import Any, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata


def sample_data(n_categories: int = 12) -> tuple[pd.DataFrame, dict[int, str]]:
    """Generate sample data."""
    # random stuff from postgres website.
    document = (
        "\n"
        "PostgreSQL is an object-relational database management system (ORDBMS) based "
        "on POSTGRES, Version 4.2, developed at the University of California at "
        "Berkeley Computer Science Department. POSTGRES pioneered many concepts that "
        "only became available in some commercial database systems much later.\n"
        "\n"
        "PostgreSQL is an open-source descendant of this original Berkeley code. It "
        "supports a large part of the SQL standard and offers many modern features:\n"
        "\n"
        "complex queries\n"
        "foreign keys\n"
        "triggers\n"
        "updatable views\n"
        "transactional integrity\n"
        "multiversion concurrency control\n"
        "Also, PostgreSQL can be extended by the user in many ways, for example by "
        "adding new\n"
    )
    words = [x for x in re.sub(r"\n|\(|\)", " ", document, flags=re.M).split(" ") if x]

    def rand_string() -> str:
        """
        random string to represent labelling.
        """
        return " ".join(
            np.random.choice(words, size=np.random.randint(3, 15, size=1)),
        ).capitalize()

    def rand_cont() -> npt.NDArray[np.float64]:
        # Generates a random bimodal distribution so that it looks roughly similar to
        # what we might see from timing data or whatever.
        loc_min = 2
        loc_max = 7
        mode_1_loc = np.random.randint(loc_min, loc_max, size=1)
        size = np.random.randint(10, 250, size=1)
        mode_1 = np.random.normal(
            loc=mode_1_loc,
            scale=2,
            size=size,
        )
        # product
        direction = 1
        if mode_1_loc > loc_max / (loc_max + loc_min):
            direction = -1

        mode_2_loc = int(mode_1_loc + direction * mode_1_loc * 0.5)
        mode_2_size = int(size * 0.4)
        mode_2 = np.random.normal(loc=mode_2_loc, scale=2, size=mode_2_size)

        ret = cast(
            npt.NDArray[np.float64],
            np.clip(np.concatenate([mode_1, mode_2]), a_min=0, a_max=np.inf),
        )
        return ret

    data_dict: dict[str, list[float]] = {"cat": [], "cont": []}

    for category in range(1, n_categories + 1):
        conts = rand_cont()
        data_dict["cont"] = data_dict["cont"] + list(conts)
        data_dict["cat"].extend(list(np.repeat(category, len(conts))))

    data = pd.DataFrame(data_dict)
    labels = {x: rand_string() for x in data["cat"].unique()}

    return data, labels


def categorical_scatters(
    *,
    ax: plt.Axes,
    data: pd.DataFrame,
    cont_var: str,
    cat_var: str,
    labels: Mapping[Any, str],
    # Used if there are particular colours for particular categories, if they're all
    # meant to be the same color then just pass in with the same value for each category
    # - they should all still be represented though.
    color_map: Mapping[Any, str] | None = None,
) -> plt.Axes:
    """Create plot."""
    y_val = 0

    # Can use this to get alternating colours, i did then went off it.
    colors = itertools.cycle(
        [metadata.color.PINK_COLOUR, metadata.color.PINK_COLOUR],
    )

    y_ticks = []

    for g, dfg in data.groupby([cat_var]):
        if len(g) == 1:
            g = g[0]
        y_val += 1
        color = next(colors)
        color = color_map[g] if color_map else color

        y_values = np.repeat([y_val], len(dfg)) + np.random.normal(
            loc=0,
            scale=0.05,
            size=len(dfg),
        )
        x_values = dfg.loc[dfg[cont_var].ne(88888), cont_var]
        ax.scatter(
            x=x_values,
            y=y_values,
            color=color,
            # alpha=0.1,
            alpha=0.3,
        )

        y_ticks.append((g, labels[g]))

    ax.grid(alpha=0.1)

    ax.yaxis.set_major_locator(
        mpl.ticker.FixedLocator([y_tick[0] for y_tick in y_ticks]),
    )
    ax.yaxis.set_major_formatter(
        mpl.ticker.FixedFormatter(
            ["\n".join(textwrap.wrap(y_tick[1], width=30)) for y_tick in y_ticks],
        ),
    )

    return ax


def main() -> mpl.figure.Figure:
    """Main."""
    data, labels = sample_data()

    cat_var = "cat"
    cont_var = "cont"

    # color
    color_map = {x: metadata.color.PINK_COLOUR for x in labels}
    # Maybe we want to highlight a particular value or whatever idk.
    color_map[3] = metadata.color.DEEPER_GREEN

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, ax = plt.subplots(
            # figsize=(7, 7),
            figsize=(20, 20),
            ncols=1,
            nrows=1,
            sharey=True,
            constrained_layout=False,
        )
        ax = categorical_scatters(
            data=data,
            cont_var=cont_var,
            cat_var=cat_var,
            labels=labels,
            ax=ax,
            color_map=color_map,
        )

        ax.set_title(
            "Scatter plot with categorical labels",
            fontsize=20,
        )

    # axis styling
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    fig.set_tight_layout(True)
    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit()
