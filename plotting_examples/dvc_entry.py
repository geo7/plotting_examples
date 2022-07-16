"""
Create an entry in the dvc.yaml file for the particular plot.
"""
from __future__ import annotations

import pathlib

import yaml

from plotting_examples.extract_year_name import extract_year_name_from_plot_py


def add_to_dvc(*, path: pathlib.Path) -> None:
    """Add stages to dvc.yaml based on given path."""
    year, name = extract_year_name_from_plot_py(file=str(path))

    dvc = yaml.safe_load(pathlib.Path("dvc.yaml").read_text(encoding="utf8"))

    stage_name = f"{year}_{name}"

    if stage_name not in dvc["stages"].keys():
        # Project not yet added to dvc.yaml
        dvc["stages"][stage_name] = {
            "wdir": ".",
            "cmd": f"python -m plotting_examples.{year}.{name}.plot",
            "deps": [f"plotting_examples/{year}/{name}/plot.py"],
            "outs": [{f"images/{year}/{name}.png": {"cache": False}}],
        }

        with open("dvc.yaml", "w", encoding="utf8") as file:
            yaml.dump(dvc, file)
