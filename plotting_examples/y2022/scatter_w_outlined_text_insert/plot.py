# pylint: disable=duplicate-code
"""
Scatter plot with text inserted to scatter points.

Data was taken from a tidy tuesday.

Example of:

- Outlining text elements in a plot.
"""
from __future__ import annotations

import pathlib
from typing import TypeVar

import matplotlib as mpl
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

T = TypeVar("T")


def get_plotting_data() -> pd.DataFrame:
    """Plotting dataframe."""
    # df = dl_data()
    df = pd.read_parquet(pathlib.Path(__file__).parent / "data.parquet")

    data_list = []
    for g, dfg in df.groupby(["year"]):
        x = dfg["distributor"]
        df_a = (
            x.value_counts()
            .reset_index()
            .rename(columns={"distributor": "count", "index": "distributor"})
        )
        df_b = (
            x.value_counts(normalize=True)
            .reset_index()
            .rename(
                columns={"distributor": "percentage", "index": "distributor"},
            )
            .assign(
                percentage=lambda x: x["percentage"].mul(100).round(1),
                year=g,
            )
        )
        df_c = pd.merge(df_a, df_b, on="distributor")
        df_c = df_c.sort_values("count", ascending=False)
        top = ["#ff2309"]
        other_colour = "#d0d0d0"
        n_size = 1
        if len(df_c) > n_size:
            df_c["colour"] = top + [
                other_colour for _ in range(len(df_c) - n_size)
            ]
        else:
            df_c["colour"] = top
        assert not df_c["colour"].isna().any()
        data_list.append(df_c)

    plotting_data = pd.concat(data_list)
    plotting_data["year"] = pd.to_datetime(plotting_data["year"], format="%Y")

    return plotting_data


def main() -> mpl.figure.Figure:
    """Main."""
    plotting_data = get_plotting_data()

    year_counts = (
        plotting_data.groupby("year").size().rename("year_counts").reset_index()
    )

    # want to know how many there were each year.
    plotting_data = pd.merge(plotting_data, year_counts, on="year")

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig, ax = plt.subplots(figsize=(40, 15))

        other_colour = "#d0d0d0"
        # BACKGROUND_COLOUR = "#f2f2f2"

        for _, dfg in plotting_data.groupby("distributor"):
            # plot text of distributor.
            for _, row in dfg.iterrows():
                if row["colour"] == other_colour:
                    ax.scatter(
                        x=row["year"],
                        y=row["percentage"],
                        alpha=0.2,
                        s=300,
                        color=metadata.color.PINK_COLOUR,
                        zorder=1,
                    )
                else:
                    ax.scatter(
                        x=row["year"],
                        y=row["percentage"],
                        alpha=1,
                        s=800,
                        color=metadata.color.PINK_COLOUR,
                        zorder=2,
                    )
                    ax.text(
                        x=row["year"],
                        y=row["percentage"],
                        s=row["distributor"],
                        horizontalalignment="center",
                        verticalalignment="center",
                        color="black",
                        size=14,
                        path_effects=[
                            pe.withStroke(
                                linewidth=4,
                                foreground=metadata.color.PINK_COLOUR,
                            ),
                        ],
                    )

        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_title("Top film distributor, 1957 - 2021", fontsize=35, y=1.05)

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(15)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(15)

        # ax.set_facecolor(
        #     BACKGROUND_COLOUR,
        # )
        # fig.patch.set_facecolor(BACKGROUND_COLOUR)

        ax.tick_params(axis="both", which="both", length=0)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        ax.grid(alpha=0.15, axis="y", zorder=0)
        # ax.grid(alpha=0.1, axis="x", zorder=0)

        years = YearLocator(5)  # every year
        years_fmt = DateFormatter("%Y")
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)

        fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
        ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit()
