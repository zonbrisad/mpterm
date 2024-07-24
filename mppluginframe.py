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
from mpplugin import MpPlugin

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QWidget,
)


class MpPluginFrame(QWidget):
    def __init__(self, parent, serial_port):
        super().__init__(parent=parent)
        self.serial_port = serial_port

        self.layout = QVBoxLayout(parent)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        # self.setMaxLength(4)
        # self.setSizePolicy(5)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Plugin"))
        self.cbPlugins = QComboBox()
        self.cbPlugins.addItem("None", None)
        self.layout.addWidget(self.cbPlugins)

        self.load_plugins()
        for plugin in self.plugins:
            pgi = plugin.info
            self.cbPlugins.addItem(pgi.name, plugin)
        self.cbPlugins.currentIndexChanged.connect(self.plugin_change)

        self.widgets = []

    def add_widget(self, widget) -> None:
        self.layout.addWidget(widget)
        self.widgets.append(widget)

    def clear_widgets(self) -> None:
        for widget in self.widgets:
            self.layout.removeWidget(widget)

        self.widgets = []

    def plugin_change(self):
        plugin: MpPlugin = self.cbPlugins.currentData()
        if plugin is None:
            self.clear_widgets()
            return
        plugin_info = plugin.info

        self.clear_widgets()
        for widget in plugin_info.widgets:
            print(widget)
            but = QPushButton(parent=self.parent())
            but.setText(widget.name)
            but.setToolTip(widget.description)
            if widget.action is not None:
                but.pressed.connect(widget.action)
            self.add_widget(but)

    def load_plugins(self) -> None:

        # Find plugin files in directory
        no_list = ["mpplugin.py", "mpframe.py"]
        plugin_files = []
        for file_name in os.listdir("plugins"):
            if (
                os.path.isfile(f"plugins/{file_name}")
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
            plugin.set_serial_port(self.serial_port)
            plugin_info = plugin.info
            logging.debug(plugin_info)

    def current_plugin(self) -> MpPlugin:
        return self.cbPlugins.currentData()

    def plugins_to_str(self) -> str:
        pgs = ["<pre><br><br>"]
        for plugin in self.plugins:
            pgi = plugin.info
            pgs.append(f"{pgi.name:14} {pgi.date:12} {pgi.description}<br>")

        pgs.append("</pre>")
        return "".join(pgs)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
