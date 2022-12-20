#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# terminal window for qt5
#
# File:     terminalwin
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2022-12-02
# License:  
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

# Imports --------------------------------------------------------------------

import logging

from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice
from PyQt5.QtGui import QTextCursor, QFont, QKeyEvent, QColor, QTextOption
from PyQt5.QtWidgets import (
    QTextEdit,
    QPlainTextEdit
)

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from dataclasses import dataclass
from escape import Esc, Ascii, TerminalState

# Variables ------------------------------------------------------------------



# Code -----------------------------------------------------------------------

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


template="""<pre>Mpterm\n"""

class TerminalWin(QPlainTextEdit):
    
    def __init__(self, parent=None, sp=None, init=""):
        super().__init__(parent)
        self.sp=sp
        font = QFont()
        font.setFamily("Monospace")
        self.setFont(font)
        self.setObjectName("textEdit")

        self.setStyleSheet("background-color: rgb(0, 0, 0); color : White")

        # doc = self.document()
        # settings = QTextOption()
        # settings.setFlags(QTextOption.IncludeTrailingSpaces | QTextOption.ShowTabsAndSpaces )
        # doc.setDefaultTextOption(settings)

        # p = self.viewport().palette()
        # p.setColor(self.viewport().backgroundRole(), QColor(0,0,0))
        # self.viewport().setPalette(p)
        
        self.setReadOnly(True)
        self.clear(init=init)
        self.ensureCursorVisible()
        self.setCursorWidth(2)

        self.ts = TerminalState()

    def clear(self, init = ""):
        super().clear()
        #self.setHtml(template+init)
        
        # self.appendHtml(template)
        # self.appendHtml("Kalle\n")
        self.moveCursor(QTextCursor.End)
        #self.buf = ""template

    def update(self, s : str) -> str:
        self.ts.update(s)
        b = template + self.ts.get_buf()
        self.buf += b
        #self.setHtml(self.buf)
        logging.debug(b)

    def append_html(self, html):
        cur = QTextCursor(self.document())
        cur.movePosition(QTextCursor.End)
        cur.insertHtml(html)

    def apps(self, s : str) -> None:
        lines = self.ts.update(s)
        
        for line in lines:
            self.append_html(line)
            logging.debug(line)
        
    def keyPressEvent(self, e: QKeyEvent) -> None:
        logging.debug(f"  {e.key():x}  {get_description(e)}")   
        self.sp.send_string(get_key(e))
        super().keyPressEvent(e)

    def scroll_down(self):
        vsb=self.verticalScrollBar()
        vsb.setValue(vsb.maximum())



def main() -> None:
    pass

if __name__ == "__main__":
    main()
    