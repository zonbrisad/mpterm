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
    QWidget,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QSlider,
    QSizePolicy,
)
from PyQt5.QtCore import QTimer, Qt
from qedit import QNumberEdit


class MpPluginWidgetType(Enum):
    NoWidget = 0
    Label = 1
    Button = 2
    ComboBox = 3
    CheckBox = 4
    LineEdit = 5
    Slider = 6
    Spacer = 100


class MpReceiveMode(Enum):
    Continous = 1
    Message = 2


@dataclass
class MpPluginWidget:
    type: MpPluginWidgetType = MpPluginWidgetType.NoWidget
    name: str = ""
    description: str = ""
    action: Callable = None
    combo_data: Any = None
    widget: QWidget = None
    value: Any = None
    min: int = None
    max: int = None

    def get_combo_value(self) -> Any:
        self.action(self.widget.currentData())

    def get_numedit_value(self) -> Any:
        self.action(self.widget.get_value())

    def get_slider_value(self, value) -> Any:
        self.action(value)

    def set_text(self, name: str) -> None:
        self.name = name
        self.widget.setText(name)

    def get_value(self) -> Any:
        if self.type == MpPluginWidgetType.Slider:
            return self.widget.tickPosition()
        elif self.type == MpPluginWidgetType.ComboBox:
            return self.widget.currentData()
        # elif self.type == MpPluginWidgetType.LineEdit:


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

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.receive_timeout)

        self.buf: bytearray = bytearray()

        self.mode = MpReceiveMode.Continous

    def _set_serial_port(self, serial_port: SerialPort) -> None:
        self.serial_port = serial_port

    def _set_terminal_widget(self, terminal: QTerminalWidget) -> None:
        self.terminal = terminal

    def receive(self, data: bytearray) -> None:
        if self.mode == MpReceiveMode.Continous:
            self.data(data)
        elif self.mode == MpReceiveMode.Message:
            self.buf.extend(data)

    def receive_timeout(self) -> None:
        self.data(self.buf)

    def start_timer(self, timeout: int) -> None:
        self.timer.setSingleShot(True)
        self.timer.setInterval(timeout)
        self.timer.start()

    def send(self, data: bytearray) -> None:
        self.serial_port.send(data)

    def send_string(self, data: str) -> None:
        self.serial_port.send_string(data)

    def send_msg(self, data: bytearray, timeout: int) -> None:
        self.mode = MpReceiveMode.Message
        self.buf.clear()
        self.serial_port.send(data)
        if timeout > 0:
            self.start_timer(timeout)

    def send_msg_string(self, data: str, timeout: int) -> None:
        self.send_msg(bytearray(data.encode()), timeout)

    def append_html_text(self, html: str) -> None:
        self.terminal.append_html_text(html)
        self.terminal.scroll_down()

    def append_ansi_text(self, ansi: str) -> None:
        self.terminal.append_ansi_text(ansi)
        self.terminal.scroll_down()

    def add_widget(self, widget: MpPluginWidget) -> None:
        self.widgets.append(widget)
        self._create_widget(widget)

    def add_label(self, text: str) -> MpPluginWidget:
        widget = MpPluginWidget(MpPluginWidgetType.Label, text)
        self.add_widget(widget)
        return widget

    def add_button(
        self, text: str, description: str, action: Callable
    ) -> MpPluginWidget:
        widget = MpPluginWidget(MpPluginWidgetType.Button, text, description, action)
        self.add_widget(widget)
        return widget

    def add_slider(
        self, text: str, description: str, action: Callable, min: int, max: int
    ) -> MpPluginWidget:
        widget = MpPluginWidget(
            MpPluginWidgetType.Slider, text, description, action, min=min, max=max
        )
        self.add_widget(widget)
        return widget

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
                # print(f"{key} -> {value}")
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

        if widget.type == MpPluginWidgetType.Slider:
            mpw = QSlider()
            mpw.setOrientation(Qt.Orientation.Horizontal)
            mpw.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            mpw.setRange(widget.min, widget.max)

            if widget.action is not None:
                mpw.valueChanged.connect(widget.get_slider_value)

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
