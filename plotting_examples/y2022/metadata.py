"""
Metadata for plotting.

I probably could / should use an rc params file for some of this stuff instead of calling from here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Colors:
    """
    Colors.

    https://mycolor.space/?hex=%23FF69B4&sub=1
    """

    PINK_COLOUR = "#ff69b4"
    BACKGROUND_COLOUR = "#f2f2f2"
    GREY = "#919191"
    BLUE = "#007FCB"
    LIGHT_GREEN = "#B4EDD2"
    DEEPER_GREEN = "#51B9BE"
    BROWNY_RED = "#554149"
    PURPLEY = "#8F6E9B"
    TAN = "#DDD7C6"


color = Colors()
