"""
Generate plots at the end of the README.

Bit of a hack - but works for now, this is mainly just to display all the created plots
in the README.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from PIL import Image

CODE = (
    "https://github.com/geo7/plotting_examples/blob/main/plotting_examples/{}/plot.py"
)


def resize_image_if_needed(
    *,
    im: str,
) -> None:
    """
    Resize image to requred aspect ratio if needed.

    Given FIGSIZE (width, height) check to see if the aspect ratio (where
    aspect ratio = height/width) of the image file `im` matches that of
    FIGSIZE. If not then the image is resized to the correct dimensions in
    place, so the original is lost with this.

    Args:
    ----
        im (str):
            Path to image file.
        FIGSIZE (tuple):
            Typically `figsize` tuple from `plt.subplots(figsize = FIGSIZE)`.

    """
    image = Image.open(im)
    width, height = image.size

    m = 500
    if height > m:
        scale = m / height
        new_height = int(height * scale)
        new_width = int(width * scale)
        new_image = image.resize((new_width, new_height))
        new_image.save(im)


EXCLUDE_PLOTS = [
    # This is just the template for starting a new plot off.
    "default_plot",
    # Got bored of seeing this one.
    "sns_violin_plot_custom",
    # This was was annoying as well - it's an example of creating a histogram from
    # scratch with patches which eh.
    "histogram_with_two_variables",
]


def docstring_from_py_module(*, mod_path: str | Path) -> str:
    """
    Docstrings in plot.py contain context about the plot.

    These are then used in the README.
    """
    # with open(mod_path, encoding="utf8") as fh:
    with Path(mod_path).open() as fh:
        code_txt = fh.read()
    mod = ast.parse(code_txt)
    docstr = ast.get_docstring(mod)

    if docstr == "":
        msg = f"No docstring found for : {mod_path}"
        raise ValueError(msg)

    if docstr is None:
        msg = "Do not expect docstring to be None."
        raise ValueError(msg)

    return docstr


def main() -> int:
    """Generate readme with plots and docstring extracts."""
    year = "y2022"

    years = [
        # This should get the years up to 2099... If I'm still using matplotlib
        # at that point I'll consider that a success.... or maybe a failure,
        # not sure.
        Path(x.name).stem
        for x in sorted(Path("./plotting_examples").glob("*"))
        if "y20" in str(x)
    ]

    readme_data = {}

    for year in years:
        # Will have to update this when there's a different year I guess but
        # for now meh.
        images = sorted(Path(f"./images/{year}").glob("*"))

        # For each image want to build up a dictionary of the image path within
        # the repo, and the docstring from the respective python module. Then
        # in the README the python docstring will be added alongside the image.
        for img in images:
            dir_from_img_path = Path(img.name).stem

            code_path = (
                Path("./plotting_examples") / str(year) / dir_from_img_path / "plot.py"
            )

            if "DS_Store" in str(code_path):
                continue

            # Not sure why this _wouldn't_ exist
            if not img.exists():
                raise ValueError

            docstr = docstring_from_py_module(mod_path=code_path)

            readme_data[dir_from_img_path] = {
                "img_path": img,
                "doc_str": docstr,
            }

    # Might as well sort the generated plots.
    readme_data = {
        x: readme_data[x]
        for x in sorted(readme_data)
        if not any(exclude in x for exclude in EXCLUDE_PLOTS)
    }

    # Create values to append to readme.
    readme_update = "\n\n# Plots\n\n"

    # Create some bullet points with the plot names
    for title in readme_data:
        readme_update += f"* [`{title}`](https://github.com/geo7/plotting_examples?tab=readme-ov-file#{title})\n"

    readme_update += "\n"

    for title, data in readme_data.items():
        year = re.findall(r".*(y\d{4}).*", str(data["img_path"]))[0]
        readme_update += "\n\n"
        url_path = f"{year}/{title}"
        readme_update += f"## [`{title}`]({CODE.format(url_path)})\n\n"
        readme_update += str(data["doc_str"])
        readme_update += "\n\n"
        md_img_format = f"![]({data['img_path']})"
        readme_update += md_img_format

    # Update README

    # This is used to signal where automated content starts.
    rm_split = "[comment]: # (Automate plots beneath this.)"
    with Path("README.md").open() as rm:
        rm_txt = rm.read()

    rm_txt = rm_txt.split(rm_split)[0]
    rm_txt = rm_txt + rm_split + readme_update
    # Ensure new line at eof
    rm_txt += "\n"

    with Path("README.md").open("w") as file:
        file.write(rm_txt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
