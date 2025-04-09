#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# simple gui for handling raspberry pi gpio ports.
#
# File:     pgio
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2025-04-09
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
#
# https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/
# https://gpiozero.readthedocs.io/en/latest/recipes.html
# https://pypi.org/project/RPi.GPIO/
# https://gpiozero.readthedocs.io/en/latest/migrating_from_rpigpio.html

from curses.ascii import alt
from email.charset import QP
import traceback
import os
import sys
import logging
import argparse
from dataclasses import dataclass, field
from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMenuBar,
    QAction,
    QStatusBar,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QDialogButtonBox,
    QPushButton,
    QMessageBox,
    QWidget,
    QLabel,
    QFileDialog,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QComboBox,
)
from sympy import im

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO not available, running in simulation mode.")
    GPIO = None


class App:
    NAME = "pgio"
    VERSION = "0.01"
    DESCRIPTION = "simple gui for handling raspberry pi gpio ports."
    LICENSE = ""
    AUTHOR = "Peter Malmberg"
    EMAIL = "<peter.malmberg@gmail.com>"
    ORG = "__ORGANISATION__"
    HOME = ""
    ICON = ""


# Qt main window settings
win_title = App.NAME
win_x_size = 420
win_y_size = 240
about_html = f"""
<center><h2>{App.NAME}</h2></center>
<br>
<b>Version: </b>{App.VERSION}
<br>
<b>Author: </b>{App.AUTHOR}
<br>
<hr>
<br>
{App.DESCRIPTION}
<br>
"""


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle(App.NAME)
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(400, 300)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(2)
        self.setLayout(self.verticalLayout)

        # TextEdit
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.textEdit)
        self.textEdit.insertHtml(about_html)

        # Buttonbox
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.setCenterButtons(True)
        self.verticalLayout.addWidget(self.buttonBox)

    @staticmethod
    def about(parent=None):
        dialog = AboutDialog(parent)
        result = dialog.exec_()
        return result == QDialog.Accepted


@dataclass
class GPIOX:
    name: str = ""
    id: int = 0
    id_p1: int = 0
    altx: str = ""


gpio_list = [
    GPIOX("GPIO 1", 1, 1, "ALT0"),
    GPIOX("GPIO 2", 2, 2, "ALT1"),
    GPIOX("GPIO 3", 3, 3, "ALT2"),
    GPIOX("GPIO 4", 4, 4, "ALT3"),
]


class GPIOWidget(QWidget):
    def __init__(self, gpio: GPIOX, parent=None):
        super().__init__()
        # self.macro = macro
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        # self.layout.setSpacing(2)
        self.setLayout(self.layout)

        self.name = QLabel(gpio.name)
        self.macro_edit = QLineEdit("aaaa")

        self.iomode = QComboBox()
        self.iomode.addItem("Input")
        self.iomode.addItem("Output")
        self.layout.addWidget(self.iomode)

        self.mode = QComboBox()
        self.mode.addItem("Pullup")
        self.mode.addItem("Pulldown")
        self.mode.addItem("None")
        self.layout.addWidget(self.mode)

        self.buttibox = QPushButton("OK")
        self.buttibox.setCheckable(True)
        self.layout.addWidget(self.buttibox)
        # self.hexModeCb = QCheckBox("Hex")
        # self.hexModeCb.stateChanged.connect(self.macroChanged)
        # self.repeatCb = QCheckBox("Repeat")

        # self.intervallEdit = QLineEdit(str(macro.intervallEdit))
        # self.intervallEdit.textChanged.connect(self.intervallChanged)
        # self.intervallEdit.setMaximumWidth(40)
        # self.setMaxLength(4)
        # self.setSizePolicy(5)

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.macro_edit)
        # self.layout.addWidget(self.hexModeCb)
        # self.layout.addWidget(self.repeatCb)
        # self.layout.addWidget(self.intervallEdit)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(win_x_size, win_y_size)
        self.setWindowTitle(win_title)
        # self.setWindowIcon(QIcon(App.ICON))

        # Create central widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)

        # TextEdit
        # self.textEdit = QTextEdit(self.centralwidget)
        # self.verticalLayout.addWidget(self.textEdit)
        for gpio in gpio_list:
            self.verticalLayout.addWidget(GPIOWidget(gpio, self.centralwidget))
        # self.verticalLayout.addSpacing(4)
        # x = GPIOWidget(self.centralwidget)
        # self.verticalLayout.addWidget(x)
        # x = GPIOWidget(self.centralwidget)
        # self.verticalLayout.addWidget(x)
        # x = GPIOWidget(self.centralwidget)
        # self.verticalLayout.addWidget(x)
        self.verticalLayout.addStretch()

        # Menubar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Menus
        self.menuFile = QMenu("File", self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.menuHelp = QMenu("Help", self.menubar)
        self.menubar.addAction(self.menuHelp.menuAction())

        # self.actionOpen = QAction("Open", self)
        # self.actionOpen.setStatusTip("Open file")
        # self.actionOpen.setShortcut("Ctrl+O")
        # self.actionOpen.triggered.connect(self.open)
        # self.menuFile.addAction(self.actionOpen)
        # self.menuFile.addSeparator()

        self.actionQuit = QAction("Quit", self)
        self.actionQuit.setStatusTip("Quit application")
        self.actionQuit.setShortcut("Ctrl+Q")
        self.actionQuit.triggered.connect(self.exit)
        self.menuFile.addAction(self.actionQuit)

        self.actionAbout = QAction("About", self)
        self.actionAbout.setStatusTip("About")
        self.actionAbout.triggered.connect(lambda: AboutDialog.about())
        self.menuHelp.addAction(self.actionAbout)

        # Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setLayoutDirection(Qt.LeftToRight)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # self.statusbar.showMessage(
        #     f"Board: {GPIO.RPI_INFO['TYPE']}  CPU: {GPIO.RPI_INFO['PROCESSOR']} {GPIO.RPI_INFO['RAM']} P1:{GPIO.RPI_INFO["P1_REVISION"]}"
        # )

    def exit(self):
        self.close()
        # msgBox = QMessageBox()
        # msgBox.setIcon(QMessageBox.Information)
        # msgBox.setWindowTitle("Quit")
        # msgBox.setText("Are you sure you want to quit?")
        # msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # if msgBox.exec() == QMessageBox.Ok:
        #     self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.exit()
        return super().closeEvent(event)


def main() -> None:
    logging_format = "[%(levelname)s] %(lineno)-4d %(funcName)-14s : %(message)s"
    logging.basicConfig(format=logging_format)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
    parser = argparse.ArgumentParser(
        prog=App.NAME, description=App.DESCRIPTION, epilog="", add_help=True
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{App.NAME} {App.VERSION}",
        help="Print version information",
    )

    parser.add_argument(
        "--debug", action="store_true", default=False, help="Print debug messages"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format=logging_format, level=logging.DEBUG)


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        print("ERROR, UNEXPECTED EXCEPTION")
        print(str(e))
        traceback.print_exc()
        os._exit(1)
