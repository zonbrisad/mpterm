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
import sys

from escape import Escape, Ascii, TerminalState, TerminalLine, escape_attribute_test
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont, QKeyEvent, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QAction,
    QLabel,
    QPushButton,
    QComboBox,
    QWidget,
)

# Variables ------------------------------------------------------------------

# Code -----------------------------------------------------------------------

keys = {
    # Qt.Key_Enter: ("\n", "Enter"),
    # Qt.Key_Return: ("\n\r", "Return"),
    Qt.Key_Escape: ("", "Escape"),
    Qt.Key_Delete: ("", "Delete"),
    Qt.Key_Left: (Escape.BACK, "Left"),
    Qt.Key_Right: (Escape.FORWARD, "Right"),
    Qt.Key_Up: (Escape.UP, "Up"),
    Qt.Key_Down: (Escape.DOWN, "Down"),
    Qt.Key_Insert: ("", "Insert"),
    Qt.Key_Backspace: ("\b", "Backspace"),
    Qt.Key_Home: ("", "Home"),
    Qt.Key_End: ("", "End"),
    Qt.Key_PageDown: ("", "Page down"),
    Qt.Key_PageUp: ("", "Page up"),
    Qt.Key_F1: ("\x09", "F1"),
    Qt.Key_F2: ("", "F2"),
    Qt.Key_F3: ("", "F3"),
    Qt.Key_F4: ("", "F4"),
    Qt.Key_F5: ("", "F5"),
    Qt.Key_F6: ("", "F6"),
    Qt.Key_F7: ("", "F7"),
    Qt.Key_F8: ("", "F8"),
    Qt.Key_F9: ("", "F9"),
    Qt.Key_F10: ("", "F10"),
    Qt.Key_F11: ("", "F11"),
    Qt.Key_F12: ("", "F12"),
    Qt.Key_Control: ("", "Control"),
    Qt.Key_Shift: ("", "Shift"),
    Qt.Key_Alt: ("", "Alt"),
    Qt.Key_AltGr: ("", "Alt Gr"),
    Qt.Key_Space: (" ", "Space"),
    Qt.Key_Print: ("", "Print"),
    Qt.Key_ScrollLock: ("", "Scroll lock"),
    Qt.Key_CapsLock: ("", "Caps lock"),
    Qt.Key_Pause: ("", "Pause"),
    Qt.Key_Tab: (Ascii.TAB, "Tab"),
}


def get_description(key: QKeyEvent) -> str:
    for a, b in keys.items():
        if key.key() == a:
            return b[1]

    return key.text()


def get_key(key: QKeyEvent) -> str:
    for a, b in keys.items():
        if key.key() == a:
            return b[0]

    return key.text()


class QTerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None, init=""):
        super().__init__(parent)

        self.cur = QTextCursor(self.document())
        self.ts = TerminalState()
        self.setCursorWidth(2)
        self.ensureCursorVisible()
        self.setReadOnly(True)
        self.clear()

        font = QFont()
        font.setFamily("Monospace")
        font.setPointSize(10)
        self.setFont(font)
        # self.maximumBlockCount = 100
        # self.setMaximumBlockCount(10)

        # self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet(
            "background-color: rgb(0, 0, 0); color : White; font-family:Monospace; font-size:10pt; line-height:1.5;"
        )
        # self.setStyleSheet("background-color: rgb(0, 0, 0); color : White; line-height:20pt; font-family:Monospace")

        self.overwrite = False
        self.idx = 0
        self.maxLines = 100
        self.cr = False
        self.last_id = 0

    def setMaxLines(self, maxLines):
        self.maxLines = maxLines

    def clear(self):
        super().clear()
        self.ts.reset()
        self.moveCursor(QTextCursor.End)

    # def update(self, s: str) -> str:
    #     self.ts.update(s)
    #     self.buf += b
    #     logging.debug(b)

    def printpos(self, newPos: QTextCursor.MoveOperation) -> None:
        pos = self.cur.position()
        bpos = self.cur.positionInBlock()
        logging.debug(f"Cursor moved: abs:{pos}  block:{bpos}  newpos: {newPos}")

    def insert(self, html):
        self.cur.insertHtml(html)

    def move(self, direction: QTextCursor, anchor: QTextCursor, steps: int = 1) -> None:
        self.cur.movePosition(direction, anchor, n=steps)
        # print(
        #     f"Cursor back: direction: {direction:2}  lines: {self.document().lineCount():3}  col: {self.cur.columnNumber():2}  steps: {steps:3}"
        # )

    def remove_rows_alt(self, lines):
        logging.debug(f"Removing {lines} lines")
        cursor = self.textCursor()  # QTextCursor(self.document())

        for _ in range(lines):
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.setTextCursor(cursor)

    def limit_lines(self):
        lines = self.document().lineCount()
        logging.debug(f"Lines: {lines}  Maxlines: {self.maxLines}")
        if lines > self.maxLines:
            self.remove_rows_alt(lines - self.maxLines)

    def append_html(self, html):
        self.move(QTextCursor.End, QTextCursor.MoveAnchor)
        self.insert(html)
        self.limit_lines()

    def insertHtml(self, html):
        self.cur.insertHtml(html)
        self.cur.movePosition(QTextCursor.Right, len(html))

    def append_terminal_text(self, s: str) -> None:
        tokens = self.ts.update(s)

        for token in tokens:
            if type(token) is TerminalLine:
                if token.id > self.last_id:  # a new line detected
                    self.last_id = token.id
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.cur.insertHtml("<br>")

                if token.id == self.last_id:  # last row
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

                if token.id < self.last_id:
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.move(
                        QTextCursor.Up, QTextCursor.MoveAnchor, self.last_id - token.id
                    )
                    self.move(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                html = token.line_to_html()
                self.cur.insertHtml(html)

        self.limit_lines()

    def scroll_down(self):
        vsb = self.verticalScrollBar()
        vsb.setValue(vsb.maximum())


class MainForm(QMainWindow):
    # Handle windows close event
    def closeEvent(self, a0: QCloseEvent) -> None:
        return super().closeEvent(a0)

    def exitProgram(self, e):
        self.close()

    def add_button(self, label, text):
        pb = QPushButton(label, self.centralwidget)
        pb.pressed.connect(lambda: self.terminal.append_terminal_text(text))
        self.buttonLayout.addWidget(pb)

    def __init__(self, args, parent=None):
        super(MainForm, self).__init__(parent)

        self.centralwidget = QWidget(self)
        self.resize(850, 500)

        # Layouts
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)

        self.setCentralWidget(self.centralwidget)

        self.main_layout = QHBoxLayout()
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.addSpacing(10)
        self.main_layout.addLayout(self.buttonLayout)
        self.rightVLayout = QVBoxLayout()
        self.main_layout.addLayout(self.rightVLayout)
        self.verticalLayout.addLayout(self.main_layout)

        self.terminal = QTerminalWidget(self.centralwidget)
        self.terminal.setMaxLines(500)
        self.rightVLayout.addWidget(self.terminal)

        self.add_button("Attributes", escape_attribute_test)
        self.add_button("Cursor up", Escape.UP)
        self.add_button("Cursor down", Escape.DOWN)
        self.add_button("Cursor back", Escape.BACK)
        self.add_button("Cursor forward", Escape.FORWARD)
        self.add_button("Erase in line", "\x1b[K")

        self.buttonLayout.addStretch()

        # Menu bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Menu
        self.menuFile = QMenu(self.menubar, title="&File")
        self.menubar.addAction(self.menuFile.menuAction())

        self.actionExit = QAction("Quit", self, triggered=self.exitProgram)
        self.actionExit.setToolTip("Quit")
        self.actionExit.setShortcutContext(Qt.WidgetShortcut)
        self.menuFile.addAction(self.actionExit)


def main() -> None:
    app = QApplication(sys.argv)
    mainForm = MainForm(sys.argv)
    mainForm.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
