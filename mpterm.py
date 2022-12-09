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

from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice
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
    QMessageBox,
    QWidget,
    QFileDialog,
)

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from ui_MainWindow import Ui_MainWindow
from dataclasses import dataclass
from escape import Esc, Ascii, TerminalState
from terminalwin import TerminalWin

import AboutDialogXX

# Settings ------------------------------------------------------------------

# Absolute path to script itself
self_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

class App:
    NAME = "mpterm"
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

chars = {  0x00:"NULL",
           0x01:"SOH",
           0x02:"STX",
           0x03:"ETX",
           0x04:"EOT",
           0x05:"ENQ",
           0x06:"ACK",
           0x07:"BEL",
           0x08:"BS",
           0x09:"TAB",
           0x0A:"LF",
           0x0B:"VT",
           0x0C:"FF",
           0x0D:"CR",
           0x0E:"SO",
           0x0F:"SI",
           0x10:"DLE",
           0x11:"DC1",
           0x12:"DC2",
           0x13:"DC3",
           0x14:"DC4",
           0x15:"NAK",
           0x16:"SYN",
           0x17:"ETB",
           0x18:"CAN",
           0x19:"EM",
           0x1A:"SUB",
           0x1B:"ESC",
           0x1C:"FS",
           0x1D:"GS",
           0x1E:"RS",
           0x1F:"US"
}

keys = { Qt.Key_Enter:("\n", "Enter"), 
         Qt.Key_Return:("\n", "Return"), 
         Qt.Key_Escape:("", "Escape"), 
         Qt.Key_Delete:("", "Delete"), 
         Qt.Key_Left:("", "Left"),
         Qt.Key_Right:("", "Right"),
         Qt.Key_Up:("", "Up"),
         Qt.Key_Down:("", "Down"),
         Qt.Key_Insert:("", "Insert"),
         Qt.Key_Backspace:("", "Backspace"),
         Qt.Key_Home:("", "Home"),
         Qt.Key_End:("", "End"),
         Qt.Key_PageDown:("", "Page down"),
         Qt.Key_PageUp:("", "Page up"),
         Qt.Key_F1:("\x09", "F1"),
         Qt.Key_F2:("", "F2"),
         Qt.Key_F3:("", "F3"),
         Qt.Key_F4:("", "F4"),
         Qt.Key_F5:("", "F5"),
         Qt.Key_F6:("", "F6"),
         Qt.Key_F7:("", "F7"),
         Qt.Key_F8:("", "F8"),
         Qt.Key_F9:("", "F9"),
         Qt.Key_F10:("", "F10"),
         Qt.Key_F11:("", "F11"),
         Qt.Key_F12:("", "F12"),
         Qt.Key_Control:("", "Control"),
         Qt.Key_Shift:("", "Shift"),
         Qt.Key_Alt:("", "Alt"),
         Qt.Key_AltGr:("", "Alt Gr"),
         Qt.Key_Space:(" ", "Space"),
         Qt.Key_Print:("", "Print"),
         Qt.Key_ScrollLock:("", "Scroll lock"),
         Qt.Key_CapsLock:("", "Caps lock"),
         Qt.Key_Pause:("", "Pause"),
         Qt.Key_Tab:(Ascii.TAB, "Tab")
} 


def get_description(key: QKeyEvent) -> str:
    for a,b in keys.items():
        if key.key() == a:
            return b[1]

    return key.text()


def get_key(key: QKeyEvent) -> str:
    for a,b in keys.items():
        if key.key() == a:
            return b[0]

    return key.text()


def get_char(c: QKeyEvent) -> str:
    for a, b in chars.items():
        if  c.key() == a:
            return b
    return c.text()


errors = {
    QSerialPort.NoError:"No error",
    QSerialPort.DeviceNotFoundError:"Device not found",
    QSerialPort.PermissionError:"Permission denied",
    QSerialPort.OpenError:"Failed to open device",
    QSerialPort.NotOpenError:"Port not open",
    QSerialPort.WriteError:"Write fail",
    QSerialPort.ReadError:"Read fail",
    QSerialPort.ResourceError:"Resource error",
    QSerialPort.UnsupportedOperationError:"Unsupported operation",
    QSerialPort.TimeoutError:"Timeout",
    QSerialPort.UnknownError:"Unknown",  
}


class State(enum.Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    SUSPENDED = 2
    RECONNECTING = 3

class MpTerm(enum.Enum):
    # Display modes
    Ascii = 0
    Hex = 1
    AsciiHex = 2
    Terminal = 3

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

    filename: str =""
    
    def toJSON(self) -> dict:
        jsonDict={}
        jsonDict["alias"] = self.alias
        jsonDict["port"] = self.port
        jsonDict["bitrate"] = self.bitrate
        jsonDict["databits"] = self.databits
        jsonDict["parity"] = self.parity
        jsonDict["stopbits"] = self.stopbits
        jsonDict["flowcontrol"] = self.flowcontrol
        return jsonDict

    def fromJSON(self, jsonDict):
        self.alias = jsonDict["alias"] 
        self.port = jsonDict["port"] 
        self.bitrate = jsonDict["bitrate"] 
        self.databits = jsonDict["databits"]
        self.parity = jsonDict["parity"] 
        self.stopbits = jsonDict["stopbits"]
        self.flowcontrol = jsonDict["flowcontrol"] 

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
    def __init__(self) -> None:
        self.clear_counters()
        self.serial_port = QSerialPort()

        # Initiate terminal state
        self.state = State.DISCONNECTED

        self.suspend_timer = QTimer()
        self.suspend_timer.setSingleShot(True)
        self.suspend_timer.timeout.connect(self.suspend_timeout)
        
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(200)
        #self.reconnect_timer.timeout.connect(self.timer_5_timeout)
        self.reconnect_timer.start()

    def name(self) -> str:
        return self.serial_port.portName()

    def open(self, port):
        res = self.serial_port.open(QIODevice.ReadWrite)
        if res:
            self.state = State.CONNECTED
        else:
            err = self.serial_port.error()
            logging.error(errors[err])
            
        return res
    
    def close(self) -> None:
        self.state = State.DISCONNECTED
        self.serial_port.close()

    def clear_counters(self):
        self.rxCnt = 0
        self.txCnt = 0

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def send(self, data: bytearray):
        if self.serial_port.isOpen():
            res = self.serial_port.write(data)
            if res >0: 
                self.txCnt += res
            else:
                logging.error("Could not write data.")

    def suspend(self):
        if self.state == State.CONNECTED:
            self.serial_port.close()
            self.state = State.SUSPENDED
            self.suspend_timer.start(4000)
            logging.debug("Suspending port")

    def suspend_timeout(self):
        if self.state == State.SUSPENDED:
            self.state = State.RECONNECTING 
            logging.debug("Reconnecting port")

    def is_open(self) -> bool:
        return self.serial_port.isOpen()
            

class MainForm(QMainWindow):

    # Handle windows close event
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.saveSettings()
        return super().closeEvent(a0)
    
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sp = SerialPort()
        self.sp.serial_port.readyRead.connect(self.read)
        
        self.updatePorts()

        self.terminal = TerminalWin(self.ui.centralwidget, sp = self.sp)
        
        self.ui.horizontalLayout.insertWidget(1, self.terminal) 

        # Set window icon
        self.setWindowIcon(QIcon(App.ICON))

        self.rxLabel = QLabel("")
        self.txLabel = QLabel("")
        self.stateLabel = QLabel("State")
        self.ui.statusbar.addPermanentWidget(self.stateLabel, stretch=0)
        self.ui.statusbar.addPermanentWidget(self.rxLabel, stretch=0)
        self.ui.statusbar.addPermanentWidget(self.txLabel, stretch=0)


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
        #self.ui.cbDisplay.addItem("Hex + Ascii", MpTerm.AsciiHex)

        self.ui.cbProfiles.addItem("Default", 0)
        self.ui.cbProfiles.addItem("115299", 2)
        self.ui.cbProfiles.addItem("New...", 3)
        self.ui.cbProfiles.hide()

        self.ui.cbRTS.clicked.connect(self.handle_rts)

        # Send menu
        ctrlcAction = QAction("Ctrl-c", self)
        ctrlcAction.triggered.connect(lambda: self.send_string(Esc.ETX))
        self.ui.menuSend.addAction(ctrlcAction)

        # event slots
        self.ui.cbBitrate.activated.connect(self.set_sp)
        self.ui.cbStopBits.activated.connect(self.set_sp)
        self.ui.cbBits.activated.connect(self.set_sp)
        self.ui.cbParity.activated.connect(self.set_sp)
        self.ui.cbFlowControl.activated.connect(self.set_sp)

        self.ui.actionNew.triggered.connect(self.new)
        self.ui.actionExit.triggered.connect(self.exitProgram)
        self.ui.actionClear.triggered.connect(self.actionClear)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionPortInfo.triggered.connect(self.portInfo)

        self.ui.pbOpen.pressed.connect(self.openPort)
        self.ui.pbSuspend.pressed.connect(self.sp.suspend)
        
        # Debug panel to the right
        self.ui.gbDebug.setHidden(True)
        self.ui.bpTest1.pressed.connect(lambda: self.send(b"ABCD"))
        self.ui.bpTest2.pressed.connect(lambda: self.send(b"0123456789"))
        #self.ui.colorTest.pressed.connect(lambda: self.send(colorTest))
        self.ui.leSyncString.textChanged.connect(self.syncChanged)

        self.loadSettings()

        # Initiate terminal state
        self.sp.state = State.DISCONNECTED

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
        
        self.updateUi()

    def signal_usr1(self, signum, frame) -> None:
        logging.debug("USR1 signal received")
        self.sp.suspend()

    def timer_5_timeout(self):
        if self.sp.state == State.SUSPENDED:
            rt = self.sp.suspend_timer.remainingTime()
            self.message(f"Port suspended. Time left {rt / 1000:.0f}")

        # Reconnect state
        if self.sp.state == State.RECONNECTING:
            self.initPort()
            self.sp.serial_port.clear()
            if self.sp.serial_port.open(QIODevice.ReadWrite):
                self.sp.state = State.CONNECTED
                self.message(f"Reconnected to port: /dev/{self.ui.cbPort.currentText()}")
            else:
                err = self.sp.serial_port.error()
                self.messageError(
                f"Failed to open port /dev/{self.ui.cbPort.currentText()}. {errors[err]}"
                )
                #logging.debug("Reconecting")
                self.message("Reconnecting...")

    def about(self) -> None:
        AboutDialog.about()

    def port_handler(self):
        if self.sp.state == State.DISCONNECTED:
            pass
        
    def timerEvent(self):
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

        self.updateUi()

    def updateUi(self):
        if self.sp.serial_port.isOpen() or self.sp.state == State.SUSPENDED:
            self.setWindowTitle(
                f"MpTerm  /dev/{self.ui.cbPort.currentText()} {self.ui.cbBitrate.currentText()}"
            )
            self.ui.pbOpen.setText("Close")
            self.ui.cbPort.setEnabled(False)
        else:
            self.setWindowTitle("MpTerm")
            self.ui.pbOpen.setText("Open")
            self.ui.cbPort.setEnabled(True)
        
        self.rxLabel.setText(f'<span style="color:Black">RX:</span> <span style="color:Purple">{self.sp.rxCnt:06d}</span> ')
        self.txLabel.setText(f'<span style="color:Black">TX:</span> <span style="color:Purple">{self.sp.txCnt:06d}</span> ')

        states = {
            State.DISCONNECTED : f"""<span style="color:Black">Disconected</span>""",
            State.CONNECTED : f"""<span style="color:Green">Connected  </span>""",
            State.SUSPENDED : f"""<span style="color:Red">Suspended </span>""",
            State.RECONNECTING : f"""<span style="color:Magenta">Reconnecting</span>""",
            }
        self.stateLabel.setText(f"{states[self.sp.state]}")

    def updatePorts(self):
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.ui.cbPort.addItem(port.portName())

    def handle_rts(self):
        logging.debug("RTS")
        if self.ui.cbRTS.isChecked():
            self.ui.cbRTS.setChecked(True)
            self.serial.setRequestToSend(True)
        else:
            self.ui.cbRTS.setChecked(False)
            self.serial.setRequestToSend(False)
            
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
        self.sp.clear_counters()
        self.update()

    # scroll down to bottom
    def scrollDown(self):
        vsb =self.terminal.verticalScrollBar()
        vsb.setValue(vsb.maximum())
        pass

    def _message(self, msg):
        self.ui.statusbar.showMessage(msg, 4000)

    # Show message in status bar
    def message(self, msg):
        self.ui.statusbar.setStyleSheet("color: black")
        self._message(msg)
        logging.debug(msg)

    # Show error message in status bar
    def messageError(self, msg):
        self.ui.statusbar.setStyleSheet("color: red")
        self._message(msg)
        logging.error(msg)

    # def appendText(self, str):    
    #     # move cursor to end of buffer
    #     self.ui.textEdit.moveCursor(QTextCursor.End)
    #     self.ui.textEdit.appendPlainText(str)

    def appendHtml(self, str):
        # move cursor to end of buffer
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertHtml(str)
        pass

    def read(self):
        # get all data from buffer

        data = self.sp.serial_port.readAll()
        data_str = str(data, "utf-8")

        self.sp.rxCnt += data.count()

        db = data_str.replace("\x1b", "\\e").replace("\x0a", "\\n").replace("\x0d", '\\r')
        logging.debug(f"Data received: {data.count()} {db}")

        DisplayMode = self.ui.cbDisplay.currentData()

        if DisplayMode == MpTerm.Ascii:  # Standard ascii display mode
            #self.decoder.append_string(data_str)
            #self.terminal.append(data_str)
            self.terminal.apps(data_str)

        elif DisplayMode == MpTerm.Hex:  # Hexadecimal display mode
            s = ""
            # self.ui.textEdit.setFont()
            for i in range(0, data.count()):
                ch = data.at(i)
                chd = int.from_bytes(ch, 'big')

                #logging.debug(f"{chd:02x} {hex2str(chd)}")
                # handle sync
                # if self.sync >= 0 and ord(ch) == self.sync:
                #     s = s + '\n'

                s = s + f"{chd:02x} "

            # self.ui.textEdit.insertPlainText(s)
            self.appendHtml(s)

        self.scrollDown()
        self.updateUi()

    def send(self, data: bytearray):
        if self.sp.is_open():
            res = self.sp.serial_port.write(data)
            if res >0: 
                self.sp.txCnt += res
            else:
                logging.error("Could not write data.")
            self.updateUi()

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def openPort(self):
        if self.sp.is_open():
            self.sp.close()
            self.updateUi()
            return

        self.initPort()
        self.sp.serial_port.clear()
        res = self.sp.open(QIODevice.ReadWrite)
        if res:
            self.message("Opening port: /dev/" + self.ui.cbPort.currentText())
        else:
            err = self.sp.serial_port.error()
            self.messageError(
                f"Failed to open port /dev/{self.ui.cbPort.currentText()}. {errors[err]}"
            )

        self.updateUi()

    def initPort(self):
        self.setPort()
        self.set_sp()

    def setPort(self):
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
        #self.prof.display = self.ui.cbDisplay.currentData()
        #self.prof.sync = self.ui.leSyncString.text()
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

        #self.ui.cbFlowControl.setCurrentText(self.settings["bitrate"])

        # self.setCbText(self.ui.cbPort, prof.port)
        # self.setCbText(self.ui.cbBitrate, prof.bitrate)
        # self.setCbData(self.ui.cbBits, prof.databits)
        # self.setCbData(self.ui.cbStopBits, prof.stopbits)
        # self.setCbData(self.ui.cbParity, prof.parity)
        # self.setCbData(self.ui.cbFlowControl, prof.flowcontrol)
        # self.setCbData(self.ui.cbDisplay, prof.display)
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
        self.appendHtml(    
            f"<b>{self.ss(desc)}</b><code><font color='Green'>{data}<br>"
        )

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
    parser.add_argument("--suspend", action="store_true",
                        help="Send signal to suspend port temporary")
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
        with os.popen("ps aux | grep mpterm.py | grep -v -e 'grep' -e '--suspend'") as f:
            res = f.readlines()

        for r in res:
            pid = int(r.split()[1])
            logging.debug(f"Sending suspend signal to process pid={pid}")
            os.kill(pid, 10)

        sys.exit()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")   # 'cleanlooks', 'gtk2', 'cde', 'motif', 'plastique', 'qt5ct-style', 'Windows', 'Fusion'
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
