from dataclasses import dataclass
from typing import List

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QDialog,
    QDialogButtonBox,
    QSizePolicy,
    QWidget,
)



@dataclass
class Macro:
    name: str = ""
    text: str = ""
    hex: bool = False
    repeat: bool = False
    intervallEdit: int = 1000

    @staticmethod
    def is_hex_string(data: str) -> bool:
        try:
            Macro.hexstring_to_list(data)
        except ValueError:
            return False

        return True

    @staticmethod
    def hexstring_to_list(data: str) -> List[int]:
        tokens = data.strip().split(" ")
        lst: List[int] = []
        for token in tokens:
            val = int(token, 16)
            if val < 0 or val > 255:
                raise ValueError
            lst.append(val)

        return lst

    def data(self) -> bytearray:
        """Return macro data as bytearray"""
        if self.hex is True:
            tokens = self.text.strip().split(" ")
            hs: List[int] = []
            try:
                for token in tokens:
                    h = int(token, 16)
                    hs.append(h)
            except ValueError:
                hs = []

            return bytearray(hs)

        return bytearray(
            self.text.replace("\\n", "\n")
            .replace("\\e", "\x1b")
            .replace("\\x1b", "\x1b"),
            "utf-8",
        )



class StyleS:
    normal = """
    QLineEdit:enabled {
    color:Black;
    }
    QLineEdit:disabled {
    color:gray;
    }
    """
    error = """
    QLineEdit:enabled {
    color:Red;
    }
    QLineEdit:disabled {
    color:gray;
    }
    """


class QMacroButton(QWidget):
    def __init__(self, macro: Macro, parent=None):
        super().__init__(parent=parent)
        self.macro = macro
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.macroButton = QPushButton(macro.name)
        self.macroButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout.addWidget(self.macroButton)
        self.repeatButton = QPushButton("R")
        self.repeatButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.layout.addWidget(self.repeatButton)


class MacroEditWidget(QWidget):
    def __init__(self, macro: Macro, parent=None):
        super().__init__(parent=parent)
        self.macro = macro
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        # self.layout.setSpacing(2)
        self.setLayout(self.layout)

        self.name = QLabel(macro.name)
        self.name.setMinimumWidth(30)
        self.macro_edit = QLineEdit(macro.text)
        self.macro_edit.textChanged.connect(self.macroChanged)
        self.hexModeCb = QCheckBox("Hex")
        self.hexModeCb.setToolTip("Interpret macro string as hex string (e.g. 0A 1B 2C)")
        self.hexModeCb.stateChanged.connect(self.macroChanged)
        self.repeatCb = QCheckBox("Repeat")

        self.intervallEdit = QLineEdit(str(macro.intervallEdit))
        self.intervallEdit.textChanged.connect(self.intervallChanged)
        self.intervallEdit.setMaximumWidth(40)
        # self.setMaxLength(4)
        # self.setSizePolicy(5)

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.macro_edit)
        self.layout.addWidget(self.hexModeCb)
        # self.layout.addWidget(self.repeatCb)
        # self.layout.addWidget(self.intervallEdit)

    def intervallChanged(self, a0: str) -> None:
        if self.intervallEdit.text().isnumeric():
            self.intervallEdit.setStyleSheet(StyleS.normal)
        else:
            self.intervallEdit.setStyleSheet(StyleS.error)

    def update(self) -> None:
        self.macro_edit.setText(self.macro.text)
        self.hexModeCb.setChecked(self.macro.hex)

    def hex_mode(self) -> bool:
        return self.hexModeCb.isChecked()

    def hex_mode_changed(self, a0: str) -> None:
        self.macroChanged()

    def macroChanged(self) -> None:
        if self.hex_mode() is True:
            if Macro.is_hex_string(self.macro_edit.text()) is True:
                self.macro_edit.setStyleSheet(StyleS.normal)
            else:
                self.macro_edit.setStyleSheet(StyleS.error)
        else:
            self.macro_edit.setStyleSheet(StyleS.normal)

    def accept(self) -> None:
        self.macro.text = self.macro_edit.text()
        self.macro.hex = self.hexModeCb.isChecked()


class MacroDialog(QDialog):
    def __init__(self, parent, macros) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle("Userdefined Macros")
        # self.setWindowIcon(QIcon(App.ICON))
        self.setMinimumWidth(600)
        self.macros = macros
        self.main_layout = QVBoxLayout()
        # self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.macro_edits = []
        for macro in self.macros:
            mew = MacroEditWidget(macro)
            self.main_layout.addWidget(mew)
            self.macro_edits.append(mew)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttonBox)

    def exec(self, macros) -> int:
        for macro_edit in self.macro_edits:
            macro_edit.update()

        return super().exec()

    def accept(self):
        for macro_edit in self.macro_edits:
            macro_edit.accept()

        self.close()


