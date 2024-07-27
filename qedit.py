#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# format validated qlineedit
#
# File:     qedit
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2024-07-26
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

from typing import Callable
from PyQt5.QtWidgets import QLineEdit, QSizePolicy


class StyleS:
    normal = """
    QLineEdit:enabled {
    color:Blask;
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
    win = "border:0"


class QNumberEdit(QLineEdit):
    def __init__(self, parent=None, min=None, max=None):
        super().__init__()
        self.textChanged.connect(self.changed)
        # self.setMaximumWidth(80)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.min = min
        self.max = max
        self.on_changed: Callable = None

    def set_on_changed(self, on_changed: Callable) -> None:
        self.on_changed = on_changed

    def set_value(self, val) -> None:
        self.setText(str(val))

    def get_value(self) -> int:
        if self.text().strip().isnumeric():
            return int(self.text().strip())
        return None

    def set_min(self, min) -> None:
        self.min = min

    def set_max(self, max) -> None:
        self.max = max

    def validate(self, val: str) -> bool:

        if self.text().strip().isnumeric() is False:
            return False

        v = int(val)

        if self.min is not None:
            if v < self.min:
                return False

        if self.max is not None:
            if v > self.max:
                return False

        return True

    def changed(self, a0: str) -> None:
        if self.text().strip().isnumeric():
            self.setStyleSheet(StyleS.normal)
        else:
            self.setStyleSheet(StyleS.error)

        if self.on_changed is not None:
            self.on_changed()


class QHexEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__()
        self.textChanged.connect(self.changed)
        # self.setMaximumWidth(80)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def is_hex_string(self, data: str) -> bool:
        try:
            self.hexstring_to_list(data)
        except ValueError:
            return False

        return True

    def hexstring_to_list(self, data: str) -> list[int]:
        tokens = data.strip().split(" ")
        lst = []
        for token in tokens:
            val = int(token, 16)
            if val < 0 or val > 255:
                raise ValueError
            lst.append(val)

        return lst

    def changed(self, a0: str) -> None:
        if self.is_hex_string(self.text()) is True:
            self.setStyleSheet(StyleS.normal)
        else:
            self.setStyleSheet(StyleS.error)

    def get_value(self) -> list[int]:
        lst = []

        try:
            lst = self.hexstring_to_list(self.text().strip())
        except ValueError:
            return []

        return lst


def main() -> None:
    pass


if __name__ == "__main__":
    main()
