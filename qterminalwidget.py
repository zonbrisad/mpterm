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

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor, QFont, QKeyEvent, QIcon, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import QPlainTextEdit

from escape import (
    Escape,
    Ascii,
    TerminalState,
    CSI,
    SGR,
    EscapeObj,
    TerminalLine,
)

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QMainWindow,
    QInputDialog,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QMenu,
    QMenuBar,
    QAction,
    QStatusBar,
    QLabel,
    QDialogButtonBox,
    QPushButton,
    QComboBox,
    QWidget,
    QLineEdit,
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

    def update(self, s: str) -> str:
        self.ts.update(s)
        # b = template + self.ts.get_buf()
        self.buf += b
        logging.debug(b)

    def printpos(self, newPos: QTextCursor.MoveOperation) -> None:
        pos = self.cur.position()
        bpos = self.cur.positionInBlock()
        logging.debug(f"Cursor moved: abs:{pos}  block:{bpos}  newpos: {newPos}")

    def insert(self, html):
        self.cur.insertHtml(html)
        # self.printpos(None)

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

        # lines = self.document().lineCount()

        for token in tokens:
            if type(token) is EscapeObj:
                if token.csi == CSI.CURSOR_UP:
                    self.move(QTextCursor.Up, QTextCursor.MoveAnchor)
                    continue

                if token.csi == CSI.CURSOR_DOWN:
                    self.move(QTextCursor.Down, QTextCursor.MoveAnchor)
                    continue

                if token.csi == CSI.CURSOR_BACK:
                    n = min((self.cur.columnNumber(), token.n))
                    self.move(QTextCursor.Left, QTextCursor.MoveAnchor, steps=n)
                    continue

                if token.csi == CSI.CURSOR_NEXT_LINE:
                    continue

                if token.csi == CSI.ERASE_IN_DISPLAY:
                    self.clear()
                    continue

                if token.csi == CSI.ERASE_IN_LINE:
                    if token.n == 0:  # clear from cursor to end of token
                        self.cur.movePosition(
                            QTextCursor.EndOfLine, QTextCursor.KeepAnchor
                        )

                    if token.n == 1:  # clear from cursor to begining of token
                        self.cur.movePosition(
                            QTextCursor.StartOfLine, QTextCursor.KeepAnchor
                        )

                    if token.n == 2:  # clear entire token
                        self.cur.movePosition(
                            QTextCursor.EndOfLine, QTextCursor.MoveAnchor
                        )
                        self.cur.movePosition(
                            QTextCursor.StartOfLine, QTextCursor.KeepAnchor
                        )

                    self.cur.removeSelectedText()
                    self.cur.deleteChar()
                    continue

                if token.csi == CSI.CURSOR_POSITION:
                    self.move(QTextCursor.End)
                    self.move(QTextCursor.StartOfLine)
                    for a in range(0, 25 - token.n):
                        self.move(QTextCursor.Up, QTextCursor.MoveAnchor)

                    logging.debug(f"Cursor position: n: {token.n}  m: {token.m}")
                    continue

                if token.csi == CSI.CURSOR_PREVIOUS_LINE:
                    logging.debug("Cursor previous token")
                    self.move(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.Up, QTextCursor.MoveAnchor)
                    continue

            if token == Ascii.BS:
                logging.debug("Backspace")
                self.move(QTextCursor.Left, QTextCursor.MoveAnchor)
                continue

            if token == Ascii.CR:
                logging.debug("Carriage return")
                self.move(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                self.cr = True
                continue

            if token == Ascii.NL:
                logging.debug("Newline")
                if self.cr:
                    self.move(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
                    self.cr = False
                self.cur.insertHtml("<br>")
                continue

            # if type(token) is TextObj:
            #     # text = token
            #     l = len(token.text)
            #     if not self.cur.atEnd():
            #         # self.cur.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, l)
            #         # self.cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, l)
            #         self.move(QTextCursor.Right, QTextCursor.KeepAnchor, l)
            #         # self.move(QTextCursor.Right, QTextCursor.MoveAnchor, l)
            #         # print(f"Distance to end: {l}")
            #         # self.cur.setPosition()
            #         # self.cur.removeSelectedText()
            #         print(f"X: {l:3} {token}")
            #         self.cur.insertHtml(token.html)
            #         self.move(QTextCursor.Right, QTextCursor.MoveAnchor, l)
            #         # self.cur.movePosition(QTextCursor.Right, l)
            #         continue

            #     # text = text.replace("<", "&lt;")
            #     self.cur.insertHtml(token.html)
            #     # self.cur.movePosition(QTextCursor.Right, l)
            #     self.cur.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, l)
            #     self.cr = False

            if type(token) is TerminalLine:
                if token.id > self.last_id:
                    self.last_id = token.id
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.cur.insertHtml("<br>")

                if token.id == self.last_id:
                    self.move(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                html = token.line_to_html()
                print(f"Token: {token}")
                print(f"Html: {html}")
                self.cur.insertHtml(html)

        self.limit_lines()

    def scroll_down(self):
        vsb = self.verticalScrollBar()
        vsb.setValue(vsb.maximum())


class MainForm(QMainWindow):
    # Handle windows close event
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.save_settings()
        return super().closeEvent(a0)

    def add_label_combobox(self, labelText) -> QComboBox:
        label = QLabel(self.centralwidget)
        label.setText(f"<b>{labelText}:</b>")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.portLayout.addWidget(label)
        comboBox = QComboBox(self.centralwidget)
        comboBox.setEditable(False)
        comboBox.setCurrentText("")
        self.portLayout.addWidget(comboBox)
        return comboBox

    def __init__(self, args, parent=None):
        super(MainForm, self).__init__(parent)

        self.centralwidget = QWidget(self)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)

        self.resize(850, 500)
        self.setCentralWidget(self.centralwidget)

        # Serial port settings above terminal widget
        self.portLayout = QHBoxLayout()
        self.portLayout.setSpacing(5)
        # self.portLayout.addSpacing(90)
        self.portLayout.addStretch()

        # "Buttons" layout, to the left
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.addSpacing(10)

        # Layouts
        self.rightVLayout = QVBoxLayout()
        self.rightVLayout.addWidget(self.terminal)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.buttonLayout)
        self.main_layout.addLayout(self.rightVLayout)

        self.verticalLayout.addLayout(self.portLayout)
        self.verticalLayout.addLayout(self.main_layout)

        # Macro layout (to the right)
        self.macroLayout = QVBoxLayout()
        self.macroLayout.setContentsMargins(2, 2, 2, 2)
        self.macroLayout.setSpacing(2)
        self.macroLayout.addSpacing(20)

        for macro in self.prof.macros:
            macro_button = QPushButton(
                macro.name,
                self.centralwidget,
                pressed=lambda m=macro: self.serialPort.send(m.data()),
            )
            self.macroLayout.addWidget(macro_button)

        self.macro_dialog = MacroDialog(self.prof.macros)
        self.macro_set = QPushButton("Edit macro's", self.centralwidget)
        self.macro_set.pressed.connect(self.edit_macro_dialog)

        self.macroLayout.addSpacing(20)
        self.macroLayout.addWidget(self.macro_set)
        self.macroLayout.addStretch()

        self.pbPause = QPushButton("Pause", self.centralwidget)
        self.pbPause.pressed.connect(self.pause)
        self.macroLayout.addWidget(self.pbPause)

        self.main_layout.addLayout(self.macroLayout)

        # Status bar
        self.statusbar = QStatusBar(self)
        self.statusbar.setLayoutDirection(Qt.LeftToRight)
        self.statusbar.setStyleSheet(StyleS.normal)
        self.setStatusBar(self.statusbar)

        # Status bar elements
        self.stateLabel = QLabel("")
        self.statusbar.addPermanentWidget(self.stateLabel, stretch=0)
        self.rxLabel = QLabel("")
        self.statusbar.addPermanentWidget(self.rxLabel, stretch=0)
        self.txLabel = QLabel("")
        self.statusbar.addPermanentWidget(self.txLabel, stretch=0)

        # Menu bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Menu
        self.menuFile = QMenu(self.menubar, title="&File")
        self.menubar.addAction(self.menuFile.menuAction())
        self.menuSettings = QMenu(self.menubar, title="Settings")
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuAction = QMenu(self.menubar, title="&Action")
        self.menubar.addAction(self.menuAction.menuAction())
        self.menuSend = QMenu(self.menubar, title="Send")
        self.menubar.addAction(self.menuSend.menuAction())
        self.menuHelp = QMenu(self.menubar, title="&Help")
        self.menubar.addAction(self.menuHelp.menuAction())

        # Menu actions
        self.actionNew = QAction("New", self, triggered=self.new_terminal)
        self.menuFile.addAction(self.actionNew)

        self.actionExit = QAction("Quit", self, triggered=self.exitProgram)
        self.actionExit.setToolTip("Quit")
        self.actionExit.setShortcutContext(Qt.WidgetShortcut)
        self.menuFile.addAction(self.actionExit)

        # self.actionEcho = QAction(
        #     "Echo", self, triggered=None, checkable=True
        # )
        # self.menuSettings.addAction(self.actionEcho)

        self.actionSetProgram = QAction(
            "Ext. Program", self, triggered=self.set_ext_program
        )
        self.menuSettings.addAction(self.actionSetProgram)
        self.actionSetTimeout = QAction(
            "Suspend timeout", self, triggered=self.set_suspend_timeout
        )
        self.menuSettings.addAction(self.actionSetTimeout)

        self.actionClear = QAction(self, text="Clear")
        self.actionClear.triggered.connect(self.terminal_clear)
        self.menuAction.addAction(self.actionClear)

        self.actionReset_port = QAction(self, text="Reset port")
        self.actionPortInfo = QAction(self, text="Port info", triggered=self.portInfo)
        self.menuAction.addAction(self.actionPortInfo)

        self.actionAbout = QAction(self, text="About")
        self.actionAbout.triggered.connect(
            lambda: AboutDialog.about(App.NAME, about_html)
        )
        self.menuHelp.addAction(self.actionAbout)

        # Send menu
        ctrlcAction = QAction("Ctrl-C (ETX)", self)
        ctrlcAction.triggered.connect(lambda: self.send_string(Escape.ETX))
        self.menuSend.addAction(ctrlcAction)
        ctrlcAction = QAction("Break (NULL)", self)
        ctrlcAction.triggered.connect(lambda: self.send_string(Ascii.NULL))
        self.menuSend.addAction(ctrlcAction)
        tabAction = QAction("Tab (0x09)", self)
        tabAction.triggered.connect(lambda: self.send_string(Ascii.TAB))
        self.menuSend.addAction(tabAction)

        self.testMenu = self.menuSend.addMenu("Tests")

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

        self.colorMenu = self.menuSend.addMenu("Colors")
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

        self.attrMenu = self.menuSend.addMenu("Attributes")
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

        # Timers
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.timerEvent)
        # self.timer.start()


def main() -> None:
    # app.setStyle(
    #     "Fusion"
    # )  # 'cleanlooks', 'gtk2', 'cde', 'motif', 'plastique', 'qt5ct-style', 'Windows', 'Fusion'
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    mainForm = MainForm(sys.argv)
    mainForm.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
