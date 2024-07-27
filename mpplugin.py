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


from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable
from serialport import SerialPort
from qterminalwidget import QTerminalWidget
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QWidget,
)
from qedit import QHexEdit, QNumberEdit


class MpPluginWidgetType(Enum):
    NoWidget = 0
    Label = 1
    Button = 2
    ComboBox = 3
    CheckBox = 4
    LineEdit = 5


@dataclass
class MpPluginWidget:
    type: MpPluginWidgetType = MpPluginWidgetType.NoWidget
    name: str = ""
    description: str = ""
    action: Callable = None
    combo_data: Any = None
    widget: Any = None
    value: Any = None
    min: int = None
    max: int = None

    def get_combo_value(self) -> Any:
        self.action(self.widget.currentData())

    def get_numedit_value(self) -> Any:
        self.action(self.widget.get_value())


class MpPlugin:

    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = ""
        self.date: str = ""
        self.author: str = ""
        self.doc: str = ""
        self.widgets: list[MpPluginWidget] = []

        self.serial_port: SerialPort = None
        self.terminal: QTerminalWidget = None

    def _set_serial_port(self, serial_port: SerialPort) -> None:
        self.serial_port = serial_port

    def _set_terminal_widget(self, terminal: QTerminalWidget) -> None:
        self.terminal = terminal

    def send(self, data: bytearray) -> None:
        self.serial_port.send(data)

    def send_string(self, data: str) -> None:
        self.serial_port.send_string(data)

    def append_html_text(self, html: str) -> None:
        self.terminal.append_html_text(html)

    def append_ansi_text(self, ansi: str) -> None:
        self.terminal.append_ansi_text(ansi)

    def add_widget(self, widget) -> None:
        self.widgets.append(widget)
        self._create_widget(widget)

    def _create_widget(self, widget: MpPluginWidget) -> None:
        if widget.type == MpPluginWidgetType.Label:
            mpw = QLabel()
            mpw.setText(widget.name)
        if widget.type == MpPluginWidgetType.Button:
            mpw = QPushButton()
            mpw.setText(widget.name)
            if widget.action is not None:
                mpw.pressed.connect(widget.action)
        if widget.type == MpPluginWidgetType.ComboBox:
            mpw = QComboBox()
            if widget.action is not None:
                mpw.activated.connect(widget.get_combo_value)
            for key, value in widget.combo_data.items():
                print(f"{key} -> {value}")
                mpw.addItem(key, value)
        if widget.type == MpPluginWidgetType.CheckBox:
            mpw = QCheckBox()
            mpw.setText(widget.name)
            if widget.action is not None:
                mpw.pressed.connect(widget.action)
        if widget.type == MpPluginWidgetType.LineEdit:
            mpw = QNumberEdit()
            mpw.set_value(widget.value)
            if widget.action is not None:
                mpw.set_on_changed(widget.get_numedit_value)

        widget.widget = mpw
        mpw.setToolTip(widget.description)

    def list_qt_widgets(self) -> list[QWidget]:
        return [widget.widget for widget in self.widgets]

    def __str__(self) -> str:
        return f"{self.name:14} {self.date:12} {self.description}  <{self.description}>"


def main() -> None:
    pass


if __name__ == "__main__":
    main()
