#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
#
# Serial terminal
#
# File:    mpterm.py
# Author:
# Date:    2017-05-29
# License:
# Python:  >=3
# QT       5
#
# -----------------------------------------------------------------------
# This file is generated from pyplate Python template generator.
# Pyplate is developed by
# Peter Malmberg <peter.malmberg@gmail.com>
#
# -----------------------------------------------------------------------
# pyuic5 mpTerminal.ui -o ui_MainWindow.py
#

# Imports --------------------------------------------------------------------

from re import ASCII
import sys
import os
import subprocess
import traceback
import logging
import argparse
import signal
import enum
import json
from datetime import datetime, date, time

from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice, QProcess
from PyQt5.QtGui import QTextCursor, QIcon, QFont, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QMenu,
    QMenuBar,
    QAction,
    QStatusBar,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QDialogButtonBox,
    QPushButton,
    QComboBox,
    QMessageBox,
    QWidget,
    QFileDialog,
)

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from ui_MainWindow import Ui_MainWindow
from dataclasses import dataclass
from escape import (
    Esc,
    Ascii,
    TerminalState,
    flag,
    escape_attribute_test,
    color_256_test,
    hex2str,
)
from terminalwin import TerminalWin

import AboutDialogXX

# Settings ------------------------------------------------------------------

# Absolute path to script itself
self_dir = os.path.abspath(os.path.dirname(sys.argv[0]))


class App:
    NAME = "mpterm plainText branch"
    VERSION = "0.2"
    DESCRIPTION = "MpTerm is a simple serial terminal program"
    LICENSE = ""
    AUTHOR = "Peter Malmberg"
    EMAIL = "peter.malmberg@gmail.com"
    ORG = ""
    HOME = "github.com/zonbrisad/mpterm"
    ICON = f"{self_dir}/icons/mp_icon2.png"


mp_settings = f"{self_dir}/mpterm.json"

# Definitions ---------------------------------------------------------------

# chars = {  0x00:"NULL",
#            0x01:"SOH",
#            0x02:"STX",
#            0x03:"ETX",
#            0x04:"EOT",
#            0x05:"ENQ",
#            0x06:"ACK",
#            0x07:"BEL",
#            0x08:"BS",
#            0x09:"TAB",
#            0x0A:"LF",
#            0x0B:"VT",
#            0x0C:"FF",
#            0x0D:"CR",
#            0x0E:"SO",
#            0x0F:"SI",
#            0x10:"DLE",
#            0x11:"DC1",
#            0x12:"DC2",
#            0x13:"DC3",
#            0x14:"DC4",
#            0x15:"NAK",
#            0x16:"SYN",
#            0x17:"ETB",
#            0x18:"CAN",
#            0x19:"EM",
#            0x1A:"SUB",
#            0x1B:"ESC",
#            0x1C:"FS",
#            0x1D:"GS",
#            0x1E:"RS",
#            0x1F:"US"
# }

# keymap = {
#     Qt.Key_Enter:("\n", "Enter"),
#     Qt.Key_Return:("\n", "Return"),
#     Qt.Key_Escape:("", "Escape"),
#     Qt.Key_Delete:("", "Delete"),
#     Qt.Key_Left:("", "Left"),
#     Qt.Key_Right:("", "Right"),
#     Qt.Key_Up:("", "Up"),
#     Qt.Key_Down:("", "Down"),
#     Qt.Key_Insert:("", "Insert"),
#     Qt.Key_Backspace:("", "Backspace"),
#     Qt.Key_Home:("", "Home"),
#     Qt.Key_End:("", "End"),
#     Qt.Key_PageDown:("", "Page down"),
#     Qt.Key_PageUp:("", "Page up"),
#     Qt.Key_F1:("\x09", "F1"),
#     Qt.Key_F2:("", "F2"),
#     Qt.Key_F3:("", "F3"),
#     Qt.Key_F4:("", "F4"),
#     Qt.Key_F5:("", "F5"),
#     Qt.Key_F6:("", "F6"),
#     Qt.Key_F7:("", "F7"),
#     Qt.Key_F8:("", "F8"),
#     Qt.Key_F9:("", "F9"),
#     Qt.Key_F10:("", "F10"),
#     Qt.Key_F11:("", "F11"),
#     Qt.Key_F12:("", "F12"),
#     Qt.Key_Control:("", "Control"),
#     Qt.Key_Shift:("", "Shift"),
#     Qt.Key_Alt:("", "Alt"),
#     Qt.Key_AltGr:("", "Alt Gr"),
#     Qt.Key_Space:(" ", "Space"),
#     Qt.Key_Print:("", "Print"),
#     Qt.Key_ScrollLock:("", "Scroll lock"),
#     Qt.Key_CapsLock:("", "Caps lock"),
#     Qt.Key_Pause:("", "Pause"),
#     Qt.Key_Tab:(Ascii.TAB, "Tab")
# }

# def get_description(key: QKeyEvent) -> str:
#     for a,b in keymap.items():
#         if key.key() == a:
#             return b[1]

#     return key.text()

# def get_key(key: QKeyEvent) -> str:
#     for a,b in keymap.items():
#         if key.key() == a:
#             return b[0]

#     return key.text()

# def get_char(c: QKeyEvent) -> str:
#     for a, b in chars.items():
#         if  c.key() == a:
#             return b
#     return c.text()


errors = {
    QSerialPort.NoError: "No error",
    QSerialPort.DeviceNotFoundError: "Device not found",
    QSerialPort.PermissionError: "Permission denied",
    QSerialPort.OpenError: "Failed to open device",
    QSerialPort.NotOpenError: "Port not open",
    QSerialPort.WriteError: "Write fail",
    QSerialPort.ReadError: "Read fail",
    QSerialPort.ResourceError: "Resource error",
    QSerialPort.UnsupportedOperationError: "Unsupported operation",
    QSerialPort.TimeoutError: "Timeout",
    QSerialPort.UnknownError: "Unknown",
}


class Mode(enum.Enum):
    Normal = 0
    Echo = 1


class State(enum.Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    SUSPENDED = 2
    RECONNECTING = 3


class StateHandler:
    def __init__(self) -> None:
        self.state = State.DISCONNECTED

    def set_state(self, new_state):
        pass


class MpTerm(enum.Enum):
    # Display modes
    Ascii = "Ascii"
    Hex = "Hex"
    AsciiHex = "AsciiHex"
    Terminal = "Terminal"

    # Newline modes
    Nl = 0
    Cr = 1
    NlCr = 2


# Code ----------------------------------------------------------------------

about_html = f"""
<center><img src={App.ICON} width="54" height="54"></center>
<center><h2>{App.NAME}</h2></center>


      <table>
        <tr>
          <td> 
            <b>Version: </b>
          </td>
          <td>  
            {App.VERSION}
          </td>
        </tr>
        <tr>
          <td> 
            <b>Author: </b>
          </td>
          <td>  
            {App.AUTHOR}
          </td/
        </tr>
        <tr>
          <td> 
            <b>Email: </b>
          </td>
          <td>  
            </b><a href="{App.EMAIL}">{App.EMAIL}</a>
          </td/
        </tr>
        <tr> 
          <td>
            <b>Github: </b>
          </td>
          <td>  
            <a href="{App.HOME}">{App.HOME}</a>
          </td/
          </td>
        </tr>
      </table>

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
class mpProfile:
    alias: str = "default"
    port: str = ""
    bitrate: str = "38400"
    databits: str = "8"
    parity: str = "None"
    stopbits: str = "1"
    flowcontrol: str = "None"
    mode: str = MpTerm.Ascii.name

    key_list = [
        "alias",
        "port",
        "bitrate",
        "databits",
        "parity",
        "stopbits",
        "flowcontrol",
        "mode",
    ]
    filename: str = ""

    def set_member(self, key, dict):
        val = dict.get(key, getattr(self, key))
        logging.debug(f"{key} = {val}")
        setattr(self, key, val)

    def toJSON(self) -> dict:
        jsonDict = {}
        for key in self.key_list:
            jsonDict[key] = getattr(self, key)

        return jsonDict

    def fromJSON(self, jsonDict):
        for key in self.key_list:
            self.set_member(key, jsonDict)

    def write(self):
        with open(self.filename, "w") as outfile:
            json.dump(self.toJSON(), outfile, indent=4)

    def load(self):
        if not os.path.exists(self.filename):
            self.write()

        with open(self.filename, "r") as infile:
            jsd = json.load(infile)

        self.fromJSON(jsd)


class SerialPort:
    count: int

    def __init__(self) -> None:
        self.clear_counters()
        self.serial_port = QSerialPort()
        self.state = State.DISCONNECTED
        self.error = ""

        self.suspend_timer = QTimer()
        self.suspend_timer.setSingleShot(True)
        self.suspend_timer.timeout.connect(self.suspend_timeout)

        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(200)
        self.reconnect_timer.timeout.connect(self.reconnect_timeout)
        self.reconnect_timer.start()

    def read_str(self) -> str:
        data = self.serial_port.readAll()
        data_str = str(data, "utf-8")
        self.count = data.count()
        self.rxCnt += self.count
        return data_str

    def read(self):
        data = self.serial_port.readAll()
        self.count = data.count()
        self.rxCnt += self.count
        return data

    def name(self) -> str:
        return self.serial_port.portName()

    def open(self):
        if self.serial_port.isOpen():
            return

        res = self.serial_port.open(QIODevice.ReadWrite)
        if res:
            self.set_state(State.CONNECTED)
        else:
            err = self.serial_port.error()
            self.error = errors[err]
            logging.error(f"Failed to open serial port: {self.error}")

        return res

    def close(self) -> None:
        self.serial_port.close()
        self.state = State.DISCONNECTED

    def clear(self) -> None:
        if self.serial_port.isOpen():
            self.serial_port.clear()

    def clear_counters(self):
        self.rxCnt = 0
        self.txCnt = 0

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def send(self, data: bytearray):
        if self.serial_port.isOpen():
            res = self.serial_port.write(data)
            if res > 0:
                self.txCnt += res
            else:
                logging.error("Could not write data.")

    def set_state(self, newState: State, timeout=4000) -> None:

        if newState == State.SUSPENDED and self.state == State.CONNECTED:
            self.serial_port.close()
            self.state = State.SUSPENDED
            if timeout != -1:
                self.suspend_timer.start(timeout)

        if newState == State.DISCONNECTED:
            self.state = newState
            self.suspend_timer.stop()

        if newState in [
            State.CONNECTED,
            State.DISCONNECTED,
            State.RECONNECTING,
            State.DISCONNECTED,
        ]:
            self.state = newState

        # self.state = newState
        logging.debug(f"State: {self.state.name}")

    def suspend_timeout(self):
        if self.state == State.SUSPENDED:
            self.set_state(State.RECONNECTING)
            self.state = State.RECONNECTING
            logging.debug("Reconnecting port")

    def is_open(self) -> bool:
        return self.serial_port.isOpen()

    def reconnect_timeout(self):
        if self.state != State.RECONNECTING:
            return

        logging.debug("Reconnecting...")

        self.clear()

        if self.open():
            self.set_state(State.CONNECTED)
            self.error = ""
        else:
            err = self.serial_port.error()


class FormatHex:
    def __init__(self) -> None:
        self.index = 0
        self.max = 15
        self.end = "<br>"
        self.setMode(MpTerm.Ascii)

    def setMode(self, mode):
        self.mode = mode
        self.index = 0

    def clear(self):
        self.index = 0

    def _format_ascii_hex(self, data) -> str:
        s = ""
        for i in range(0, data.count()):
            byte = data.at(i)
            ch = int.from_bytes(byte, "big")
            cs = hex2str(ch)
            if len(cs) == 1:
                cs = f'"{cs}"'

            # if ch == 0x1b:
            #     s += "\n"
            #     self.index = 0

            # s += f"""<b>{chd:02x}</b> "{str(ch, "utf-8")}" """
            s += f"""<b>{ch:02x}</b> {cs:<3} """
            self.index += 1
            if self.index == self.max:
                s += self.end
                self.index = 0
        return s

    def _format_hex(self, data) -> str:
        s = ""
        for i in range(0, data.count()):
            ch = data.at(i)
            chd = int.from_bytes(ch, "big")
            s += f"{chd:02x} "
            self.index += 1
            if self.index == self.max:
                s += self.end
                self.index = 0
        return s

    def update(self, data) -> str:
        if self.mode == MpTerm.Hex:
            return self._format_hex(data)

        if self.mode == MpTerm.AsciiHex:
            return self._format_ascii_hex(data)

        return ""


class StyleS:
    normal = "color:Black; border:0"
    error = "color:Red; border:0"
    win = "border:0"
    # normal = "background-color:#3F84CB; color:#F7F9FC; border:0"
    # error = "background-color:#CC6633; color:#F7F9FC; border:0"


class MainForm(QMainWindow):

    # Handle windows close event
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.saveSettings()
        return super().closeEvent(a0)

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(QIcon(App.ICON))
        self.ui.statusbar.setStyleSheet(StyleS.normal)

        self.sp = SerialPort()
        self.sp.serial_port.readyRead.connect(self.read)
        self.updatePorts()

        self.terminal = TerminalWin(
            self.ui.centralwidget,
            sp=self.sp,
            init=f"""MpTerm Ver: <b>{App.VERSION}</b>\n""",
        )
        self.ui.horizontalLayout.insertWidget(1, self.terminal)

        self.formater = FormatHex()

        self.rxLabel = QLabel("")
        self.txLabel = QLabel("")
        self.stateLabel = QLabel("")
        self.ui.statusbar.addPermanentWidget(self.stateLabel, stretch=0)
        self.ui.statusbar.addPermanentWidget(self.rxLabel, stretch=0)
        self.ui.statusbar.addPermanentWidget(self.txLabel, stretch=0)

        # Statusbar button test
        # self.customSignal = QtCore.Signal()
        self.statusButton = QPushButton("XX")
        self.ui.statusbar.addPermanentWidget(self.statusButton, stretch=0)
        self.statusButton.clicked.connect(lambda: print("Button XX clicked"))

        self.ui.cbStopBits.addItem("1", QSerialPort.OneStop)
        self.ui.cbStopBits.addItem("1.5", QSerialPort.OneAndHalfStop)
        self.ui.cbStopBits.addItem("2", QSerialPort.TwoStop)
        self.ui.cbStopBits.setCurrentIndex(0)

        self.ui.cbBits.addItem("5", QSerialPort.Data5)
        self.ui.cbBits.addItem("6", QSerialPort.Data6)
        self.ui.cbBits.addItem("7", QSerialPort.Data7)
        self.ui.cbBits.addItem("8", QSerialPort.Data8)
        self.ui.cbBits.setCurrentIndex(3)

        self.ui.cbParity.addItem("None", QSerialPort.NoParity)
        self.ui.cbParity.addItem("Odd", QSerialPort.OddParity)
        self.ui.cbParity.addItem("Even", QSerialPort.EvenParity)
        self.ui.cbParity.setCurrentIndex(0)

        self.ui.cbFlowControl.addItem("None", QSerialPort.NoFlowControl)
        self.ui.cbFlowControl.addItem("Hardware", QSerialPort.HardwareControl)
        self.ui.cbFlowControl.addItem("Software", QSerialPort.SoftwareControl)
        self.ui.cbFlowControl.setCurrentIndex(0)

        self.ui.cbBitrate.addItem("300", 300)
        self.ui.cbBitrate.addItem("600", 600)
        self.ui.cbBitrate.addItem("1200", 1200)
        self.ui.cbBitrate.addItem("2400", 2400)
        self.ui.cbBitrate.addItem("4800", 4800)
        self.ui.cbBitrate.addItem("9600", 9600)
        self.ui.cbBitrate.addItem("19200", 19200)
        self.ui.cbBitrate.addItem("28400", 28400)
        self.ui.cbBitrate.addItem("57600", 57600)
        self.ui.cbBitrate.addItem("115200", 115200)
        self.ui.cbBitrate.setCurrentIndex(5)

        self.ui.cbNewline.addItem("nl", 0)
        self.ui.cbNewline.addItem("cr", 1)
        self.ui.cbNewline.addItem("cr+nl", 2)

        self.ui.cbDisplay.addItem("Ascii", MpTerm.Ascii)
        self.ui.cbDisplay.addItem("Hex", MpTerm.Hex)
        self.ui.cbDisplay.addItem("Hex + Ascii", MpTerm.AsciiHex)
        self.ui.cbDisplay.currentIndexChanged.connect(self.mode_change)

        self.ui.cbProfiles.addItem("Default", 0)
        self.ui.cbProfiles.addItem("115299", 2)
        self.ui.cbProfiles.addItem("New...", 3)
        self.ui.cbProfiles.hide()

        self.ui.cbRTS.clicked.connect(self.handle_rts)
        self.ui.cbDTR.clicked.connect(self.handle_dtr)

        # Send menu
        ctrlcAction = QAction("Ctrl-C (ETX)", self)
        ctrlcAction.triggered.connect(lambda: self.send_string(Esc.ETX))
        self.ui.menuSend.addAction(ctrlcAction)
        ctrlcAction = QAction("Break (NULL)", self)
        ctrlcAction.triggered.connect(lambda: self.send_string(Ascii.NULL))
        self.ui.menuSend.addAction(ctrlcAction)
        tabAction = QAction("Tab (0x09)", self)
        tabAction.triggered.connect(lambda: self.send_string(Ascii.TAB))
        self.ui.menuSend.addAction(tabAction)

        self.testMenu = self.ui.menuSend.addMenu("Tests")

        sendTestAction = QAction("Escape test", self)
        sendTestAction.triggered.connect(
            lambda: self.send_string(escape_attribute_test)
        )
        self.testMenu.addAction(sendTestAction)

        sendFlagAction = QAction("Flag SE", self)
        sendFlagAction.triggered.connect(lambda: self.send_string(flag))
        self.testMenu.addAction(sendFlagAction)

        colorAction = QAction("Color test", self)
        colorAction.triggered.connect(lambda: self.send_string(color_256_test()))
        self.testMenu.addAction(colorAction)

        self.colorMenu = self.ui.menuSend.addMenu("Colors")
        self.add_menu("Red", self.colorMenu, lambda: self.send_string(Esc.RED))
        self.add_menu("Green", self.colorMenu, lambda: self.send_string(Esc.GREEN))
        self.add_menu("Yellow", self.colorMenu, lambda: self.send_string(Esc.YELLOW))
        self.add_menu("Blue", self.colorMenu, lambda: self.send_string(Esc.BLUE))
        self.add_menu("Magenta", self.colorMenu, lambda: self.send_string(Esc.MAGENTA))
        self.add_menu("Cyan", self.colorMenu, lambda: self.send_string(Esc.CYAN))
        self.add_menu("White", self.colorMenu, lambda: self.send_string(Esc.WHITE))

        self.add_menu("Bg Red", self.colorMenu, lambda: self.send_string(Esc.ON_RED))
        self.add_menu(
            "Bg Green", self.colorMenu, lambda: self.send_string(Esc.ON_GREEN)
        )
        self.add_menu(
            "Bg Yellow", self.colorMenu, lambda: self.send_string(Esc.ON_YELLOW)
        )
        self.add_menu("Bg Blue", self.colorMenu, lambda: self.send_string(Esc.ON_BLUE))
        self.add_menu(
            "Bg Magenta", self.colorMenu, lambda: self.send_string(Esc.ON_MAGENTA)
        )
        self.add_menu("Bg Cyan", self.colorMenu, lambda: self.send_string(Esc.ON_CYAN))
        self.add_menu(
            "Bg White", self.colorMenu, lambda: self.send_string(Esc.ON_WHITE)
        )

        self.attrMenu = self.ui.menuSend.addMenu("Attributes")
        self.add_menu("Reset", self.attrMenu, lambda: self.send_string(Esc.ATTR_RESET))
        self.add_menu("Bold", self.attrMenu, lambda: self.send_string(Esc.ATTR_BOLD))
        self.add_menu(
            "Italic", self.attrMenu, lambda: self.send_string(Esc.ATTR_ITALIC)
        )
        self.add_menu("Dim", self.attrMenu, lambda: self.send_string(Esc.ATTR_DIM))
        self.add_menu(
            "Reverse", self.attrMenu, lambda: self.send_string(Esc.ATTR_REVERSE)
        )
        self.add_menu(
            "Underline", self.attrMenu, lambda: self.send_string(Esc.ATTR_UNDERLINE)
        )
        self.add_menu(
            "Crossed", self.attrMenu, lambda: self.send_string(Esc.ATTR_CROSSED)
        )

        # event slots
        self.ui.cbBitrate.activated.connect(self.set_sp)
        self.ui.cbStopBits.activated.connect(self.set_sp)
        self.ui.cbBits.activated.connect(self.set_sp)
        self.ui.cbParity.activated.connect(self.set_sp)
        self.ui.cbFlowControl.activated.connect(self.set_sp)
        self.ui.cbDisplay.activated.connect(self.set_sp)

        self.ui.actionNew.triggered.connect(self.new)
        self.ui.actionExit.triggered.connect(self.exitProgram)
        self.ui.actionClear.triggered.connect(self.actionClear)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionPortInfo.triggered.connect(self.portInfo)

        self.ui.pbOpen.pressed.connect(self.openPort)
        self.ui.pbSuspend.pressed.connect(self.suspend)

        self.cbMode = QComboBox(self.ui.centralwidget)
        self.ui.verticalLayout_4.insertWidget(1, self.cbMode)
        self.cbMode.addItem(Mode.Normal.name, Mode.Normal)
        self.cbMode.addItem(Mode.Echo.name, Mode.Echo)

        self.dtrLabel = QLabel("\u26D4 DTR")
        self.rtsLabel = QLabel("\u26D4 RTS")
        self.ui.verticalLayout_4.insertWidget(9, self.dtrLabel)
        self.ui.verticalLayout_4.insertWidget(9, self.rtsLabel)

        self.bpProgram = QPushButton("Program", self.ui.centralwidget)
        self.ui.verticalLayout_4.insertWidget(12, self.bpProgram)
        self.bpProgram.pressed.connect(self.program)

        self.loadSettings()

        self.mode_change()

        # Configure signal handler
        signal.signal(signal.SIGUSR1, self.signal_usr1)

        # Timers
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start()

        self.timer_5 = QTimer()
        self.timer_5.setInterval(200)
        self.timer_5.timeout.connect(self.timer_5_timeout)
        self.timer_5.start()

        self.ts = TerminalState()

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.program_data_available)
        self.process.finished.connect(self.program_finished)

        self.update_ui()

    # def keyPressEvent(self, a0: QKeyEvent) -> None:
    #     return super().keyPressEvent(a0)
    #     #print("Key")
    #     pass
    

    def add_menu(self, name, menu, function):
        action = QAction(name, self)
        menu.addAction(action)
        action.triggered.connect(function)

    def suspend(self):
        self.sp.set_state(State.SUSPENDED)
        self.update_ui()

    def program_data_available(self):
        data = self.process.readAllStandardOutput()
        # data = self.process.readAllStandardError()
        #self.process.re
        data_str = str(data, "utf-8")
        print(data_str)
        self.terminal.apps(data_str)
        self.terminal.scroll_down()
        self.update_ui()

    def program_finished(self):
        logging.debug("External program finnished executing")
        if self.sp.state == State.SUSPENDED:
            self.sp.set_state(State.RECONNECTING)

        self.update_ui()

    def program(self):
        if self.sp.state == State.SUSPENDED:
            return

        if self.sp.state == State.CONNECTED:
            self.sp.set_state(State.SUSPENDED, timeout=-1)

        # self.process.start("bpdev attr")
        # self.process.start("avrdude 2>&1")
        self.process.start("wget")
        logging.debug("Runing external program")
        self.update_ui()
        self.terminal.scroll_down()

    def signal_usr1(self, signum, frame) -> None:
        logging.debug("USR1 signal received")
        self.sp.set_state(State.SUSPENDED)

    def timer_5_timeout(self):
        if self.sp.state == State.SUSPENDED:
            rt = self.sp.suspend_timer.remainingTime()
            self.message(f"Port suspended. Time left {rt / 1000:.0f}")

        #        pins = self.sp.serial_port.PinoutSignal()

        self.update_ui()

    def about(self) -> None:
        AboutDialog.about()

    # def port_handler(self):
    #     if self.sp.state == State.DISCONNECTED:
    #         pass

    def port_handler(self):
        portNames = [x.portName() for x in QSerialPortInfo.availablePorts()]

        # Check if current port is still connecter (USB to serial adapters), if not close port
        if self.sp.is_open():
            if self.sp.name() not in portNames:
                self.sp.close()
                self.messageError(f"Port {self.sp.name()} no longer available.")

        # Update list of serialports in combobox
        for x in range(self.ui.cbPort.count()):
            if self.ui.cbPort.itemText(x) not in portNames:
                self.ui.cbPort.removeItem(x)
            else:
                portNames.remove(self.ui.cbPort.itemText(x))

        for x in portNames:
            self.ui.cbPort.addItem(x)

    def timerEvent(self):
        self.port_handler()

    def update_ui(self):

        if self.sp.state == State.DISCONNECTED:
            self.setWindowTitle("MpTerm")
            self.ui.pbOpen.setText("Open")
            self.ui.cbPort.setEnabled(True)
        else:
            self.setWindowTitle(
                f"MpTerm  /dev/{self.ui.cbPort.currentText()} {self.ui.cbBitrate.currentText()}"
            )
            self.ui.pbOpen.setText("Close")
            self.ui.cbPort.setEnabled(False)

        self.rxLabel.setText(
            f'<span style="color:Black">RX:</span> <span style="color:Purple">{self.sp.rxCnt:06d}</span> '
        )
        self.txLabel.setText(
            f'<span style="color:Black">TX:</span> <span style="color:Purple">{self.sp.txCnt:06d}</span> '
        )

        states = {
            State.DISCONNECTED: f"""<span style="color:Black">Disconected</span>""",
            State.CONNECTED: f"""<span style="color:Green">Connected  </span>""",
            State.SUSPENDED: f"""<span style="color:Red">Suspended </span>""",
            State.RECONNECTING: f"""<span style="color:Magenta">Reconnecting</span>""",
        }
        self.stateLabel.setText(f"{states[self.sp.state]}")

        if self.sp.serial_port.isDataTerminalReady():
            self.dtrLabel.setText("\u26AA  DTR")
        else:
            self.dtrLabel.setText("\u26AB  DTR")

        if self.sp.serial_port.isRequestToSend():
            self.rtsLabel.setText("\u26AA  RTS")
        else:
            self.rtsLabel.setText("\u26AB  RTS")

        # logging.debug(f"DTR: {self.sp.serial_port.isDataTerminalReady()}  RTS: {self.sp.serial_port.isRequestToSend()}")

    def updatePorts(self):
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.ui.cbPort.addItem(port.portName())

    def handle_dtr(self):
        # self.ui.cbDTR.clicked.connect(self.handle_dtr)
        logging.debug("DTR")
        if self.ui.cbDTR.isChecked():
            self.ui.cbDTR.setChecked(True)
            self.sp.serial_port.setDataTerminalReady(True)
        else:
            self.ui.cbDTR.setChecked(False)
            self.sp.serial_port.setDataTerminalReady(False)

    def handle_rts(self):
        logging.debug("RTS")
        if self.ui.cbRTS.isChecked():
            self.ui.cbRTS.setChecked(True)
            self.sp.serial_port.setRequestToSend(True)
        else:
            self.ui.cbRTS.setChecked(False)
            self.sp.serial_port.setRequestToSend(False)

    def syncChanged(self):
        try:
            self.sync = int(self.ui.leSyncString.text(), 16)

            if self.sync > 255 or self.sync < 0:
                self.sync = -1
                self.ui.lSync.setText('<font color="Red">Sync string')
            else:
                self.ui.lSync.setText('<font color="Black">Sync string')

        except:
            self.sync = -1
            text = self.ui.leSyncString.text()
            #            print(len(text), 'Text: '+text)
            if len(text) > 0:
                self.ui.lSync.setText('<font color="Red">Sync string')
            else:
                self.ui.lSync.setText('<font color="Black">Sync string')
        return

    def actionClear(self):
        self.terminal.clear()
        self.formater.clear()
        self.sp.clear_counters()
        self.update()

    def _message(self, msg):
        self.ui.statusbar.showMessage(msg, 4000)
        self.ui.statusbar.show

    # Show message in status bar
    def message(self, msg):
        # self.ui.statusbar.setStyleSheet("color: black")
        self.ui.statusbar.setStyleSheet(StyleS.normal)
        self._message(msg)
        
        logging.debug(msg)

    # Show error message in status bar
    def messageError(self, msg):
        self.ui.statusbar.setStyleSheet(StyleS.error)
        self._message(msg)
        logging.error(msg)

    def mode_change(self):
        self.terminal.clear()
        self.formater.setMode(self.ui.cbDisplay.currentData())
        logging.debug(f"Setting display mode {self.ui.cbDisplay.currentData()}")

    def appendHtml(self, str):
        # move cursor to end of buffer
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertHtml(str)

    def read(self):

        data = self.sp.read()
        data_str = str(data, "utf-8")

        db = (
            data_str.replace("\x1b", "\\e")
            .replace("\x0a", "\\n")
            .replace("\x0d", "\\r")
            .replace("\x08", "\\b")
        )
        logging.debug(f"Data received: {self.sp.count} \"{db}\"")

        DisplayMode = self.ui.cbDisplay.currentData()

        if DisplayMode == MpTerm.Ascii:  # Standard ascii display mode
            self.terminal.apps(data_str)

        if DisplayMode != MpTerm.Ascii:  # Hexadecimal display mode
            self.terminal.apps(self.formater.update(data))

        self.terminal.scroll_down()
        self.update_ui()

        if self.cbMode.currentData() == Mode.Echo:
            self.sp.send(data)

    def send(self, data: bytearray):
        if self.sp.is_open():
            res = self.sp.serial_port.write(data)
            if res > 0:
                self.sp.txCnt += res
            else:
                logging.error("Could not write data.")
            self.update_ui()

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def openPort(self):
        if self.sp.is_open():
            self.sp.close()
            self.update_ui()
            return

        self.init_port()
        self.sp.clear()
        res = self.sp.open()
        if res:
            self.message("Opening port: /dev/" + self.ui.cbPort.currentText())
        else:
            err = self.sp.serial_port.error()
            self.messageError(
                f"Failed to open port /dev/{self.ui.cbPort.currentText()}. {errors[err]}"
            )

        self.update_ui()

    def init_port(self):
        self.set_port()
        self.set_sp()

    def set_port(self):
        self.sp.serial_port.setPortName("/dev/" + self.ui.cbPort.currentText())

    def set_sp(self):
        self.sp.serial_port.setBaudRate(self.ui.cbBitrate.currentData())
        self.sp.serial_port.setStopBits(self.ui.cbStopBits.currentData())
        self.sp.serial_port.setDataBits(self.ui.cbBits.currentData())
        self.sp.serial_port.setParity(self.ui.cbParity.currentData())
        self.sp.serial_port.setFlowControl(self.ui.cbFlowControl.currentData())

    def setCbText(self, cb, txt):
        a = cb.findText(txt)
        if a == -1:
            cb.setCurrentIndex(0)
        else:
            cb.setCurrentIndex(a)

    def setCbData(self, cb, data):
        a = cb.findData(data)
        if a == -1:
            cb.setCurrentIndex(0)
        else:
            cb.setCurrentIndex(a)

    def saveSettings(self):
        self.prof.port = self.ui.cbPort.currentText()
        self.prof.bitrate = self.ui.cbBitrate.currentText()
        self.prof.databits = self.ui.cbBits.currentText()
        self.prof.stopbits = self.ui.cbStopBits.currentText()
        self.prof.parity = self.ui.cbParity.currentText()
        self.prof.flowcontrol = self.ui.cbFlowControl.currentText()
        self.prof.mode = self.ui.cbDisplay.currentData().name

        # self.prof.sync = self.ui.leSyncString.text()
        self.prof.write()

    def loadSettings(self):

        # Handle settings
        self.prof = mpProfile(filename=mp_settings)
        self.prof.load()

        self.ui.cbPort.setCurrentText(self.prof.port)
        self.ui.cbBitrate.setCurrentText(self.prof.bitrate)
        self.ui.cbStopBits.setCurrentText(self.prof.stopbits)
        self.ui.cbBits.setCurrentText(self.prof.databits)
        self.ui.cbParity.setCurrentText(self.prof.parity)
        self.ui.cbFlowControl.setCurrentText(self.prof.flowcontrol)

        idx = self.ui.cbDisplay.findData(MpTerm(self.prof.mode))
        self.ui.cbDisplay.setCurrentIndex(idx)

        # self.ui.leSyncString.setText(prof.sync)

    def exitProgram(self, e):
        self.sp.serial_port.close()
        self.saveSettings()
        self.close()

    def ss(self, str):
        print(len(str))
        nstr = str
        for i in range(1, 16 - len(str)):
            nstr += "&nbsp;"
        return nstr

    def appendInfo(self, desc, data):
        self.appendHtml(f"<b>{self.ss(desc)}</b><code><font color='Green'>{data}<br>")

    def portInfo(self):
        if not self.sp.state == State.DISCONNECTED:
            return
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.appendInfo("Port:", port.portName())
            self.appendInfo("Location:", port.systemLocation())
            self.appendInfo("Vendor id:", str(port.vendorIdentifier()))
            self.appendInfo("Product id:", str(port.productIdentifier()))
            self.appendInfo("Manufacturer:", port.manufacturer())
            self.appendInfo("Description:", port.description())
            self.appendHtml("<br>")

    def new(self):
        subprocess.Popen([f"{self_dir}/mpterm.py"], shell=False)


def list_ports():
    spi = QSerialPortInfo.availablePorts()
    for p in spi:
        print(f"{p.portName():<10}{p.description():<20}{p.systemLocation()}")


def main():
    logging_format = "[%(levelname)s] %(lineno)d %(funcName)s() : %(message)s"

    # options parsing
    parser = argparse.ArgumentParser(
        prog=App.NAME, add_help=True, description=App.DESCRIPTION
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {App.VERSION}"
    )
    parser.add_argument("--info", action="store_true", help="Information about script")
    parser.add_argument(
        "--suspend", action="store_true", help="Send signal to suspend port temporary"
    )
    parser.add_argument("--list", action="store_true", help="List serialports")
    parser.add_argument("--build", action="store_true", help="Build ui code")
    parser.add_argument("--debug", action="store_true", help="Activate debug printout")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format=logging_format, level=logging.DEBUG)

    if args.build:
        os.system("pyuic5 mpTerminal.ui -o ui_MainWindow.py")
        sys.exit()

    if args.list:
        list_ports()
        sys.exit()

    if args.suspend:
        with os.popen(
            "ps aux | grep mpterm.py | grep -v -e 'grep' -e '--suspend'"
        ) as f:
            res = f.readlines()

        for r in res:
            pid = int(r.split()[1])
            logging.debug(f"Sending suspend signal to process pid={pid}")
            os.kill(pid, 10)

        sys.exit()

    app = QApplication(sys.argv)
    app.setStyle(
        "Fusion"
    )  # 'cleanlooks', 'gtk2', 'cde', 'motif', 'plastique', 'qt5ct-style', 'Windows', 'Fusion'
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    mainForm = MainForm()
    mainForm.show()
    sys.exit(app.exec_())


# Main program handle
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
