#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     dl24.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
# Not complete nor correct
# https://github.com/syssi/esphome-atorch-dl24/blob/main/docs/protocol-design.md#type-indicator
#
#

# Imports --------------------------------------------------------------------

from mpplugin import MpPluginInfo, MpPlugin, MpPluginWidget, MpPluginWidgetType

# Variables ------------------------------------------------------------------

doc = """
<br><br>
"Dummy" plugin for MpTerm formats incoming bytes into hexadecimal in lines of 16 bytes each.<br>
<br>
"""

plugin_info = MpPluginInfo(
    name="Dummy",
    description="Dummy plugin for MpTerm",
    date="2024-07-23",
    author="Peter Malmberg <peter.malmberg@gmail.com>",
)

# Code -----------------------------------------------------------------------


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.info = plugin_info
        self.cnt = 0

    def data(self, data: bytearray) -> str:
        ret = ""
        for i in range(0, data.count()):
            byte = int.from_bytes(data.at(i), "big")

            ret += f"{byte:02x} "
            self.cnt += 1
            if self.cnt >= 16:
                ret += "<br>"
                self.cnt = 0

        return ret


def main() -> None: ...


if __name__ == "__main__":
    main()
