"""Get year, name from path to plotting file."""

from __future__ import annotations

from pathlib import Path


def extract_year_name_from_plot_py(*, file: str) -> tuple[str, str]:
    """
    Given a path such as.

    >>> /home/.../plotting_examples/plotting_examples/y2022/default_plot/plot.py

    Return:
    ------
    >>> 2022, default_plot

    """
    pth = Path(file)
    if pth.suffix != ".py":
        msg = "Expect this to be run on .py files."
        raise ValueError(msg)
    year, name = (
        str(pth)
        .rsplit("plotting_examples/plotting_examples/", maxsplit=1)[-1]
        .rsplit("/", maxsplit=1)[0]
        .split("/")
    )
    return year, name
