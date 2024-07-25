#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     fy3200s.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
# https://integrac.sk/wp-content/uploads/2018/02/FY3200S-DDS-Protocol-EN-DRAFT-.pdf
#

# Imports --------------------------------------------------------------------

from enum import Enum
from mpplugin import MpPluginInfo, MpPlugin, MpPluginWidget, MpPluginWidgetType
from mpframe import MpFrame

# Variables ------------------------------------------------------------------

plugin_info = MpPluginInfo(
    name="FY3200S",
    description="FeelTech FY3200S Dual channel function generator",
    date="2024-07-25",
    author="Peter Malmberg <peter.malmberg@gmail.com>",
)

# Code -----------------------------------------------------------------------


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.info = plugin_info

        self.info.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Button,
                "Set waveform",
                "Set waveform",
                action=self.cmd_set_waveform,
            )
        )
        self.info.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.ComboBox,
                "",
                "Selected waveform",
                combo_data={"A": "AA", "B": "BB"},
                action=self.change_waveform,
            )
        )

    def data(self, data: bytearray) -> str:
        # ret = ""
        # for i in range(0, data.count()):
        #     byte = int.from_bytes(data.at(i), "big")
        #     if self.frame.add_byte(byte) is True:
        #         ret += self.frame.to_html()
        #         self.frame.clear()

        return ""

    def cmd_set_waveform(self) -> None:
        # data = self.frame.command(AtorchCommandType.Reset_All)
        # self.send(self.frame.command(AtorchCommandType.Reset_All))
        ...

    def change_waveform(self) -> None:
        print("Changing waveform")


def main() -> None:
    pass


# Main run_ext_program handle
if __name__ == "__main__":
    main()
