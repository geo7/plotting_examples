# pylint: disable=duplicate-code
"""
Layout containing two bar plots and a bivariate plot between them.

In this case it's a silly example of some data containing the social grade of
Labradors, as well as the education group. The main plot is a stacked bar containing
the breakdown of education group for each social grade.

Don't think I'm too keen on the code for this plot - though it's not always so clear
(to me) how to make "nice" code with a lot of matplotlib stuff.

Obviously, the data is made up.
"""
from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from plotting_examples import dvc_entry, save_plot_output
from plotting_examples.y2022 import metadata

# Fontsize for the main title and subtitle
FONTSIZE_TITLE = 30
FONTSIZE_SUBTITLE = 20
# Fontsize for the numbers displayed on bars.
FONTSIZE_PLT_TXT = 10

# What colour to outline the edges of bars with - if None then there's no outline
# created.
BAR_EDGECOLOR: str | None = None
# What level of rounding to apply to percentages displayed on bars.
ROUNDING_PCTS = 1

# Dependent var
VAR_DEPENDENT = "dependent_var"
# Independent var
VAR_INDEPENDENT = "independent_var"
# Text for the main title - the subtitle is generated from the metadata atm.
TEXT_TITLE = "Labradors\neducation ~ social grade"
# Image to display in teh top left.
IMAGE_PATH = (
    "./plotting_examples/y2022/stacked_bar_with_single_bars_layout/data/lab.png"
)

COLORS = [
    metadata.color.PINK_COLOUR,
    metadata.color.DEEPER_GREEN,
    metadata.color.BROWNY_RED,
]
COLOR_SUBTITLE_TEXT = "#808080"

# subplot_mosaic layout definition.
LAYOUT = [
    ["top_left_corner", "title", "title", "title", "top_right_corner"],
    ["main", "main", "main", "main", "side"],
    ["main", "main", "main", "main", "side"],
    ["bottom", "bottom", "bottom", "bottom", "bottom_right_corner"],
]

# Colors which are used when the bar colour is dark/light respectively - so that the
# text is readable (not dark font on dark bars etd).
COLOR_FONT_LIGHT = "#000000"
COLOR_FONT_DARK = "#ffffff"


def get_sample_data() -> (
    tuple[
        pd.DataFrame,
        dict[str, dict[float, str]],
        dict[str, str],
    ]
):
    """
    Generate sample data.

    Data structured similar to what you'd find in an SPSS sav file - where there's the
    df (responses), cnl (metadata about the columns) and vvl (metadata about the values
    within the columns)
    """
    rng = np.random.default_rng(1)
    # Create dataframe with different distributions for each of the independent
    # variable levels.
    df = (
        pd.concat(
            [
                pd.DataFrame(
                    {
                        VAR_DEPENDENT: rng.choice(
                            [1, 2, 3],
                            size=330,
                            p=(0.87, 0.1, 0.03),
                        ),
                        VAR_INDEPENDENT: 5,
                    },
                ),
                pd.DataFrame(
                    {
                        VAR_DEPENDENT: rng.choice(
                            [1, 2, 3],
                            size=410,
                            p=(0.44, 0.54, 0.02),
                        ),
                        VAR_INDEPENDENT: 4,
                    },
                ),
                pd.DataFrame(
                    {
                        VAR_DEPENDENT: rng.choice(
                            [1, 2, 3],
                            size=510,
                            p=(0.26, 0.61, 0.13),
                        ),
                        VAR_INDEPENDENT: 3,
                    },
                ),
                pd.DataFrame(
                    {
                        VAR_DEPENDENT: rng.choice(
                            [1, 2, 3],
                            size=800,
                            p=(0.105, 0.565, 0.33),
                        ),
                        VAR_INDEPENDENT: 2,
                    },
                ),
                pd.DataFrame(
                    {
                        VAR_DEPENDENT: rng.choice(
                            [1, 2, 3],
                            size=950,
                            p=(0.08, 0.33, 0.59),
                        ),
                        VAR_INDEPENDENT: 1,
                    },
                ),
            ],
        )
        .assign(weight=1)
        .reset_index(drop=True)
    )
    vvl = {
        VAR_INDEPENDENT: {
            1.0: "Upper management",
            2.0: "Lower Management",
            3.0: "Intermediate",
            4.0: "Routine",
            5.0: "Never worked",
        },
        VAR_DEPENDENT: {
            1.0: "Low",
            2.0: "Medium",
            3.0: "High",
        },
    }
    cnl = {
        VAR_INDEPENDENT: "Social Grade",
        VAR_DEPENDENT: "Education Level",
    }

    return df, vvl, cnl


def patch_color_light(patch: mpl.patches.Rectangle) -> bool:
    """Determine if mpl patch is light or dark."""
    # TODO: Put this into a global helper module.
    bar_col = mpl.colors.to_hex(patch.get_facecolor())
    hex_col = bar_col[1:]
    red, green, blue = (
        int(hex_col[0:2], 16),
        int(hex_col[2:4], 16),
        int(hex_col[4:6], 16),
    )
    # https://stackoverflow.com/questions/3942878/how-to-decide-
    # font-color-in-white-or-black-depending-on-background-color
    threshold = 100
    if (red * 0.299 + green * 0.587 + blue * 0.114) > threshold:
        return True
    return False


class PlotSections:

    """
    Holds plotting sections.

    Just using this for namespacing really! Which was triggered by pylint complaining,
    which probably isn't a good reason... Might usually just put this in a module but
    wanted all the code in plot.py

    Considered adding the df, vvl, cnl to the class in an __init__ or whatever but left
    it as-is.
    """

    # rename to bivariate.
    @staticmethod
    def main(
        ax: plt.Axes,
        df: pd.DataFrame,
        vvl: dict[str, dict[float, str]],
        # cnl: dict[str, str],
    ) -> None:
        # pylint: disable=too-many-locals
        """Plot the stacked bars."""
        df_plot = (
            pd.crosstab(
                df[VAR_DEPENDENT],
                df[VAR_INDEPENDENT].replace(vvl[VAR_INDEPENDENT]),
                normalize="columns",
            )
            .mul(100)
            .round(1)
            .loc[:, list(vvl[VAR_INDEPENDENT].values())]
        )
        df_plot_counts = pd.crosstab(
            df[VAR_DEPENDENT],
            df[VAR_INDEPENDENT],
        )
        df_plot.T.plot.barh(
            stacked=True,
            ax=ax,
            color=COLORS,
            edgecolor=BAR_EDGECOLOR,
        )

        ax.grid(linestyle=":", alpha=0.3)

        # The legend _should_ be self explanatory from the context of the plot.
        ax.get_legend().remove()

        # Not interested in seeing the col name on the y axis for the main plot
        ax.set_ylabel("")

        data_matrix = df_plot.to_numpy().flatten()
        data_matrix_counts = df_plot_counts.to_numpy().flatten()
        min_bar_size = 3
        for i, patch in enumerate(ax.patches):
            width = patch.get_width()
            height = patch.get_height()
            x, y = patch.get_xy()
            data_i = data_matrix[i] if data_matrix[i] >= min_bar_size else "-"
            data_count_i = (
                data_matrix_counts[i] if data_matrix[i] >= min_bar_size else None
            )

            ann = f"{data_i} ({data_count_i})" if data_count_i is not None else "-"

            text_col = COLOR_FONT_LIGHT if patch_color_light(patch) else COLOR_FONT_DARK

            ax.annotate(
                f"{ann}",
                (x + width * 0.5, y + height * 0.5),
                ha="center",
                va="center",
                fontsize=10,
                zorder=12,
                color=text_col,
            )

        ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=5))
        ax.set_xlabel("%", fontsize=10)
        ax.set_xlim(0, 100)

        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)

    @staticmethod
    def side_marginal(
        ax: plt.Axes,
        df: pd.DataFrame,
        vvl: dict[str, dict[float, str]],
        cnl: dict[str, str],
    ) -> None:
        """Bar plot of the independent var."""
        counts = df[VAR_INDEPENDENT].replace(vvl[VAR_INDEPENDENT]).value_counts()

        ax.barh(
            counts.index,
            counts,
            color=metadata.color.TAN,
            edgecolor=BAR_EDGECOLOR,
            height=0.5,
        )
        ax.grid(alpha=0.2, linestyle=":")
        ax.set_title(cnl[VAR_INDEPENDENT], loc="left")

        counts_list = list(counts)

        for count, patch in zip(counts, ax.patches):
            count_pct = round((count / sum(counts_list)) * 100, ROUNDING_PCTS)
            width = patch.get_width()
            height = patch.get_height()
            x, y = patch.get_xy()
            txt_color = "#000000" if patch_color_light(patch) else "#ffffff"
            ax.text(
                s=f"{count_pct}%\n({count})",
                x=x + width * 0.5,
                y=y + height * 0.5,
                va="center",
                ha="center",
                color=txt_color,
                fontsize=FONTSIZE_PLT_TXT,
            )

        ax.set_xticks([])
        ax.set_yticks([])

        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        ax.spines.bottom.set_visible(False)
        ax.spines.left.set_visible(False)

    @staticmethod
    def bottom_marginal(
        ax: plt.Axes,
        df: pd.DataFrame,
        vvl: dict[str, dict[float, str]],
        cnl: dict[str, str],
    ) -> None:
        """Bar plot of the dependent variable."""
        counts = df[VAR_DEPENDENT].value_counts().sort_index()
        ax.bar(
            x=list(vvl[VAR_DEPENDENT].values()),
            height=counts,
            color=COLORS,
            edgecolor=BAR_EDGECOLOR,
        )
        ax.set_title(cnl[VAR_DEPENDENT])
        ax.set_yticks([])

        counts_list = list(counts)
        for count, patch in zip(counts, ax.patches):
            count_pct = round((count / sum(counts_list)) * 100, 2)
            width = patch.get_width()
            height = patch.get_height()
            x, y = patch.get_xy()
            if patch_color_light(patch):
                txt_color = COLOR_FONT_LIGHT
            else:
                txt_color = COLOR_FONT_DARK
            ax.text(
                s=f"{count_pct}\n({count})",
                x=x + width * 0.5,
                y=y + height * 0.5,
                va="center",
                ha="center",
                color=txt_color,
                fontsize=FONTSIZE_PLT_TXT,
            )

        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
        ax.spines.left.set_visible(False)

    @staticmethod
    def title(ax: plt.Axes, cnl: dict[str, str]) -> None:
        """Overall title."""
        ax.text(
            s="Labradors",
            x=0.1,
            y=0.5,
            fontsize=FONTSIZE_TITLE,
            horizontalalignment="left",
            verticalalignment="bottom",
        )

        # Just using this to nudge the text placement around...
        diff = 0.3
        ax.text(
            # Assuming that the metadata is reasonably nice for this.
            s=f"{cnl[VAR_DEPENDENT]} ~ {cnl[VAR_INDEPENDENT]}",
            x=0.1,
            y=0.5 - diff,
            fontsize=FONTSIZE_SUBTITLE,
            horizontalalignment="left",
            verticalalignment="bottom",
            color=COLOR_SUBTITLE_TEXT,
        )

        ax.axis("off")

    @staticmethod
    def top_left_corner(ax: plt.Axes) -> None:
        """Plot logo."""
        img_path = IMAGE_PATH
        club_icon = Image.open(img_path)
        ax.imshow(club_icon)
        ax.axis("off")

    @staticmethod
    def top_right_corner(ax: plt.Axes) -> None:
        """Just leaving this empty for now."""
        ax.axis("off")

    @staticmethod
    def bottom_right_corner(ax: plt.Axes, df: pd.DataFrame) -> None:
        """Some random information like data source etc."""
        ax.text(
            s=(
                #
                "2022 Labrador educational \ndata and social grades"
                "\n"
                "\n"
                f"Sample size : {df.shape[0]}"
                "\n"
                "\n"
                "source: somedogdata.com"
            ),
            x=0,
            y=0.5,
            fontsize=FONTSIZE_PLT_TXT,
            va="center",
            ha="left",
            color=COLOR_SUBTITLE_TEXT,
        )
        ax.axis("off")

    @staticmethod
    def footnote(ax: plt.Axes) -> None:
        """
        Plot footnote.

        Didn't bother using this in the end.
        """
        ax.text(
            s=(
                #
                "Some text about the data, Labradors, whatever."
            ),
            x=0,
            y=1,
            fontsize=10,
            style="italic",
            va="top",
            ha="left",
            color=COLOR_SUBTITLE_TEXT,
        )
        ax.set_xticks([])
        ax.set_yticks([])


def main() -> mpl.figure.Figure:
    """Main."""
    df, vvl, cnl = get_sample_data()

    plot_sections = PlotSections()

    with plt.rc_context(
        {
            "xtick.major.pad": 10,
            "font.family": "monospace",
        },
    ):
        fig = plt.figure(
            figsize=(15, 10),
        )
        ax_dict = fig.subplot_mosaic(LAYOUT)

        plot_sections.title(ax=ax_dict["title"], cnl=cnl)
        plot_sections.bottom_marginal(
            ax=ax_dict["bottom"],
            df=df,
            cnl=cnl,
            vvl=vvl,
        )
        plot_sections.main(
            ax=ax_dict["main"],
            df=df,
            vvl=vvl,
        )
        plot_sections.side_marginal(ax=ax_dict["side"], df=df, vvl=vvl, cnl=cnl)
        plot_sections.top_left_corner(ax=ax_dict["top_left_corner"])
        plot_sections.top_right_corner(ax=ax_dict["top_right_corner"])
        plot_sections.bottom_right_corner(
            ax=ax_dict["bottom_right_corner"],
            df=df,
        )

        fig.tight_layout()

    # Set background colours.
    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    for ax_name in ax_dict:
        ax_dict[ax_name].set_facecolor(metadata.color.BACKGROUND_COLOUR)

    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
