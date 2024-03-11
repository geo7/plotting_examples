# pylint: disable=duplicate-code
"""
Bar chart style copied from Opinium.

Saw this on twitter (i think) and thought I'd recreate it in mpl.
"""

from __future__ import annotations

import pathlib

import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

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
        data = {
            "Trump": -63,
            "Johnson": -11,
            "O'Neill": 3,
            "Foster": 9,
            "Khan": 16,
            "Starmer": 18,
            "Sturgeon": 34,
            "Drakeford": 34,
        }

        fig, ax = plt.subplots(figsize=(15, 7))

        # trying to setup as many variables as possible here - though there are still
        # some magic values

        min(list(data.values()))
        max_val = max(list(data.values()))

        line_width = 20
        start_offset = line_width * 0.08
        percentage_label_shift = 3
        positive_bar_color = metadata.color.DEEPER_GREEN
        negative_bar_color = metadata.color.PINK_COLOUR
        font_size = 12
        source_fontsize = 8
        footnote_location = (0, -0.3)

        # Johnson here is the value which is used as it's not the most negative, but is
        # negative. Really, this is just what kinda looked ok, with different data
        # there would likely have to be pretty different approaches to all of this i
        # think
        grey_bar_left_x = data["Johnson"]

        # shading every other bar a bit
        for bar_i, (name, y_val_) in enumerate(zip(data, range(8))):
            y_val = y_val_ * 2
            x_val = data[name]
            x_loc = 20
            direction = 1
            left_adjust = 0
            if x_val > 0:
                left_adjust = 9
                direction *= -1
                bar_color = positive_bar_color
                sign = "+"
                sign_align = "left"
            else:
                left_adjust = -15
                bar_color = negative_bar_color
                sign = ""
                sign_align = "right"

            ax.plot(
                [start_offset * -direction, data[name]],
                [y_val, y_val],
                linewidth=line_width,
                c=bar_color,
            )
            ax.text(
                x=(x_loc * direction) + left_adjust,
                y=y_val,
                s=name,
                horizontalalignment="left",
                verticalalignment="center",
                fontsize=font_size,
            )
            ax.text(
                x=data[name] + -direction * percentage_label_shift,
                y=y_val,
                s=f"{sign}{data[name]}",
                verticalalignment="center",
                horizontalalignment=sign_align,
                fontsize=font_size,
            )

            if bar_i % 2 == 1:
                ax.plot(
                    [grey_bar_left_x, max_val + 20],
                    [y_val, y_val],
                    linewidth=line_width,
                    c="#a0a0a0",
                    alpha=0.07,
                    zorder=0,
                )

        _ = [ax.spines[s].set_visible(False) for s in ax.spines]
        _ = ax.xaxis.set_ticklabels([])
        _ = ax.yaxis.set_ticklabels([])
        _ = ax.tick_params(axis="both", length=0)

        title_y = 1.2
        title_x = 0.45

        # Title
        ax.text(
            x=title_x,
            y=title_y,
            s="Level of Trust in information \nprovided on Coronavirus",
            transform=ax.transAxes,
            fontsize=20,
            horizontalalignment="left",
        )

        # subtitle
        _ = ax.text(
            x=title_x,
            y=title_y - 0.11,
            s=(
                "Net Level of Trust in providing of information by party leaders\non"
                " Coronavirus"
            ),
            transform=ax.transAxes,
            c="#717171",
        )

        # add rectangle
        rect = mpl.patches.Rectangle(
            (title_x - 0.015, title_y - 0.11),
            width=0.01,
            height=0.25,
            color=positive_bar_color,
            transform=ax.transAxes,
            clip_on=False,
        )
        ax.add_patch(rect)

        # source of data
        _ = ax.text(
            x=footnote_location[0],
            y=footnote_location[1],
            s=(
                "https://www.opinium.com/wp-content/uploads/2020/06/"
                "VI-26-06-2020-Observer-Data-Tables.xlsx"
            ),
            transform=ax.transAxes,
            fontsize=source_fontsize,
        )

        # add company logo to plot
        image = mpimg.imread(
            pathlib.Path(__file__).parent / "opinium.png",
            format="png",
        )
        img_y = ax.bbox.ymin

        ax.text(
            x=ax.bbox.xmax + 400,
            y=img_y + 20,
            s="* Sample size: 2001\n25-26th June\nOpinium.co.uk",
            transform=None,
            verticalalignment="top",
        )

        fig.figimage(
            image,
            ax.bbox.xmax + 659,
            0,
            origin="upper",
        )
        ax.axvline(0, linewidth=0.1, alpha=0.9, color="#212121")

    fig.patch.set_facecolor(metadata.color.BACKGROUND_COLOUR)
    ax.set_facecolor(metadata.color.BACKGROUND_COLOUR)

    return fig


if __name__ == "__main__":
    dvc_entry.add_to_dvc(path=pathlib.Path(__file__))
    save_plot_output.save_plot(fig=main(), file=__file__)
    raise SystemExit
