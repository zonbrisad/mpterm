#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# 
#
# File:    TermWin_test.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2022-08-18
# License: 
# Python:  3
# QT       5
# 
#----------------------------------------------------------------------------
# Pyplate
#   This file is generated from pyplate Python template generator.
#
# Pyplate is developed by:
#   Peter Malmberg <peter.malmberg@gmail.com>
#
# Available at:
#   https://github.com/zobrisad/pyplate.git
# 
# ---------------------------------------------------------------------------
#

# Imports -------------------------------------------------------------------

import sys
import os
import traceback
import logging
import argparse
from datetime import datetime, date, time

sys.path.append("../")

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qterminalwidget import QTerminalWidget
from escape import Escape, escape_attribute_test 

from PyQt5 import QtCore, QtGui, QtWidgets

# Settings ------------------------------------------------------------------

# Application settings
AppName     = "TermWin_test"
AppVersion  = "0.1"
AppLicense  = ""
AppAuthor   = "Peter Malmberg <peter.malmberg@gmail.com>"
AppDesc     = "TerminalWindow test"
AppDomain   = "Domain"
AppOrg      = "Organisation"
 
# Qt settings
WindowTitle = AppName
WindowXSize = 1000
WindowYSize = 1000

QCoreApplication.setOrganizationName(AppOrg)
QCoreApplication.setOrganizationDomain(AppDomain)
QCoreApplication.setApplicationName(AppName)

# Time to show message in ms
MsgTime     = 2000

# Code ----------------------------------------------------------------------


class MainForm(QMainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        
        # Set window size. 
        self.resize(WindowXSize, WindowYSize)
 
        # Set window title  
        self.setWindowTitle(WindowTitle) 
        
        # Create central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
                
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setSpacing(2)
         
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        
        # Button 1
        self.pb1 = QtWidgets.QPushButton("Move right", self.centralwidget)
        self.verticalLayout.addWidget(self.pb1)
        self.pb1.pressed.connect(self.attributes)

        self.pb2 = QtWidgets.QPushButton("Move left", self.centralwidget)
        self.verticalLayout.addWidget(self.pb2)
        self.pb2.pressed.connect(self.move_left)

        self.pb3 = QtWidgets.QPushButton("Move up", self.centralwidget)
        self.verticalLayout.addWidget(self.pb3)
        self.pb3.pressed.connect(self.move_up)

        self.pb4 = QtWidgets.QPushButton("Move down", self.centralwidget)
        self.verticalLayout.addWidget(self.pb4)
        self.pb4.pressed.connect(self.move_down)

        # Exit button
        self.pbExit = QtWidgets.QPushButton("Exit", self.centralwidget)
        self.pbExit.pressed.connect(lambda: self.close())
        self.verticalLayout.addWidget(self.pbExit)

        # PlaintTextEdit
        self.vlPlain = QtWidgets.QVBoxLayout()
        self.vlPlain.setSpacing(2)
        self.horizontalLayout.addLayout(self.vlPlain)
        self.label = QtWidgets.QLabel("PlainTextEdit", self.centralwidget)
        self.vlPlain.addWidget(self.label)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self)
        self.plainTextEdit.setReadOnly(False)
        self.vlPlain.addWidget(self.plainTextEdit)
        self.plainTextEdit.textChanged.connect(self.changeText)

        # TerminalWin
        self.vlText = QtWidgets.QVBoxLayout()
        self.vlText.setSpacing(2)
        self.horizontalLayout.addLayout(self.vlText)
        self.label = QtWidgets.QLabel("TerminaWin", self.centralwidget)
        self.vlText.addWidget(self.label)
        self.terminal = QTerminalWidget(self.centralwidget, serialPort = None)
        self.vlText.addWidget(self.terminal)

        self.changeText()

        # Spacer
        self.spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.spacerItem1)

        # Statusbar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # Menubar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 855, 25))
        self.setMenuBar(self.menubar)
        
        # Menus
        self.menuFile   = QtWidgets.QMenu("File", self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())
        
        self.actionQuit = QtWidgets.QAction("Quit",  self ) 
        self.actionQuit.setStatusTip('Quit application')
        self.actionQuit.setShortcut('Ctrl+Q')
        self.actionQuit.triggered.connect(lambda: self.close())

        self.menuFile.addAction(self.actionQuit)

    def attributes(self):
        self.plainTextEdit.setPlainText(escape_attribute_test)
        
    def move_left(self):
        #self.plainTextEdit.moveCursor(QTextCursor.Left)
        self.cursor_changed()

    def move_up(self):
        #self.plainTextEdit.moveCursor(QTextCursor.Up)
        self.cursor_changed()

    def move_down(self):
        #self.plainTextEdit.moveCursor(QTextCursor.Down)
        self.cursor_changed()

    def changeText(self):
        self.terminal.apps(self.plainTextEdit.toPlainText())
        #self.terminal.app(self.plainTextEdit.toPlainText())
        #x = self.terminal.document().toHtml()
        #x = self.terminal.document().toPlainText()
        #print(x)
                                                          
        
def main():
    logging_format = "[%(levelname)s] %(lineno)d %(funcName)s() : %(message)s"
    logging.basicConfig(format=logging_format, level=logging.DEBUG)
           
    app = QApplication(sys.argv)
    mainForm = MainForm()
    mainForm.show()
    sys.exit(app.exec_())                   

# Absolute path to script itself        
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))

# Main program handle 
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt as e: # Ctrl-C
        raise e
    except SystemExit as e:        # sys.exit()
        raise e
    except Exception as e:
        print('ERROR, UNEXPECTED EXCEPTION')
        print(str(e))
        traceback.print_exc()
        os._exit(1)
                

