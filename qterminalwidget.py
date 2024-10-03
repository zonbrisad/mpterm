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
from typing import Callable

from escape import (
    Ansi,
    Ascii,
    TerminalState,
    TerminalLine,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QTextCursor,
    QFont,
    QKeyEvent,
    QKeyEvent,
    QCloseEvent,
    QFontDatabase,
    QTextBlockFormat,
)
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
    Qt.Key_Left: (Ansi.BACK, "Left"),
    Qt.Key_Right: (Ansi.FORWARD, "Right"),
    Qt.Key_Up: (Ansi.UP, "Up"),
    Qt.Key_Down: (Ansi.DOWN, "Down"),
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
    """QTerminalWidget implements a partial ANSI terminal into a QPlainTextEdit."""

    def __init__(self, parent=None, init="") -> None:
        super().__init__(parent)

        self.cur = QTextCursor(self.document())
        self.terminal_state = TerminalState()
        self.setCursorWidth(2)
        self.ensureCursorVisible()
        self.setReadOnly(True)
        self.clear()

        # font = QFont()
        # font.setFamily("Monospace")
        # font.setPointSize(10)
        # self.setFont(font)

        # self.maximumBlockCount = 100
        # self.setMaximumBlockCount(10)

        #
        # https://stackoverflow.com/questions/10250533/set-line-spacing-in-qtextedit
        #
        # bf = self.cur.blockFormat()
        # bf.setLineHeight(10, QTextBlockFormat.LineHeightTypes.SingleHeight)
        # bf.setLineHeight(30, QTextBlockFormat.LineHeightTypes.FixedHeight)
        # bf.setLineHeight(50, QTextBlockFormat.LineHeightTypes.LineDistanceHeight)
        # self.cur.setBlockFormat(bf)

        # self.setFocusPolicy(Qt.NoFocus)
        # https://developer.mozilla.org/en-US/docs/Web/CSS/line-height

        # self.setStyleSheet(  # No overlapping lines, but line distance to large
        #     """
        #     color : White;
        #     background-color: rgb(0, 0, 0);
        #     font-family:Monospace;
        #     font-size:12pt;
        #     line-height:1.2;
        #     """
        # )
        # self.setStyleSheet(  #
        #     """
        #     color : White;
        #     background-color: rgb(0, 0, 0);
        #     font-family:Monospace;
        #     font-size:10px;
        #     font-style:normal;
        #     """
        # )

        self.setStyleSheet(  # Good line distance, but with line overlapping
            """
        color : White;
        background-color: rgb(0, 0, 0);
        font-family:Monospace;
        font-size:10pt;
        line-height:1.2;
        """
        )
        # self.setStyleSheet(  # Test of font other than "Monospace"
        #     """
        #     color : White;
        #     background-color: rgb(0, 0, 0);
        #     font-family:UbuntuMono;
        #     font-size:12pt;
        #     line-height:normal;
        #     """
        # )

        # self.overwrite = False
        # self.idx = 0
        # self.cr = False
        self.max_lines = 100
        self.last_id = 0

    def setMaxLines(self, max_lines) -> None:
        self.max_lines = max_lines

    def clear(self) -> None:
        super().clear()
        self.terminal_state.reset()
        self.moveCursor(QTextCursor.End)

    def printpos(self, newPos: QTextCursor.MoveOperation) -> None:
        pos = self.cur.position()
        bpos = self.cur.positionInBlock()
        logging.debug(f"Cursor moved: abs:{pos}  block:{bpos}  newpos: {newPos}")

    def insert(self, html: str) -> None:
        self.cur.insertHtml(html)

    def move(self, direction: QTextCursor, anchor: QTextCursor, steps: int = 1) -> None:
        self.cur.movePosition(direction, anchor, n=steps)

    def remove_rows_alt(self, lines) -> None:
        logging.debug(f"Removing {lines} lines")
        cursor = self.textCursor()  # QTextCursor(self.document())

        for _ in range(lines):
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.setTextCursor(cursor)

    def limit_lines(self) -> None:
        lines = self.document().lineCount()
        logging.debug(f"Lines: {lines}  Maxlines: {self.max_lines}")
        if lines > self.max_lines:
            self.remove_rows_alt(lines - self.max_lines)

    def insert_html(self, html: str) -> None:
        self.cur.insertHtml(html)
        self.cur.movePosition(QTextCursor.Right, len(html))

    def append_html_text(self, html: str) -> None:
        self.move(QTextCursor.End, QTextCursor.MoveAnchor)
        self.insert(html)
        self.limit_lines()

    def append_ansi_text(self, data: str) -> None:
        lines = self.terminal_state.update(data)

        for line in lines:
            # print(f"X {line}")
            if type(line) is TerminalLine:
                if line.id > self.last_id:  # a new line detected
                    self.last_id = line.id
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.cur.insertHtml("<br>")

                if line.id == self.last_id:  # last row
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

                if line.id < self.last_id:
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.move(
                        QTextCursor.Up, QTextCursor.MoveAnchor, self.last_id - line.id
                    )
                    self.move(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                self.cur.insertHtml(line.line_to_html())

        self.limit_lines()

    def scroll_down(self) -> None:
        vsb = self.verticalScrollBar()
        vsb.setValue(vsb.maximum())


class MainForm(QMainWindow):
    # Handle windows close event
    def closeEvent(self, a0: QCloseEvent) -> None:
        return super().closeEvent(a0)

    def exitProgram(self, e) -> None:
        self.close()

    def add_button(self, label: str, text: str) -> None:
        pb = QPushButton(label, self.centralwidget)
        pb.pressed.connect(lambda: self.terminal.append_ansi_text(text))
        self.button_layout.addWidget(pb)

    def add_func_button(self, label: str, func: Callable) -> None:
        pb = QPushButton(label, self.centralwidget)
        pb.pressed.connect(func)
        self.button_layout.addWidget(pb)

    def __init__(self, args, parent=None) -> None:
        super(MainForm, self).__init__(parent)

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.resize(850, 500)

        # Layouts
        self.vertical_layout = QVBoxLayout(self.centralwidget)
        self.vertical_layout.setContentsMargins(2, 2, 2, 2)
        self.vertical_layout.setSpacing(2)

        self.main_layout = QHBoxLayout(self.centralwidget)
        self.button_layout = QVBoxLayout(self.centralwidget)
        self.button_layout.addSpacing(10)
        self.main_layout.addLayout(self.button_layout)
        self.right_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.addLayout(self.right_layout)
        self.vertical_layout.addLayout(self.main_layout)

        self.terminal = QTerminalWidget(self.centralwidget)
        self.terminal.setMaxLines(500)
        self.right_layout.addWidget(self.terminal)

        self.add_func_button("Clear terminal", lambda: self.terminal.clear())
        self.add_button("Font Attributes", Ansi.test())
        self.add_button("Colors 256", Ansi.color_test())
        self.add_button("Cursor up", Ansi.UP)
        self.add_button("Cursor down", Ansi.DOWN)
        self.add_button("Cursor back", Ansi.BACK)
        self.add_button("Cursor forward", Ansi.FORWARD)
        self.add_button("Erase in line", "\x1b[K")

        self.button_layout.addStretch()

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

        # self.terminal.append_terminal_text(escape_attribute_test)
        # print(escape_attribute_test)

        self.terminal.append_html_text(
            """<div style="font-size:20px;line-height:40px;color:green;">
                Line 1 <br>
                Line 2 <br>
              </div>"""
        )

        # list fonts
        # fonts = QFontDatabase()
        # print(fonts.families())


def main() -> None:
    app = QApplication(sys.argv)
    mainForm = MainForm(sys.argv)
    mainForm.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
