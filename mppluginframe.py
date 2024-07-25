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
    QPushButton,
    QComboBox,
    QWidget,
    QCheckBox,
)


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
        self.cbPlugins = QComboBox()
        self.cbPlugins.addItem("None", None)
        self.layout.addWidget(self.cbPlugins)
        self.layout.addSpacing(10)

        self.load_plugins()
        for plugin in self.plugins:
            pgi = plugin.info
            self.cbPlugins.addItem(pgi.name, plugin)
        self.cbPlugins.currentIndexChanged.connect(self.plugin_change)

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
        plugin: MpPlugin = self.cbPlugins.currentData()
        if plugin is None:
            self.clear_widgets()
            return

        plugin_info = plugin.info

        self.clear_widgets()
        for widget in plugin_info.widgets:
            logging.debug(widget)

            if widget.type == MpPluginWidgetType.Label:
                mpw = QLabel(parent=self.parent())
                mpw.setText(widget.name)

            if widget.type == MpPluginWidgetType.Button:
                mpw = QPushButton(parent=self.parent())
                mpw.setText(widget.name)
                if widget.action is not None:
                    mpw.pressed.connect(widget.action)

            if widget.type == MpPluginWidgetType.ComboBox:
                mpw = QComboBox(parent=self.parent())
                if widget.action is not None:
                    mpw.activated.connect(widget.action)

                for key, value in widget.combo_data.items():
                    print(f"{key} -> {value}")
                    mpw.addItem(key, value)

            if widget.type == MpPluginWidgetType.CheckBox:
                mpw = QCheckBox(parent=self.parent())
                mpw.setText(widget.name)

                if widget.action is not None:
                    mpw.pressed.connect(widget.action)

            mpw.setToolTip(widget.description)
            self.add_widget(mpw)

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
            plugin._set_serial_port(self.serial_port)
            plugin._set_terminal_widget(self.terminal)
            plugin_info = plugin.info
            logging.debug(plugin_info)

    def current_plugin(self) -> MpPlugin:
        return self.cbPlugins.currentData()

    def plugins_to_str(self) -> str:
        pgs = ["<pre><br><br>"]
        for plugin in self.plugins:
            pgi = plugin.info
            pgs.append(f"{pgi.name:14} {pgi.date:12} {pgi.description}<br>")

        pgs.append("<br></pre>")
        return "".join(pgs)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
