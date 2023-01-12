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
from escape import Esc, Ascii, TerminalState2, CSI, SGR, EscapeObj

# Variables ------------------------------------------------------------------



# Code -----------------------------------------------------------------------

keys = { Qt.Key_Enter:("\n", "Enter"), 
         Qt.Key_Return:("\n", "Return"), 
         Qt.Key_Escape:("", "Escape"), 
         Qt.Key_Delete:("", "Delete"), 
         Qt.Key_Left:(Esc.CUR_BACK, "Left"),
         Qt.Key_Right:(Esc.CUR_FORWARD, "Right"),
         Qt.Key_Up:(Esc.CUR_UP, "Up"),
         Qt.Key_Down:(Esc.CUR_DOWN, "Down"),
         Qt.Key_Insert:("", "Insert"),
         Qt.Key_Backspace:("\b", "Backspace"),
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


class TerminalWin(QPlainTextEdit):

    def __init__(self, parent=None, sp=None, init=""):
        super().__init__(parent)
        self.sp=sp
        font = QFont()
        font.setFamily("Monospace")
        self.setFont(font)
        self.setObjectName("textEdit")
        #self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("background-color: rgb(0, 0, 0); color : White")

        self.cur = QTextCursor(self.document())
        # doc = self.document()
        # settings = QTextOption()
        # settings.setFlags(QTextOption.IncludeTrailingSpaces | QTextOption.ShowTabsAndSpaces )
        # doc.setDefaultTextOption(settings)

        # p = self.viewport().palette()
        # p.setColor(self.viewport().backgroundRole(), QColor(0,0,0))
        # self.viewport().setPalette(p)
        
        self.ts = TerminalState2()

        self.setReadOnly(True)
        self.clear()
        self.ensureCursorVisible()
        self.setCursorWidth(2)
        self.overwrite = False
        self.idx = 0
        self.maxLines = 100
        self.cr = False

    def setMaxLines(self, maxLines):
        self.maxLines = maxLines

    def clear(self):
        super().clear()
        self.ts.reset()
        self.moveCursor(QTextCursor.End)
        
    def update(self, s : str) -> str:
        self.ts.update(s)
        #b = template + self.ts.get_buf()
        self.buf += b
        logging.debug(b)

    def printpos(self, newPos : QTextCursor.MoveOperation ) -> None:
        pos = self.cur.position() 
        bpos = self.cur.positionInBlock()
        print(f"Cursor moved: abs:{pos}  block:{bpos}  newpos: {newPos}") 
        
    def insert(self, html):
        self.cur.insertHtml(html)
        #self.printpos(None)

    def move(self, newPos : QTextCursor) -> None:
        self.cur.movePosition(newPos)
        #self.printpos(newPos)

    def limit(self):
        lines = self.document().lineCount()

        if lines > self.maxLines:
            cursor = QTextCursor(self.document())  
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.Down, 2)
            cursor.removeSelectedText()  


    def append_html(self, html):

        self.move(QTextCursor.End)
        self.insert(html)

    def apps(self, s : str) -> None:
        lines = self.ts.update(s)

        rows = self.document().lineCount()
        
        for line in lines:
            
            if type(line) == EscapeObj:
                if line.csi == CSI.CURSOR_UP:
                    self.move(QTextCursor.Up)
                    continue

                if line.csi == CSI.CURSOR_DOWN:
                    self.move(QTextCursor.Down)
                    continue

                if line.csi == CSI.CURSOR_NEXT_LINE:
                    continue

                if line.csi == CSI.ERASE_IN_DISPLAY:
                    self.clear()
                    continue

                if line.csi == CSI.CURSOR_POSITION:
                    
                    continue
                
                if line.csi == CSI.CURSOR_PREVIOUS_LINE:
                    logging.debug("Cursor previous line") 
                    self.move(QTextCursor.StartOfLine)
                    self.move(QTextCursor.Up)
                    continue
                
            if line == Ascii.BS:
                logging.debug("Backspace")
                # self.cur.deletePreviousChar()
                self.move(QTextCursor.Left)
                continue

            if line == Ascii.CR:
                logging.debug("Carriage return")
                self.move(QTextCursor.StartOfLine)
                self.cr = True
                continue

            if line == Ascii.NL:
                logging.debug("Newline")
                if self.cr:
                    self.move(QTextCursor.EndOfLine)
                    self.cr = False
                self.cur.insertHtml("<br>")
                continue
                
            #logging.debug(line) 
            #self.append_html(line)
            l = len(line)
            if not self.cur.atEnd():
                self.cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, l)
                #print(f"Distance to end: {l}")
                #self.cur.setPosition()
                #self.cur.removeSelectedText()
                self.cur.insertHtml(line)
                self.cur.movePosition(QTextCursor.Right, l)
                continue
                
            self.cur.insertHtml(line)
            self.cur.movePosition(QTextCursor.Right, l)
            self.cr = False

        self.limit()
        
    def keyPressEvent(self, e: QKeyEvent) -> None:
        logging.debug(f"  {e.key():x}  {get_description(e)}")   
        self.sp.send_string(get_key(e))
        #super().keyPressEvent(e)

    def scroll_down(self):
        vsb=self.verticalScrollBar()
        vsb.setValue(vsb.maximum())


def main() -> None:
    pass

if __name__ == "__main__":
    main()
    