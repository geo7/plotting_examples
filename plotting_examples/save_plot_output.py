"""Util for saving output from plots."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from plotting_examples.extract_year_name import extract_year_name_from_plot_py

if TYPE_CHECKING:
    import matplotlib as mpl


def save_plot(
    *,
    fig: mpl.figure.Figure,
    file: str,
    dpi: int = 150,
) -> None:
    """Util for saving plot to images dir."""
    year, name = extract_year_name_from_plot_py(file=file)

    year_dir = Path("./images") / year
    # If the dir doesn't exist we need to make it...
    if not year_dir.exists():
        year_dir.mkdir(exist_ok=False, parents=False)

    png_pth = year_dir / (name + ".png")
    fig.savefig(png_pth, dpi=dpi)
