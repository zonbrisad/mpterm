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

from mpplugin import MpPlugin, MpPluginWidget, MpPluginWidgetType

# Variables ------------------------------------------------------------------

doc = """
<br><br>
"Example" plugin for MpTerm formats incoming bytes into hexadecimal in lines of 16 bytes each.<br>
<br>
"""

plugin_name = "Example"
plugin_description = "Example plugin for MpTerm"
plugin_date = "2024-07-25"
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

        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Label,
                "Label widget",
            )
        )
        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Button,
                "Button widget",
                action=self.button_action,
            )
        )
        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.ComboBox,
                "",
                "Selected waveform",
                combo_data={"Item A": "AA", "Item B": "BB", "Item C": "CC"},
                action=self.combobox_action,
            )
        )
        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.CheckBox,
                "Check",
                "Check the box",
                action=self.checkbox_action,
            )
        )
        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Slider,
                "",
                "Slider",
                action=self.slider_action,
                min=-100,
                max=100,
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
        self.terminal.scroll_down()

    def combobox_action(self, value) -> None:
        self.terminal.append_html_text(f"Combobox {value}<br>")
        self.terminal.scroll_down()

    def checkbox_action(self) -> None:
        self.terminal.append_html_text("Checkbox<br>")
        self.terminal.scroll_down()

    def slider_action(self, value) -> None:
        self.terminal.append_html_text(f"Slider {value}<br>")
        self.terminal.scroll_down()


def main() -> None: ...


if __name__ == "__main__":
    main()
