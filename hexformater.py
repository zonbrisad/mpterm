import enum
from typing import List

from escape import Ascii


class HexFormaterMode(enum.Enum):
    Length = 1
    SynchAfter = 2
    SynchBefore = 3


class HexFormater:

    def __init__(self) -> None:
        self.end = "<br>"
        self.sync_string: List[int] = []
        self.mode = HexFormaterMode.Length
        self.display_mode = None
        self.set_columns(12)
        self.clear()

    def set_mode(self, mode) -> None:
        # store display mode (expected to be an enum with .name, e.g. MpTerm)
        self.display_mode = mode
        self.index = 1

    def clear(self) -> None:
        self.index = 1
        self.sync_index = 0
        self.sync_list = []

    def append(self, chr: str) -> None:
        self.chars.append(chr)

    def append_byte(self, chd) -> None:
        if self.index >= self.max:
            self.clear()
            self.append(f"{self.get_char(chd)}<br>")
            return

        self.append(f"{self.get_char(chd)} ")
        self.index += 1

    def set_columns(self, cols: int) -> None:
        self.max = cols

    def set_sync_string(self, sync: List[int]) -> None:
        self.sync_string = sync

    def get(self, byte: int) -> str:

        if byte == 0x3C:  # Less than '<'
            return "'&lt;'"

        symbol = Ascii.symbol(byte)
        if symbol is None:
            if byte < 128:
                return f"'{chr(byte)}'"
            else:
                return "---"
        return symbol

    def get_char(self, byte: int) -> str:
        # display_mode expected to be enum (MpTerm) passed from mpterm
        mode_name = getattr(self.display_mode, "name", None)
        if mode_name == "Hex":
            return f"{byte:02x}"

        if mode_name == "AsciiHex":
            ch = self.get(byte)
            return f"<b>{byte:02x}</b> {ch:3}"

        # default to ascii representation
        return self.get(byte)

    def format(self, data) -> str:
        self.chars = []
        # support objects that provide count()/at(i) (e.g., QByteArray)
        try:
            cnt = data.count()
            getter = lambda i: int.from_bytes(data.at(i), "big")
        except Exception:
            # fallback for Python bytes/bytearray
            cnt = len(data)
            getter = lambda i: data[i]

        for i in range(0, cnt):
            byte = getter(i)

            # if syncstring empty just printout
            if len(self.sync_string) == 0:
                self.append_byte(byte)
                self.sync_index = 0
                continue

            if byte == self.sync_string[self.sync_index]:
                self.sync_index += 1
            else:
                if self.sync_index > 0:
                    for j in range(self.sync_index):
                        self.append_byte(self.sync_string[j])
                self.append_byte(byte)
                self.sync_index = 0

            # sync is complete, append newline
            if self.sync_index == len(self.sync_string):
                self.sync_index = 0
                self.append("<br>")
                self.clear()
                for sbyte in self.sync_string:
                    self.append_byte(sbyte)

        return f"<pre>{''.join(self.chars)}</pre>"
