#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# mpterm plugin
#
# File:     mpplugin
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2024-07-06
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------


from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
from serialport import SerialPort
from qterminalwidget import QTerminalWidget


class MpPluginWidgetType(Enum):
    NoWidget = 0
    Label = 1
    Button = 2
    ComboBox = 3
    CheckBox = 4


@dataclass
class MpPluginWidget:
    type: MpPluginWidgetType = MpPluginWidgetType.NoWidget
    name: str = ""
    description: str = ""
    action: Callable = None
    combo_data: Any = None


@dataclass
class MpPluginInfo:
    name: str = ""
    description: str = ""
    date: str = ""
    author: str = ""
    doc: str = ""
    widgets: list[MpPluginWidget] = field(default_factory=list)

    def add_widget(self, widget) -> None:
        self.widgets.append(widget)


class MpPlugin:

    def __init__(self) -> None:
        self.info: MpPluginInfo = None
        self.serial_port: SerialPort = None
        self.terminal: QTerminalWidget = None

    def _set_serial_port(self, serial_port: SerialPort) -> None:
        self.serial_port = serial_port

    def _set_terminal_widget(self, terminal: QTerminalWidget) -> None:
        self.terminal = terminal

    def send(self, data: bytearray) -> None:
        self.serial_port.send(data)

    def append_html_text(self, html: str) -> None:
        self.terminal.append_html_text(html)

    def append_ansi_text(self, ansi: str) -> None:
        self.terminal.append_ansi_text(ansi)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
