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
# master*
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

from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice, QProcess, QEvent, QObject
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
    QToolButton,
    QComboBox,
    QMessageBox,
    QWidget,
    QFileDialog,
)

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from ui_MainWindow import Ui_MainWindow
from dataclasses import dataclass
from escape import (
    Escape,
    Ascii,
    TerminalState,
    flag,
    escape_attribute_test,
    color_256_test,
    hex2str,
)
from qterminalwidget import QTerminalWidget, get_key, get_description
from serialport import SerialPort, State

from aboutdialog import AboutDialog

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

SUSPEND_TIMEOUT = 8000

# Definitions ---------------------------------------------------------------


class Mode(enum.Enum):
    Normal = 0
    Echo = 1


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

# Code ----------------------------------------------------------------------


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

        self.serialPort = SerialPort()
        self.serialPort.readyRead.connect(self.read)
        self.updatePorts()

        self.terminal = QTerminalWidget(
            self.ui.centralwidget, serialPort=self.serialPort
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
        # self.statusButton = QPushButton("XX")
        # self.ui.statusbar.addPermanentWidget(self.statusButton, stretch=0)
        # self.statusButton.clicked.connect(lambda: print("Button XX clicked"))

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
        self.ui.cbProfiles.addItem("115200", 2)
        self.ui.cbProfiles.addItem("New...", 3)
        self.ui.cbProfiles.hide()

        self.ui.cbRTS.clicked.connect(self.handle_rts)
        self.ui.cbDTR.clicked.connect(self.handle_dtr)

        # Send menu
        ctrlcAction = QAction("Ctrl-C (ETX)", self)
        ctrlcAction.triggered.connect(lambda: self.send_string(Escape.ETX))
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
        self.add_action("Red", self.colorMenu, lambda: self.send_string(Escape.RED))
        self.add_action("Green", self.colorMenu, lambda: self.send_string(Escape.GREEN))
        self.add_action(
            "Yellow", self.colorMenu, lambda: self.send_string(Escape.YELLOW)
        )
        self.add_action("Blue", self.colorMenu, lambda: self.send_string(Escape.BLUE))
        self.add_action(
            "Magenta", self.colorMenu, lambda: self.send_string(Escape.MAGENTA)
        )
        self.add_action("Cyan", self.colorMenu, lambda: self.send_string(Escape.CYAN))
        self.add_action("White", self.colorMenu, lambda: self.send_string(Escape.WHITE))

        self.add_action(
            "Bg Red", self.colorMenu, lambda: self.send_string(Escape.BG_RED)
        )
        self.add_action(
            "Bg Green", self.colorMenu, lambda: self.send_string(Escape.BG_GREEN)
        )
        self.add_action(
            "Bg Yellow", self.colorMenu, lambda: self.send_string(Escape.BG_YELLOW)
        )
        self.add_action(
            "Bg Blue", self.colorMenu, lambda: self.send_string(Escape.BG_BLUE)
        )
        self.add_action(
            "Bg Magenta", self.colorMenu, lambda: self.send_string(Escape.BG_MAGENTA)
        )
        self.add_action(
            "Bg Cyan", self.colorMenu, lambda: self.send_string(Escape.BG_CYAN)
        )
        self.add_action(
            "Bg White", self.colorMenu, lambda: self.send_string(Escape.BG_WHITE)
        )

        self.attrMenu = self.ui.menuSend.addMenu("Attributes")
        self.add_action("Reset", self.attrMenu, lambda: self.send_string(Escape.RESET))
        self.add_action("Bold", self.attrMenu, lambda: self.send_string(Escape.BOLD))
        self.add_action(
            "Italic", self.attrMenu, lambda: self.send_string(Escape.ITALIC)
        )
        self.add_action("Dim", self.attrMenu, lambda: self.send_string(Escape.DIM))
        self.add_action(
            "Reverse", self.attrMenu, lambda: self.send_string(Escape.REVERSE)
        )
        self.add_action(
            "Underline", self.attrMenu, lambda: self.send_string(Escape.UNDERLINE)
        )
        self.add_action(
            "Crossed", self.attrMenu, lambda: self.send_string(Escape.CROSSED)
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
        self.ui.actionAbout.triggered.connect(
            lambda: AboutDialog.about(App.NAME, about_html)
        )
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

        self.bpPause = QPushButton("Pause", self.ui.centralwidget)
        self.ui.verticalLayout_4.insertWidget(12, self.bpPause)
        self.bpPause.pressed.connect(self.pause)

        # self.pMenu = QMenu("X")
        # self.add_action("AA",self.pMenu, self.pause)
        # self.bpPause.setMenu(self.pMenu)

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

        self.isPaused = False

        # self.terminal.insert(f"""MpTerm Ver: <b>{App.VERSION}</b><br><br>""")
        self.terminal.apps(f"""MpTerm Ver: <b>{App.VERSION}</b><br><br>""")

        self.update_ui()
        self.init_port()
        # testAction = QAction("Testactopm", self)
        # testAction.triggered.connect(lambda: print("TestAction"))
        # self.terminal.addAction(testAction)
        # self.terminal.keyPressEvent.connect(self.key)

        #self.installEventFilter(self)
        self.terminal.installEventFilter(self)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        logging.debug(f"  {e.key():x}  {get_description(e)}")
        self.serialPort.send_string(get_key(e))

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        key2key = {
            Qt.Key_Tab: Ascii.TAB,
            Qt.Key_Left: Escape.BACK,
            Qt.Key_Right: Escape.FORWARD,
            Qt.Key_Up: Escape.UP,
            Qt.Key_Down: Escape.DOWN,
            Qt.Key_Delete: Escape.KEY_DELETE,
            Qt.Key_Space: " ",
        }
        #logging.debug(f"Event: {event}")
                
        # if event == Qt.Key_CTR
        
        if event.type() == QEvent.KeyPress:
            #logging.debug(f"Keypress Event: {event}")
            keyEvent = QKeyEvent(event)
            if keyEvent.key() in key2key:
                logging.debug(f"Key:{keyEvent.key()}")
                self.serialPort.send_string(key2key[keyEvent.key()])
                return True
            else:
                return False
        return False

        # return super().eventFilter(obj, event)

    # def key(self, e: QKeyEvent) -> None:
    #     # logging.debug(f"  {e.key():x}  {get_description(e)}")
    #     # self.sp.send_string(get_key(e))
    #     print("Keypressed")

    def add_action(self, name, menu, function) -> QAction:
        action = QAction(name, self)
        menu.addAction(action)
        action.triggered.connect(function)
        return action

    def pause(self):
        if self.isPaused:
            self.isPaused = False
            self.bpPause.setText("Pause")
        else:
            self.isPaused = True
            self.bpPause.setText("Paused")

    def suspend(self):
        self.serialPort.set_state(State.SUSPENDED, timeout = SUSPEND_TIMEOUT)
        self.update_ui()

    def program_data_available(self):
        data = self.process.readAllStandardOutput()
        logging.debug("Program received data")
        # data = self.process.readAllStandardError()
        # self.process.re
        data_str = str(data, "utf-8")
        print(data_str)
        self.terminal.apps(data_str)
        self.terminal.scroll_down()
        self.update_ui()

    def program_finished(self):
        logging.debug("External program finnished executing")
        self.terminal.append_html("<br>")
        if self.serialPort.state == State.SUSPENDED:
            self.serialPort.set_state(State.RECONNECTING)

        self.update_ui()

    def program(self):
        if self.serialPort.state == State.SUSPENDED:
            return

        if self.serialPort.state == State.CONNECTED:
            self.serialPort.set_state(State.SUSPENDED, timeout=-1)
        self.terminal.append_html("<br>")
        # self.process.start("ls -l")
        # self.process.start("bpdev attr")
        # self.process.start("bpexample shade")
        self.process.start("avrdude")
        # self.process.start("mpt ard 2>&1")
        # self.process.

        logging.debug("Runing external program")
        self.update_ui()
        self.terminal.scroll_down()

    def signal_usr1(self, signum, frame) -> None:
        logging.debug("USR1 signal received")
        self.suspend()
        #self.serialPort.set_state(State.SUSPENDED)

    def timer_5_timeout(self):
        if self.serialPort.state == State.SUSPENDED:
            rt = self.serialPort.suspend_timer.remainingTime()
            self.message(f"Port suspended. Time left {rt / 1000:.0f}")

        self.update_ui()

    def port_handler(self) -> None:
        portNames = [x.portName() for x in QSerialPortInfo.availablePorts()]

        # Check if current port is still connecter (USB to serial adapters), if not close port
        if self.serialPort.isOpen():
            if self.serialPort.portName() not in portNames:
                self.serialPort.close()
                self.messageError(f"Port {self.serialPort.name()} no longer available.")

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

        if self.serialPort.state == State.DISCONNECTED:
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
            f'<span style="color:Black">RX:</span> <span style="color:Purple">{self.serialPort.rxCnt:06d}</span> '
        )
        self.txLabel.setText(
            f'<span style="color:Black">TX:</span> <span style="color:Purple">{self.serialPort.txCnt:06d}</span> '
        )

        states = {
            State.DISCONNECTED: f"""<span style="color:Black">Disconected</span>""",
            State.CONNECTED: f"""<span style="color:Green">Connected  </span>""",
            State.SUSPENDED: f"""<span style="color:Red">Suspended </span>""",
            State.RECONNECTING: f"""<span style="color:Magenta">Reconnecting</span>""",
        }
        self.stateLabel.setText(f"{states[self.serialPort.state]}")

        if self.serialPort.isDataTerminalReady():
            self.dtrLabel.setText("\u26AA  DTR")
        else:
            self.dtrLabel.setText("\u26AB  DTR")

        if self.serialPort.isRequestToSend():
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
            self.serialPort.setDataTerminalReady(True)
        else:
            self.ui.cbDTR.setChecked(False)
            self.serialPort.setDataTerminalReady(False)

    def handle_rts(self):
        logging.debug("RTS")
        if self.ui.cbRTS.isChecked():
            self.ui.cbRTS.setChecked(True)
            self.serialPort.setRequestToSend(True)
        else:
            self.ui.cbRTS.setChecked(False)
            self.serialPort.setRequestToSend(False)

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
        self.serialPort.clear_counters()
        self.update()

    def _message(self, msg):
        self.ui.statusbar.showMessage(msg, 4000)
        self.ui.statusbar.show

    # Show message in status bar
    def message(self, msg):
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
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.append_html(str)

    def read(self):

        data = self.serialPort.read()
        data_str = str(data, "utf-8")

        db = Escape.to_str(data_str)

        logging.debug(f'Data received: {len(data)} "{db}"')

        if self.isPaused:
            return

        DisplayMode = self.ui.cbDisplay.currentData()

        if DisplayMode == MpTerm.Ascii:  # Standard ascii display mode
            self.terminal.apps(data_str)

        if DisplayMode != MpTerm.Ascii:  # Hexadecimal display mode
            self.terminal.apps(self.formater.update(data))

        self.terminal.scroll_down()
        self.update_ui()

        if self.cbMode.currentData() == Mode.Echo:
            self.serialPort.send(data)

    def send(self, data: bytearray):
        if self.serialPort.isOpen():
            res = self.serialPort.serial_port.write(data)
            if res > 0:
                self.serialPort.txCnt += res
            else:
                logging.error("Could not write data.")
            self.update_ui()

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def openPort(self):
        if self.serialPort.isOpen():
            self.serialPort.close()
            self.update_ui()
            return

        self.serialPort.clear()
        self.init_port()
        res = self.serialPort.open()
        if res:
            self.message(
                f"Opening port: /dev/{self.serialPort.portName()} {self.serialPort.baudRate()}"
            )
        else:
            self.messageError(
                f"Failed to open port /dev/{self.serialPort.portName()}. {self.serialPort.error()}"
            )

        self.update_ui()

    def init_port(self):
        self.set_port()
        self.set_sp()

    def set_port(self):
        self.serialPort.setPortName(f"/dev/{self.ui.cbPort.currentText()}")

    def set_sp(self):
        br = self.ui.cbBitrate.currentData()
        self.serialPort.setBaudRate(self.ui.cbBitrate.currentData())
        self.serialPort.setStopBits(self.ui.cbStopBits.currentData())
        self.serialPort.setDataBits(self.ui.cbBits.currentData())
        self.serialPort.setParity(self.ui.cbParity.currentData())
        self.serialPort.setFlowControl(self.ui.cbFlowControl.currentData())
        logging.debug(self.ui.cbBitrate.currentData())

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

    def loadSetting(self, cb, setting):
        idx = cb.findText(setting)
        if idx != -1:
            cb.setCurrentIndex(idx)

    def loadSettings(self):

        # Handle settings
        self.prof = mpProfile(filename=mp_settings)
        self.prof.load()

        # idx = self.ui.cbBitrate.findText(self.prof.bitrate)
        # if idx != -1:
        #     self.ui.cbBitrate.setCurrentIndex(idx)
        self.loadSetting(self.ui.cbBitrate, self.prof.bitrate)

        # self.ui.cbBitrate.setCurrentText(self.prof.bitrate)
        # self.ui.cbPort.setCurrentText(self.prof.port)
        # self.ui.cbStopBits.setCurrentText(self.prof.stopbits)
        # self.ui.cbBits.setCurrentText(self.prof.databits)
        # self.ui.cbParity.setCurrentText(self.prof.parity)
        # self.ui.cbFlowControl.setCurrentText(self.prof.flowcontrol)
        self.loadSetting(self.ui.cbBitrate, self.prof.bitrate)
        self.loadSetting(self.ui.cbPort, self.prof.port)
        self.loadSetting(self.ui.cbStopBits, self.prof.stopbits)
        self.loadSetting(self.ui.cbBits, self.prof.databits)
        self.loadSetting(self.ui.cbParity, self.prof.parity)
        self.loadSetting(self.ui.cbFlowControl, self.prof.flowcontrol)

        idx = self.ui.cbDisplay.findData(MpTerm(self.prof.mode))
        self.ui.cbDisplay.setCurrentIndex(idx)

    def exitProgram(self, e):
        self.serialPort.close()
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
        # if not self.sp.state == State.DISCONNECTED:
        #     return
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
    #logging.basicConfig(format=logging_format, level=logging.DEBUG)

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
    # parser.add_argument("--build", action="store_true", help="Build ui code")
    parser.add_argument("--debug", action="store_true", help="Activate debug printout")
    parser.add_argument(
        "--program", action="store", type=str, help="Program to run", default=""
    )

    args = parser.parse_args()

    #if args.debug:
        #logging.setLevel(logging.DEBUG)
        

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
    mainForm.args = args
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
