"""
Generate plots at the end of the README.

Bit of a hack - but works for now, this is mainly just to display all the created plots in the
README.
"""
from __future__ import annotations

import ast
from pathlib import Path

from PIL import Image

CODE = "https://github.com/geo7/plotting_examples/blob/main/plotting_examples/{}/plot.py"


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
        im (str):
            Path to image file.
        FIGSIZE (tuple):
            Typically `figsize` tuple from `plt.subplots(figsize = FIGSIZE)`.
    """
    image = Image.open(im)
    # expected_aspect = FIGSIZE[1] / FIGSIZE[0]
    # aspect_ratio = image.size[1] / image.size[0]
    width, height = image.size

    M = 500
    if height > M:
        scale = M / height
        new_height = int(height * scale)
        new_width = int(width * scale)
        print(
            f"Resizing : {im} by scale {round(scale,1)}, from "
            f"{(width, height)} to {(new_width, new_height)}",
        )
        new_image = image.resize((new_width, new_height))
        new_image.save(im)


def main() -> int:
    year = "y2022"
    # Will have to update this when there's a different year I guess but for now meh.
    images = sorted(Path(f"./images/{year}").glob("*"))

    readme_data = {}

    for img in images:
        # breakpoint()
        # Eh - bit of a hack but should work...
        dir_from_img_path = str(img).split(f"{year}/")[-1].split(".png")[0]

        code_path = (
            Path("./plotting_examples")
            / str(year)
            / dir_from_img_path
            / "plot.py"
        )

        if "DS_Store" in str(code_path):
            continue

        assert img.exists()

        with open(code_path, encoding="utf8") as fh:
            code_txt = fh.read()
        mod = ast.parse(code_txt)
        docstr = ast.get_docstring(mod)

        if docstr == "":
            raise ValueError(f"No docstring found for : {code_path}")

        readme_data[dir_from_img_path] = {
            "img_path": img,
            "doc_str": docstr,
        }

    # Might as well sort the generated plots - don't want to include the default plot either.
    readme_data = {
        x: readme_data[x]
        for x in sorted(readme_data)
        if "default_plot" not in x
    }

    # Create values to append to readme.
    readme_update = "\n\n# Plots\n\n"

    # Create some bullet points with the plot names
    for title, _ in readme_data.items():
        readme_update += f"* [`{title}`](https://github.com/geo7/plotting_examples#{title})\n"

    readme_update += "\n"

    for title, data in readme_data.items():
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
    with open("README.md", encoding="utf8") as rm:
        rm_txt = rm.read()

    rm_txt = rm_txt.split(rm_split)[0]
    rm_txt = rm_txt + rm_split + readme_update
    # Ensure new line at eof
    rm_txt += "\n"

    with open("README.md", "w", encoding="utf8") as rm:
        rm.write(rm_txt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
