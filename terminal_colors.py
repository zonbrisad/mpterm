#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# Color codes for terminal decoder
#
# File:    terminal_colors.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2022-05-22
# License: MIT
# Python:  3
#
# ----------------------------------------------------------------------------
# Pyplate
#   This file is generated from pyplate Python template generator.
#
# Pyplate is developed by:
#   Peter Malmberg <peter.malmberg@gmail.com>
#
# Available at:
#   https://github.com/zobrisad/pyplate.git
#
# ---------------------------------------------------------------------------
# References:
# https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
# https://www.ditig.com/256-colors-cheat-sheet
# https://michurin.github.io/xterm256-color-picker/
# https://vt100.net/docs/vt510-rm/contents.html
#
#

from __future__ import annotations
import logging


Palette256 = [
    {"name": "Black (SYSTEM)", "hex": "#000000"},
    {"name": "Maroon (SYSTEM)", "hex": "#800000"},
    {"name": "Green (SYSTEM)", "hex": "#008000"},
    {"name": "Olive (SYSTEM)", "hex": "#808000"},
    {"name": "Navy (SYSTEM)", "hex": "#000080"},
    {"name": "Purple (SYSTEM)", "hex": "#800080"},
    {"name": "Teal (SYSTEM)", "hex": "#008080"},
    {"name": "Silver (SYSTEM)", "hex": "#c0c0c0"},
    {"name": "Grey (SYSTEM)", "hex": "#808080"},
    {"name": "Red (SYSTEM)", "hex": "#ff0000"},
    {"name": "Lime (SYSTEM)", "hex": "#00ff00"},
    {"name": "Yellow (SYSTEM)", "hex": "#ffff00"},
    {"name": "Blue (SYSTEM)", "hex": "#0000ff"},
    {"name": "Fuchsia (SYSTEM)", "hex": "#ff00ff"},
    {"name": "Aqua (SYSTEM)", "hex": "#00ffff"},
    {"name": "White (SYSTEM)", "hex": "#ffffff"},
    {"name": "Grey0", "hex": "#000000"},
    {"name": "NavyBlue", "hex": "#00005f"},
    {"name": "DarkBlue", "hex": "#000087"},
    {"name": "Blue3", "hex": "#0000af"},
    {"name": "Blue3", "hex": "#0000d7"},
    {"name": "Blue1", "hex": "#0000ff"},
    {"name": "DarkGreen", "hex": "#005f00"},
    {"name": "DeepSkyBlue4", "hex": "#005f5f"},
    {"name": "DeepSkyBlue4", "hex": "#005f87"},
    {"name": "DeepSkyBlue4", "hex": "#005faf"},
    {"name": "DodgerBlue3", "hex": "#005fd7"},
    {"name": "DodgerBlue2", "hex": "#005fff"},
    {"name": "Green4", "hex": "#008700"},
    {"name": "SpringGreen4", "hex": "#00875f"},
    {"name": "Turquoise4", "hex": "#008787"},
    {"name": "DeepSkyBlue3", "hex": "#0087af"},
    {"name": "DeepSkyBlue3", "hex": "#0087d7"},
    {"name": "DodgerBlue1", "hex": "#0087ff"},
    {"name": "Green3", "hex": "#00af00"},
    {"name": "SpringGreen3", "hex": "#00af5f"},
    {"name": "DarkCyan", "hex": "#00af87"},
    {"name": "LightSeaGreen", "hex": "#00afaf"},
    {"name": "DeepSkyBlue2", "hex": "#00afd7"},
    {"name": "DeepSkyBlue1", "hex": "#00afff"},
    {"name": "Green3", "hex": "#00d700"},
    {"name": "SpringGreen3", "hex": "#00d75f"},
    {"name": "SpringGreen2", "hex": "#00d787"},
    {"name": "Cyan3", "hex": "#00d7af"},
    {"name": "DarkTurquoise", "hex": "#00d7d7"},
    {"name": "Turquoise2", "hex": "#00d7ff"},
    {"name": "Green1", "hex": "#00ff00"},
    {"name": "SpringGreen2", "hex": "#00ff5f"},
    {"name": "SpringGreen1", "hex": "#00ff87"},
    {"name": "MediumSpringGreen", "hex": "#00ffaf"},
    {"name": "Cyan2", "hex": "#00ffd7"},
    {"name": "Cyan1", "hex": "#00ffff"},
    {"name": "DarkRed", "hex": "#5f0000"},
    {"name": "DeepPink4", "hex": "#5f005f"},
    {"name": "Purple4", "hex": "#5f0087"},
    {"name": "Purple4", "hex": "#5f00af"},
    {"name": "Purple3", "hex": "#5f00d7"},
    {"name": "BlueViolet", "hex": "#5f00ff"},
    {"name": "Orange4", "hex": "#5f5f00"},
    {"name": "Grey37", "hex": "#5f5f5f"},
    {"name": "MediumPurple4", "hex": "#5f5f87"},
    {"name": "SlateBlue3", "hex": "#5f5faf"},
    {"name": "SlateBlue3", "hex": "#5f5fd7"},
    {"name": "RoyalBlue1", "hex": "#5f5fff"},
    {"name": "Chartreuse4", "hex": "#5f8700"},
    {"name": "DarkSeaGreen4", "hex": "#5f875f"},
    {"name": "PaleTurquoise4", "hex": "#5f8787"},
    {"name": "SteelBlue", "hex": "#5f87af"},
    {"name": "SteelBlue3", "hex": "#5f87d7"},
    {"name": "CornflowerBlue", "hex": "#5f87ff"},
    {"name": "Chartreuse3", "hex": "#5faf00"},
    {"name": "DarkSeaGreen4", "hex": "#5faf5f"},
    {"name": "CadetBlue", "hex": "#5faf87"},
    {"name": "CadetBlue", "hex": "#5fafaf"},
    {"name": "SkyBlue3", "hex": "#5fafd7"},
    {"name": "SteelBlue1", "hex": "#5fafff"},
    {"name": "Chartreuse3", "hex": "#5fd700"},
    {"name": "PaleGreen3", "hex": "#5fd75f"},
    {"name": "SeaGreen3", "hex": "#5fd787"},
    {"name": "Aquamarine3", "hex": "#5fd7af"},
    {"name": "MediumTurquoise", "hex": "#5fd7d7"},
    {"name": "SteelBlue1", "hex": "#5fd7ff"},
    {"name": "Chartreuse2", "hex": "#5fff00"},
    {"name": "SeaGreen2", "hex": "#5fff5f"},
    {"name": "SeaGreen1", "hex": "#5fff87"},
    {"name": "SeaGreen1", "hex": "#5fffaf"},
    {"name": "Aquamarine1", "hex": "#5fffd7"},
    {"name": "DarkSlateGray2", "hex": "#5fffff"},
    {"name": "DarkRed", "hex": "#870000"},
    {"name": "DeepPink4", "hex": "#87005f"},
    {"name": "DarkMagenta", "hex": "#870087"},
    {"name": "DarkMagenta", "hex": "#8700af"},
    {"name": "DarkViolet", "hex": "#8700d7"},
    {"name": "Purple", "hex": "#8700ff"},
    {"name": "Orange4", "hex": "#875f00"},
    {"name": "LightPink4", "hex": "#875f5f"},
    {"name": "Plum4", "hex": "#875f87"},
    {"name": "MediumPurple3", "hex": "#875faf"},
    {"name": "MediumPurple3", "hex": "#875fd7"},
    {"name": "SlateBlue1", "hex": "#875fff"},
    {"name": "Yellow4", "hex": "#878700"},
    {"name": "Wheat4", "hex": "#87875f"},
    {"name": "Grey53", "hex": "#878787"},
    {"name": "LightSlateGrey", "hex": "#8787af"},
    {"name": "MediumPurple", "hex": "#8787d7"},
    {"name": "LightSlateBlue", "hex": "#8787ff"},
    {"name": "Yellow4", "hex": "#87af00"},
    {"name": "DarkOliveGreen3", "hex": "#87af5f"},
    {"name": "DarkSeaGreen", "hex": "#87af87"},
    {"name": "LightSkyBlue3", "hex": "#87afaf"},
    {"name": "LightSkyBlue3", "hex": "#87afd7"},
    {"name": "SkyBlue2", "hex": "#87afff"},
    {"name": "Chartreuse2", "hex": "#87d700"},
    {"name": "DarkOliveGreen3", "hex": "#87d75f"},
    {"name": "PaleGreen3", "hex": "#87d787"},
    {"name": "DarkSeaGreen3", "hex": "#87d7af"},
    {"name": "DarkSlateGray3", "hex": "#87d7d7"},
    {"name": "SkyBlue1", "hex": "#87d7ff"},
    {"name": "Chartreuse1", "hex": "#87ff00"},
    {"name": "LightGreen", "hex": "#87ff5f"},
    {"name": "LightGreen", "hex": "#87ff87"},
    {"name": "PaleGreen1", "hex": "#87ffaf"},
    {"name": "Aquamarine1", "hex": "#87ffd7"},
    {"name": "DarkSlateGray1", "hex": "#87ffff"},
    {"name": "Red3", "hex": "#af0000"},
    {"name": "DeepPink4", "hex": "#af005f"},
    {"name": "MediumVioletRed", "hex": "#af0087"},
    {"name": "Magenta3", "hex": "#af00af"},
    {"name": "DarkViolet", "hex": "#af00d7"},
    {"name": "Purple", "hex": "#af00ff"},
    {"name": "DarkOrange3", "hex": "#af5f00"},
    {"name": "IndianRed", "hex": "#af5f5f"},
    {"name": "HotPink3", "hex": "#af5f87"},
    {"name": "MediumOrchid3", "hex": "#af5faf"},
    {"name": "MediumOrchid", "hex": "#af5fd7"},
    {"name": "MediumPurple2", "hex": "#af5fff"},
    {"name": "DarkGoldenrod", "hex": "#af8700"},
    {"name": "LightSalmon3", "hex": "#af875f"},
    {"name": "RosyBrown", "hex": "#af8787"},
    {"name": "Grey63", "hex": "#af87af"},
    {"name": "MediumPurple2", "hex": "#af87d7"},
    {"name": "MediumPurple1", "hex": "#af87ff"},
    {"name": "Gold3", "hex": "#afaf00"},
    {"name": "DarkKhaki", "hex": "#afaf5f"},
    {"name": "NavajoWhite3", "hex": "#afaf87"},
    {"name": "Grey69", "hex": "#afafaf"},
    {"name": "LightSteelBlue3", "hex": "#afafd7"},
    {"name": "LightSteelBlue", "hex": "#afafff"},
    {"name": "Yellow3", "hex": "#afd700"},
    {"name": "DarkOliveGreen3", "hex": "#afd75f"},
    {"name": "DarkSeaGreen3", "hex": "#afd787"},
    {"name": "DarkSeaGreen2", "hex": "#afd7af"},
    {"name": "LightCyan3", "hex": "#afd7d7"},
    {"name": "LightSkyBlue1", "hex": "#afd7ff"},
    {"name": "GreenYellow", "hex": "#afff00"},
    {"name": "DarkOliveGreen2", "hex": "#afff5f"},
    {"name": "PaleGreen1", "hex": "#afff87"},
    {"name": "DarkSeaGreen2", "hex": "#afffaf"},
    {"name": "DarkSeaGreen1", "hex": "#afffd7"},
    {"name": "PaleTurquoise1", "hex": "#afffff"},
    {"name": "Red3", "hex": "#d70000"},
    {"name": "DeepPink3", "hex": "#d7005f"},
    {"name": "DeepPink3", "hex": "#d70087"},
    {"name": "Magenta3", "hex": "#d700af"},
    {"name": "Magenta3", "hex": "#d700d7"},
    {"name": "Magenta2", "hex": "#d700ff"},
    {"name": "DarkOrange3", "hex": "#d75f00"},
    {"name": "IndianRed", "hex": "#d75f5f"},
    {"name": "HotPink3", "hex": "#d75f87"},
    {"name": "HotPink2", "hex": "#d75faf"},
    {"name": "Orchid", "hex": "#d75fd7"},
    {"name": "MediumOrchid1", "hex": "#d75fff"},
    {"name": "Orange3", "hex": "#d78700"},
    {"name": "LightSalmon3", "hex": "#d7875f"},
    {"name": "LightPink3", "hex": "#d78787"},
    {"name": "Pink3", "hex": "#d787af"},
    {"name": "Plum3", "hex": "#d787d7"},
    {"name": "Violet", "hex": "#d787ff"},
    {"name": "Gold3", "hex": "#d7af00"},
    {"name": "LightGoldenrod3", "hex": "#d7af5f"},
    {"name": "Tan", "hex": "#d7af87"},
    {"name": "MistyRose3", "hex": "#d7afaf"},
    {"name": "Thistle3", "hex": "#d7afd7"},
    {"name": "Plum2", "hex": "#d7afff"},
    {"name": "Yellow3", "hex": "#d7d700"},
    {"name": "Khaki3", "hex": "#d7d75f"},
    {"name": "LightGoldenrod2", "hex": "#d7d787"},
    {"name": "LightYellow3", "hex": "#d7d7af"},
    {"name": "Grey84", "hex": "#d7d7d7"},
    {"name": "LightSteelBlue1", "hex": "#d7d7ff"},
    {"name": "Yellow2", "hex": "#d7ff00"},
    {"name": "DarkOliveGreen1", "hex": "#d7ff5f"},
    {"name": "DarkOliveGreen1", "hex": "#d7ff87"},
    {"name": "DarkSeaGreen1", "hex": "#d7ffaf"},
    {"name": "Honeydew2", "hex": "#d7ffd7"},
    {"name": "LightCyan1", "hex": "#d7ffff"},
    {"name": "Red1", "hex": "#ff0000"},
    {"name": "DeepPink2", "hex": "#ff005f"},
    {"name": "DeepPink1", "hex": "#ff0087"},
    {"name": "DeepPink1", "hex": "#ff00af"},
    {"name": "Magenta2", "hex": "#ff00d7"},
    {"name": "Magenta1", "hex": "#ff00ff"},
    {"name": "OrangeRed1", "hex": "#ff5f00"},
    {"name": "IndianRed1", "hex": "#ff5f5f"},
    {"name": "IndianRed1", "hex": "#ff5f87"},
    {"name": "HotPink", "hex": "#ff5faf"},
    {"name": "HotPink", "hex": "#ff5fd7"},
    {"name": "MediumOrchid1", "hex": "#ff5fff"},
    {"name": "DarkOrange", "hex": "#ff8700"},
    {"name": "Salmon1", "hex": "#ff875f"},
    {"name": "LightCoral", "hex": "#ff8787"},
    {"name": "PaleVioletRed1", "hex": "#ff87af"},
    {"name": "Orchid2", "hex": "#ff87d7"},
    {"name": "Orchid1", "hex": "#ff87ff"},
    {"name": "Orange1", "hex": "#ffaf00"},
    {"name": "SandyBrown", "hex": "#ffaf5f"},
    {"name": "LightSalmon1", "hex": "#ffaf87"},
    {"name": "LightPink1", "hex": "#ffafaf"},
    {"name": "Pink1", "hex": "#ffafd7"},
    {"name": "Plum1", "hex": "#ffafff"},
    {"name": "Gold1", "hex": "#ffd700"},
    {"name": "LightGoldenrod2", "hex": "#ffd75f"},
    {"name": "LightGoldenrod2", "hex": "#ffd787"},
    {"name": "NavajoWhite1", "hex": "#ffd7af"},
    {"name": "MistyRose1", "hex": "#ffd7d7"},
    {"name": "Thistle1", "hex": "#ffd7ff"},
    {"name": "Yellow1", "hex": "#ffff00"},
    {"name": "LightGoldenrod1", "hex": "#ffff5f"},
    {"name": "Khaki1", "hex": "#ffff87"},
    {"name": "Wheat1", "hex": "#ffffaf"},
    {"name": "Cornsilk1", "hex": "#ffffd7"},
    {"name": "Grey100", "hex": "#ffffff"},
    {"name": "Grey3", "hex": "#080808"},
    {"name": "Grey7", "hex": "#121212"},
    {"name": "Grey11", "hex": "#1c1c1c"},
    {"name": "Grey15", "hex": "#262626"},
    {"name": "Grey19", "hex": "#303030"},
    {"name": "Grey23", "hex": "#3a3a3a"},
    {"name": "Grey27", "hex": "#444444"},
    {"name": "Grey30", "hex": "#4e4e4e"},
    {"name": "Grey35", "hex": "#585858"},
    {"name": "Grey39", "hex": "#626262"},
    {"name": "Grey42", "hex": "#6c6c6c"},
    {"name": "Grey46", "hex": "#767676"},
    {"name": "Grey50", "hex": "#808080"},
    {"name": "Grey54", "hex": "#8a8a8a"},
    {"name": "Grey58", "hex": "#949494"},
    {"name": "Grey62", "hex": "#9e9e9e"},
    {"name": "Grey66", "hex": "#a8a8a8"},
    {"name": "Grey70", "hex": "#b2b2b2"},
    {"name": "Grey74", "hex": "#bcbcbc"},
    {"name": "Grey78", "hex": "#c6c6c6"},
    {"name": "Grey82", "hex": "#d0d0d0"},
    {"name": "Grey85", "hex": "#dadada"},
    {"name": "Grey89", "hex": "#e4e4e4"},
    {"name": "Grey93", "hex": "#eeeeee"},
]


def rgb2str(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


PaletteXtermL = [
    rgb2str(0, 0, 0),
    rgb2str(205, 0, 0),
    rgb2str(0, 205, 0),
    rgb2str(205, 205, 0),
    rgb2str(0, 0, 238),
    rgb2str(205, 0, 205),
    rgb2str(0, 205, 205),
    rgb2str(229, 229, 229),
    rgb2str(127, 127, 127),
    rgb2str(255, 0, 0),
    rgb2str(0, 255, 0),
    rgb2str(255, 255, 0),
    rgb2str(92, 92, 255),
    rgb2str(255, 0, 255),
    rgb2str(0, 255, 255),
    rgb2str(255, 255, 255),
]

PaletteVSCodeL = [
    rgb2str(0, 0, 0),
    rgb2str(205, 49, 49),
    rgb2str(13, 188, 121),
    rgb2str(229, 229, 16),
    rgb2str(36, 114, 200),
    rgb2str(188, 63, 188),
    rgb2str(17, 168, 205),
    rgb2str(229, 229, 229),
    rgb2str(102, 102, 102),
    rgb2str(241, 76, 76),
    rgb2str(35, 209, 139),
    rgb2str(245, 245, 67),
    rgb2str(59, 142, 234),
    rgb2str(214, 112, 214),
    rgb2str(41, 184, 219),
    rgb2str(229, 229, 229),
]

PalettePutty = [
    rgb2str(0, 0, 0),
    rgb2str(187, 0, 0),
    rgb2str(0, 187, 0),
    rgb2str(187, 187, 0),
    rgb2str(0, 0, 187),
    rgb2str(187, 0, 187),
    rgb2str(0, 187, 187),
    rgb2str(187, 187, 187),
    rgb2str(85, 85, 85),
    rgb2str(255, 85, 85),
    rgb2str(85, 255, 85),
    rgb2str(255, 255, 85),
    rgb2str(85, 85, 255),
    rgb2str(255, 85, 255),
    rgb2str(85, 255, 255),
    rgb2str(255, 255, 255),
]

PaletteWinXPL = [
    rgb2str(0, 0, 0),
    rgb2str(128, 0, 0),
    rgb2str(0, 128, 0),
    rgb2str(128, 128, 0),
    rgb2str(0, 0, 128),
    rgb2str(128, 0, 128),
    rgb2str(0, 128, 128),
    rgb2str(192, 192, 192),
    rgb2str(128, 128, 128),
    rgb2str(255, 0, 0),
    rgb2str(0, 255, 0),
    rgb2str(255, 255, 0),
    rgb2str(0, 0, 255),
    rgb2str(255, 0, 255),
    rgb2str(0, 255, 255),
    rgb2str(255, 255, 255),
]
# PaletteWinXPL = [
#     "#000000",
#     "#800000",
#     "#008000",
#     "#808000",
#     "#000080",
#     "#800080",
#     "#008080",
#     "#c0c0c0",
#     "#808080",
#     "#ff0000",
#     "#00ff00",
#     "#ffff00",
#     "#0000ff",
#     "#ff00ff",
#     "#00ffff",
#     "#ffffff",
# ]


PaletteDefault = [
    "#000000",
    "#cc0000",
    "#4e9a06",
    "#c4a000",
    "#3465a4",
    "#75507b",
    "#06989a",
    "#d3d7cf",
    "#555753",
    "#ef2929",
    "#8ae234",
    "#fce94f",
    "#729fcf",
    "#ad7fa8",
    "#34e2e2",
    "#eeeeec",
]


def main() -> None:
    logging.basicConfig(
        format="[%(levelname)s] Line: %(lineno)d %(message)s", level=logging.DEBUG
    )


if __name__ == "__main__":
    main()
