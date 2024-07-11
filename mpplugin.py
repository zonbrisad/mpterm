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
from typing import Any
from serialport import SerialPort


class MpPluginWidgetType(Enum):
    NoWidget = 0
    Label = 1
    Button = 2


@dataclass
class MpPluginWidget:
    type: MpPluginWidgetType = MpPluginWidgetType.NoWidget
    name: str = ""
    description: str = ""
    action: Any = None


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
        self.plugin_info = None
        self.serial_port: SerialPort = None

    def info(self) -> MpPluginInfo:
        return self.plugin_info

    def send(self, data: bytearray) -> None:
        self.serial_port.send(data)

    def set_serial_port(self, serial_port: SerialPort) -> None:
        self.serial_port = serial_port


def main() -> None:
    pass


if __name__ == "__main__":
    main()
