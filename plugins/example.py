#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     example.py
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
"Example" plugin for MpTerm formats incoming bytes into hexadecimal in lines of 16 bytes each.<br>
<br>
"""

plugin_info = MpPluginInfo(
    name="Example",
    description="Example plugin for MpTerm",
    date="2024-07-25",
    author="Peter Malmberg <peter.malmberg@gmail.com>",
)

# Code -----------------------------------------------------------------------


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.cnt = 0
        self.info = plugin_info
        self.info.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Label,
                "Label widget",
            )
        )
        self.info.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Button,
                "Button widget",
                action=self.button_action,
            )
        )
        self.info.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.ComboBox,
                "",
                "Selected waveform",
                combo_data={"Item A": "AA", "Item B": "BB", "Item C": "CC"},
                action=self.combobox_action,
            )
        )
        self.info.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.CheckBox,
                "Check",
                "Check the box",
                action=self.checkbox_action,
            )
        )

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

    def button_action(self) -> None:
        self.terminal.append_html_text("Button<br>")

    def combobox_action(self) -> None:
        self.terminal.append_html_text("Combobox<br>")

    def checkbox_action(self) -> None:
        self.terminal.append_html_text("Checkbox<br>")


def main() -> None: ...


if __name__ == "__main__":
    main()
