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

from mpplugin import MpPlugin, MpPluginWidget, MpPluginWidgetType

# Variables ------------------------------------------------------------------

doc = """
<br><br>
"Dummy" plugin for MpTerm formats incoming bytes into hexadecimal in lines of 16 bytes each.<br>
<br>
"""

plugin_name = "Dummy"
plugin_description = "Dummy plugin for MpTerm"
plugin_date = "2024-07-23"
plugin_author = "Peter Malmberg <peter.malmberg@gmail.com>"


# Code -----------------------------------------------------------------------


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = plugin_name
        self.description = plugin_description
        self.date = plugin_date
        self.author = plugin_author
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
