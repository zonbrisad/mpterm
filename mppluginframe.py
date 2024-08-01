#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# qt widget for handling mpterm plugins
#
# File:     mppluginwidget
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2024-07-11
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

import os
import importlib
import logging

from mpplugin import MpPlugin, MpPluginWidget, MpPluginWidgetType

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QComboBox,
    QWidget,
)
from qedit import QHexEdit, QNumberEdit


class MpPluginFrame(QWidget):
    def __init__(self, parent, serial_port, terminal):
        super().__init__(parent=parent)
        self.serial_port = serial_port
        self.terminal = terminal

        self.layout: QVBoxLayout = QVBoxLayout(parent)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        # self.setMaxLength(4)
        # self.setSizePolicy(5)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Plugin"))
        self.cb_plugins = QComboBox()
        self.cb_plugins.addItem("None", None)
        self.layout.addWidget(self.cb_plugins)
        self.layout.addSpacing(10)

        self.load_plugins()
        for plugin in self.plugins:
            self.cb_plugins.addItem(plugin.name, plugin)

        self.cb_plugins.currentIndexChanged.connect(self.plugin_change)
        self.cur_plugin: MpPlugin = None
        self.widgets = []

    def add_widget(self, widget) -> MpPluginWidget:
        self.layout.addWidget(widget)
        self.widgets.append(widget)
        return widget

    def clear_widgets(self) -> None:
        for widget in self.widgets:
            self.layout.removeWidget(widget)

        self.widgets = []

    def plugin_change(self):
        plugin: MpPlugin = self.cb_plugins.currentData()
        logging.debug(f"Plugin change: {plugin}")

        if plugin is not None:
            self.cb_plugins.setToolTip(plugin.description)
            for widget in plugin.list_qt_widgets():
                widget.setParent(self.layout.parent())
                self.layout.addWidget(widget)
                widget.setVisible(True)
        else:
            self.cb_plugins.setToolTip("")

        if self.cur_plugin is not None:
            for widget in self.cur_plugin.list_qt_widgets():
                # widget.setParent(None)
                widget.setVisible(False)

        self.cur_plugin = plugin

    def load_plugins(self) -> None:

        # Find plugin files in directory
        no_list = ["mpplugin.py", "mpframe.py"]
        plugin_files = []
        for file_name in os.listdir(f"{os.path.dirname(__file__)}/plugins"):
            if (
                os.path.isfile(f"{os.path.dirname(__file__)}/plugins/{file_name}")
                and file_name.startswith("__") is not True
                and file_name not in no_list
            ):
                plugin_files.append(os.path.splitext(file_name)[0])

        # Load plugins
        self.plugins: list[MpPlugin] = []
        for file_name in plugin_files:
            plugin: MpPlugin = importlib.import_module(
                f"plugins.{file_name}"
            ).MpTermPlugin()
            self.plugins.append(plugin)

        # Initiate plugins
        for plugin in self.plugins:
            plugin._set_serial_port(self.serial_port)
            plugin._set_terminal_widget(self.terminal)
            logging.debug(str(plugin))

    def current_plugin(self) -> MpPlugin:
        return self.cb_plugins.currentData()

    def current_plugin_name(self) -> str:
        return self.cb_plugins.currentText()

    def set_plugin(self, plugin_name: str) -> None:
        idx = self.cb_plugins.findText(plugin_name)
        if idx >= 0:
            self.cb_plugins.setCurrentIndex(idx)
            return

        self.cb_plugins.setCurrentIndex(0)

    def plugins_to_str(self) -> str:
        pgs = ["<pre><br><br>"]
        for plugin in self.plugins:
            pgs.append(f"{str(plugin)}<br>")

        pgs.append("<br></pre>")
        return "".join(pgs)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
