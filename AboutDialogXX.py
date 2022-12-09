#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# about dialog
#
# File:     aboutdialog.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2022-11-23
# License:  
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QTextCursor, QIcon, QFont, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import (
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
)

class AboutDialogXX(QDialog):
    def __init__(self, App, parent=None):
        super(AboutDialogXX, self).__init__(parent)

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
        self.textEdit.insertHtml(self.x(App))

        # Buttonbox
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.setCenterButtons(True)
        self.verticalLayout.addWidget(self.buttonBox)

    def x(self, App) -> str:
        about_html = f"""
<center><h2>{App.NAME}</h2></center>
<br>

<table>
  <tr>
    <td> 
      <img src={App.ICON} width="48" height="48">
    </td>
    <td>
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
  </tr>
</table>
<hr>
<br>
{App.DESCRIPTION}
<br>
"""
        return about_html
    
    @staticmethod
    def about(App, parent=None):
        dialog = AboutDialogXX(App, parent)
        result = dialog.exec_()
        return result == QDialog.Accepted



def main() -> None:
    pass

if __name__ == "__main__":
    main()
