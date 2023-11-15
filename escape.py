#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# A bashplate like python script
#
# File:    bpp.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2022-05-22
# License: MIT
# Python:  3
#
# ----------------------------------------------------------------------------
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
# https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
# https://www.ditig.com/256-colors-cheat-sheet
# https://michurin.github.io/xterm256-color-picker/
#
#

from __future__ import annotations
from copy import copy
from curses import is_term_resized
from dataclasses import dataclass
import logging
from enum import Enum


class Ascii:
    NULL = "\0"
    ETX = "\x03"  # End of text(ETX), CTRL-C
    BEL = "\a"
    BS = "\b"
    TAB = "\t"
    NL = "\n"
    VT = "\v"
    FF = "\f"
    CR = "\r"
    ESC = "\e"

    nls = ["\n", "\r\n", "\r"]

    @staticmethod
    def is_newline(s: str) -> bool:
        if s in Ascii.nls:
            return True
        return False


ascii = {
    0x00: "NULL",
    0x01: "SOH",
    0x02: "STX",
    0x03: "ETX",
    0x04: "EOT",
    0x05: "ENQ",
    0x06: "ACK",
    0x07: "BEL",  # Bell
    0x08: "BS",  # Backspace
    0x09: "TAB",  # Horizontal tab
    0x0A: "LF",  # Line feed
    0x0B: "VT",  # Vertical tab
    0x0C: "FF",  # Form feed
    0x0D: "CR",  # Carriage return
    0x0E: "SO",
    0x0F: "SI",
    0x10: "DLE",
    0x11: "DC1",
    0x12: "DC2",
    0x13: "DC3",
    0x14: "DC4",
    0x15: "NAK",
    0x16: "SYN",
    0x17: "ETB",
    0x18: "CAN",
    0x19: "EM",
    0x1A: "SUB",
    0x1B: "ESC",  # Escape
    0x1C: "FS",
    0x1D: "GS",
    0x1E: "RS",
    0x1F: "US",
    0x20: "Spc",  # Space
}


def getc(c: str) -> str:
    for a, b in ascii.items():
        if ord(c) == a:
            return b
    return c


def hex2str(c: int) -> str:
    for a, b in ascii.items():
        if c == a:
            return b
    return chr(c)


class C1(Enum):
    CSI = "["  # Control Sequence Introducer
    # OSC = "]"  # Operating System Command
    # Fs (independet function) sequences 0x60-0x7E
    # RIS = "c"  # Reset to Initial State

    # Fp (private use) sequences 0x30-0x3F
    DECSC = "7"  # Save cursor position and character attributes
    DECRC = "8"  # Restore cursor and attributes to previously saved position

    # RESERVERD = "'"  # Reserved for future standardization
    UNSUPPORTED = "UNSUPPORTED"


class CSI(Enum):
    """Control Sequence Introducer

    Args:
        Enum (_type_): _description_
    """

    CURSOR_UP = "A"
    CURSOR_DOWN = "B"
    CURSOR_FORWARD = "C"
    CURSOR_BACK = "D"
    CURSOR_NEXT_LINE = "E"
    CURSOR_PREVIOUS_LINE = "F"
    CURSOR_HORIZONTAL_ABSOLUTE = "G"
    CURSOR_POSITION = "H"
    ERASE_IN_DISPLAY = "J"
    ERASE_IN_LINE = "K"
    INSERT_LINE = "L"  # Insert line and move current line(s) down (VT102)
    DELETE_LINE = "M"  # Delete line and move lines up (VT102)
    DELETE_CHAR = "P"  # Delete character(s) from cursor position (VT102)
    SCROLL_UP = "S"  # "\e[2S" Move lines up, new lines at bottom
    SCROLL_DOWN = "T"

    HVP = "f"  #  Horizontal and Vertical Position(depends on PUM=Positioning Unit Mode)

    SGR = "m"  # Select graphics rendition (SGR)
    # AUX = "i"  # Enable/Disable aux serial port
    # DSR = "n"  # Device status report

    SET_SCROLLING_REGION = "r"
    # \e[12;24r  Set scrolling region between line 12 to 24
    # If a linefeed is received while on row 24 line 12 is removed and lines 13-24 is scrolled up

    # Private sequences
    SAVE_CURSOR_POSITION = "s"  # Save Current Cursor Position
    RESTORE_CURSOR_POSITION = "u"  # Restore Saved Curosr Position

    UNSUPPORTED = "UNSUP"
    # TEXT = "TEXT"

    @staticmethod
    def decode(s: str) -> CSI:
        if not s[0] == Escape.ESCAPE:
            return None

        tc = s[-1]  # termination character in Escape sequence

        for csi in CSI:
            if tc == csi.value:
                logging.debug(f'Found {csi}  "{Escape.to_str(s)}"')
                return csi

        logging.debug(f'Found {CSI.UNSUPPORTED}  "{Escape.to_str(s)}"')
        return CSI.UNSUPPORTED


class SGR(Enum):
    """Select Graphic Rendition

    Args:
        Enum (_type_): _description_
    """

    # SGR (Select Graphic Rendition)
    RESET = 0  # Reset all attributes
    BOLD = 1  # Bold/increased intensity
    DIM = 2  # Dim/decreased intensity
    ITALIC = 3
    UNDERLINE = 4
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    REVERSE_VIDEO = 7
    CONCEAL = 8
    CROSSED = 9
    PRIMARY = 10  # Primary (default) font

    FRACTUR = 20  # Gothic
    DOUBLE_UNDERLINE = 21

    NORMAL_INTENSITY = 22
    NOT_ITALIC = 23
    NOT_UNDERLINED = 24
    NOT_BLINKING = 25
    NOT_REVERSED = 27
    REVEAL = 28
    NOT_CROSSED = 29
    FG_COLOR_BLACK = 30
    FG_COLOR_RED = 31
    FG_COLOR_GREEN = 32
    FG_COLOR_YELLOW = 33
    FG_COLOR_BLUE = 34
    FG_COLOR_MAGENTA = 35
    FG_COLOR_CYAN = 36
    FG_COLOR_WHITE = 37

    BG_COLOR_BLACK = 40
    BG_COLOR_RED = 41
    BG_COLOR_GREEN = 42
    BG_COLOR_YELLOW = 43
    BG_COLOR_BLUE = 44
    BG_COLOR_MAGENTA = 45
    BG_COLOR_CYAN = 46
    BG_COLOR_WHITE = 47

    OVERLINE = 53
    NOT_OVERLINE = 55

    SET_FG_COLOR_DEFAULT = 39  # Set default color foreground
    SET_BG_COLOR_DEFAULT = 49  # Set default color background

    SET_FG_COLOR = 38  # Select 256 color or RGB color foreground
    SET_BG_COLOR = 48  # Select 256 color or RGB color background
    SET_UL_COLOR = 58  # Select underline color
    FRAMED = 51

    SUPERSCRIPT = 73
    SUBSCRIPT = 74

    UNSUPPORTED = 0xFFFF

    @staticmethod
    def is_sgr(s: str) -> bool:
        if s[0] == Escape.ESCAPE and s[-1] == "m":
            return True
        return False

    @staticmethod
    def find_sgr(sgr_code: str) -> SGR:
        for e in SGR:
            if sgr_code == e.value:
                return e
        return SGR.UNSUPPORTED

    @staticmethod
    def decode(s: str):
        if not SGR.is_sgr(s):
            return None

        x = s[2:-1]
        # attributes = x.split(";")
        attributes = x.replace(":", ";").split(";")
        attr_list = []
        for attr in attributes:
            if attr == "":  # If no number present it is a reset(0)
                # attr_list.append({"SGR":SGR.RESET})
                attr = "0"

            # Extended(256/Truecolor) color management
            if attr in [SGR.SET_BG_COLOR.value, SGR.SET_FG_COLOR.value]:
                logging.debug(attributes)
                # 256 color mode
                if int(attributes[1]) == 5:
                    attr_list.append(
                        {"SGR": SGR.find_sgr(attr), "color": int(attributes[2])}
                    )
                # Truecolor mode
                if int(attributes[1]) == 2:
                    # xx.append({"SGR":SGR.find_sgr(c), "color":int(sp[2])})
                    pass
                break

            # Handle underline style
            if attr == SGR.UNDERLINE.value:
                attr_list.append({"SGR": SGR.find_sgr(attr)})
                break

            # Handle underline color
            if attr == SGR.SET_UL_COLOR.value:
                break

            attr_list.append({"SGR": SGR.find_sgr(attr)})

        # if isinstance(t, SGR):
        logging.debug(f"SGR: {attr_list}")
        return attr_list


@dataclass
class EscapeObj:
    c1: C1 = C1.UNSUPPORTED
    csi: CSI = CSI.UNSUPPORTED
    sgr: SGR = SGR.UNSUPPORTED
    n: int = 1
    m: int = 1
    is_text: bool = False
    text: str = ""

    def decode(self, seq: str) -> CSI:
        if not seq[0] == Escape.ESCAPE:
            return

        self.text = Escape.to_str(seq)

        tc = seq[-1]  # termination character in Escape sequence

        for c in C1:
            if seq[1] == c.value:
                self.c1 = c

        if self.c1 == C1.UNSUPPORTED:
            # logging.debug(f'C1 unsupported:  "{self.text}"')
            return

        if seq[1] != "[":
            self.csi = CSI.UNSUPPORTED
            return

        for csi in CSI:
            if tc == csi.value:
                self.csi = csi

        if self.csi == CSI.UNSUPPORTED:
            # logging.debug(f'CSI unsupported:  "{self.text}"')
            return

        # The following CSI's has 0 as default for n
        if self.csi in [CSI.ERASE_IN_DISPLAY, CSI.ERASE_IN_LINE]:
            self.n = 0

        paramsx = seq[2:-1].replace(":", ";").split(";")
        params = [param for param in paramsx if param != ""]  # removing empty strings

        # logging.debug(f'Found {self.csi}  "{Escape.to_str(seq)}" {params}')
        if len(params) > 0:
            self.n = int(params[0])
        if len(params) > 1:
            self.m = int(params[1])

        # Decode SGR (Select Graphic Rendition)
        if self.csi == CSI.SGR:
            self.decode_sgr(seq)

    def __str__(self) -> str:
        return f"{self.csi:20} n={self.n:<2} m={self.m:<2}"

    @staticmethod
    def find_sgr(sgr_code: int) -> SGR:
        for sgr in SGR:
            if sgr_code == sgr.value:
                return sgr
        return SGR.UNSUPPORTED

    def decode_sgr(self, s: str):
        x = s[2:-1]
        attributes = x.replace(":", ";").split(";")
        attr_list = []
        for attr in attributes:
            if attr == "":  # If no number present it is a reset(0)
                attr = 0
            else:
                attr = int(attr)

            # Extended(256/Truecolor) color management
            if attr in [SGR.SET_BG_COLOR.value, SGR.SET_FG_COLOR.value]:
                # logging.debug(attributes)
                # 256 color mode
                if int(attributes[1]) == 5:
                    attr_list.append(
                        {"SGR": SGR.find_sgr(attr), "color": int(attributes[2])}
                    )
                # Truecolor mode
                if int(attributes[1]) == 2:
                    # xx.append({"SGR":SGR.find_sgr(c), "color":int(sp[2])})
                    pass
                break

            # Handle underline style
            if attr == SGR.UNDERLINE.value:
                attr_list.append({"SGR": SGR.find_sgr(attr)})
                break

            # Handle underline color
            if attr == SGR.SET_UL_COLOR.value:
                break

            attr_list.append({"SGR": SGR.find_sgr(attr)})

        # for sgr in attr_list:
        #     logging.debug(f"SGR: {sgr}")

        self.sgr = attr_list


class Escape:
    ETX = "\x03"  # End of text(ETX), CTRL-C
    ESCAPE = "\x1b"

    """ ANSI foreground colors codes """
    BLACK = "\x1b[0;30m"  # Black
    RED = "\x1b[0;31m"  # Red
    GREEN = "\x1b[0;32m"  # Green
    YELLOW = "\x1b[0;33m"  # Yellow
    BLUE = "\x1b[0;34m"  # Blue
    MAGENTA = "\x1b[0;35m"  # Magenta
    CYAN = "\x1b[0;36m"  # Cyan
    WHITE = "\x1b[0;37m"  # Gray
    DARKGRAY = "\x1b[1;30m"  # Dark Gray
    BR_RED = "\x1b[1;31m"  # Bright Red
    BR_GREEN = "\x1b[1;32m"  # Bright Green
    BR_YELLOW = "\x1b[1;33m"  # Bright Yellow
    BR_BLUE = "\x1b[1;34m"  # Bright Blue
    BR_MAGENTA = "\x1b[1;35m"  # Bright Magenta
    BR_CYAN = "\x1b[1;36m"  # Bright Cyan
    BR_WHITE = "\x1b[1;37m"  # White

    # ANSI background color codes
    #
    BG_BLACK = "\x1b[40m"  # Black
    BG_RED = "\x1b[41m"  # Red
    BG_GREEN = "\x1b[42m"  # Green
    BG_YELLOW = "\x1b[43m"  # Yellow
    BG_BLUE = "\x1b[44m"  # Blue
    BG_MAGENTA = "\x1b[45m"  # Magenta
    BG_CYAN = "\x1b[46m"  # Cyan
    BG_WHITE = "\x1b[47m"  # White

    # ANSI Text attributes
    RESET = "\x1b[0m"  # Reset attributes
    BOLD = "\x1b[1m"  # bold font
    DIM = "\x1b[2m"  # Low intensity/faint/dim
    ITALIC = "\x1b[3m"  # Low intensity/faint/dim
    UNDERLINE = "\x1b[4m"  # Underline
    SLOWBLINK = "\x1b[5m"  # Slow blink
    FASTBLINK = "\x1b[6m"  # Fast blink
    REVERSE = "\x1b[7m"  # Reverse video
    HIDE = "\x1b[8m"
    CROSSED = "\x1b[9m"  # Crossed text
    FRACTUR = "\x1b[20m"  # Gothic
    FRAMED = "\x1b[51m"  # Framed
    OVERLINE = "\x1b[53m"  # Overlined
    SUPERSCRIPT = "\x1b[73m"  # Superscript
    SUBSCRIPT = "\x1b[74m"  # Subscript
    NORMAL = "\x1b[22m"  # Normal intensity
    NOT_ITALIC = "\x1b[23m"
    NOT_UNDERLINED = "\x1b[24m"
    NOT_BLINKING = "\x1b[25m"
    NOT_REVERSED = "\x1b[27m"
    REVEAL = "\x1b[28m"
    NOT_CROSSED = "\x1b[29m"
    NOT_SSCRIPT = "\x1b[75m"
    NOT_OVERLINE = "\x1b[55m"

    END = "\x1b[m"  # Clear Attributes
    CLEAR = "\x1b[2J"
    RESET = "\x1b[m"

    WONR = "\x1b[1;47\x1b[1;31m"

    # ANSI cursor operations
    #
    UP = "\x1b[A"  # Move cursor one line up
    DOWN = "\x1b[B"  # Move cursor one line down
    FORWARD = "\x1b[C"  # Move cursor forward
    BACK = "\x1b[D"  # Move cursor backward
    RETURN = "\x1b[F"  # Move cursor to begining of line
    HIDE = "\x1b[?25l"  # Hide cursor
    SHOW = "\x1b[?25h"  # Show cursor

    KEY_HOME = "\x1b[1~"  # Home
    KEY_INSERT = "\x1b[2~"  #
    KEY_DELETE = "\x1b[3~"  #
    KEY_END = "\x1b[4~"  #
    KEY_PGUP = "\x1b[5~"  #
    KEY_PGDN = "\x1b[6~"  #
    KEY_HOME = "\x1b[7~"  #
    KEY_END = "\x1b[8~"  #
    KEY_F0 = "\x1b[10~"  # F
    KEY_F1 = "\x1b[11~"  # F
    KEY_F2 = "\x1b[12~"  # F
    KEY_F3 = "\x1b[13~"  # F
    KEY_F4 = "\x1b[14~"  # F
    KEY_F5 = "\x1b[15~"  # F
    KEY_F6 = "\x1b[17~"  # F
    KEY_F7 = "\x1b[18~"  # F
    KEY_F8 = "\x1b[19~"  # F
    KEY_F9 = "\x1b[20~"  # F
    KEY_F10 = "\x1b[21~"  # F
    KEY_F11 = "\x1b[23~"  # F
    KEY_F12 = "\x1b[24~"  # F
    KEY_F13 = "\x1b[25~"  # F
    KEY_F14 = "\x1b[26~"  # F
    KEY_F15 = "\x1b[28~"  # F
    KEY_F16 = "\x1b[29~"  # F

    E_RET = 100
    E_UP = 101
    E_DOWN = 102

    x = [RETURN, UP, DOWN]
    y = {E_RET: RETURN, E_UP: UP, E_DOWN: DOWN}

    @staticmethod
    def fg_8bit_color(c: int) -> str:
        return f"\x1b[38;5;{c}m"

    @staticmethod
    def bg_8bit_color(c: int) -> str:
        return f"\x1b[48;5;{c}m"

    @staticmethod
    def findEnd(data, idx):
        i = idx
        while (i - idx) < 12:
            ch = data.at(i)
            if ch.isalpha():
                return i
            else:
                i += 1
        return -1

    @staticmethod
    def is_escape_seq(s: str) -> bool:
        if s[0] == Escape.ESCAPE:
            return True
        else:
            return False

    @staticmethod
    def to_str(s: str) -> str:
        return (
            s.replace("\x1b", "\\e")
            .replace("\x0a", "\\n")
            .replace("\x0d", "\\r")
            .replace("\x08", "\\b")
        )


class EscapeTokenizer:
    """EscapeTokenizer"""

    def __init__(self):
        self.clear()

    def clear(self):
        self.seq = ""
        self.lbuf = []

    def append_string(self, s: str) -> None:
        self.lbuf.extend(list(s))

    def append_bytearray(self, ba: bytearray) -> None:
        utf = ba.decode("utf-8")
        self.lbuf.extend(list(utf))

    def is_csi(self) -> bool:
        """Check if a string is CSI terminated"""

        if self.seq[1] != C1.CSI.value:
            return False

        lc = ord(self.seq[-1])
        if lc == 0x5B:  # "[" is excluded as terminator, possibly wrong
            return False

        if lc >= 0x40 and lc <= 0x7E:
            return True

        return False

    def is_Fp(self) -> bool:
        """Check if independent function dequence"""

        lc = ord(self.seq[1])
        if (lc >= 0x60) and (lc <= 0x7E):
            return True

    def is_Fs(self) -> bool:
        """Check if private two character sequence"""

        lc = ord(self.seq[-1])
        if (lc >= 0x30) and (lc <= 0x3F):
            return True

    def is_terminated(self) -> bool:
        """Check if Escape sequence is terminated"""

        seq_len = len(self.seq)

        if seq_len <= 1:
            return False

        if seq_len == 2:
            if self.is_Fp() is True:
                return True

            if self.is_Fs() is True:
                return True

        if seq_len == 3 and self.seq[1] == "(":
            return True

        # return False

        if self.is_csi() is True:
            return True

        return False

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self) -> str:
        try:
            while True:
                ch = self.lbuf.pop(0)  # get next character from buffer

                if ch in [Ascii.NL, Ascii.BEL, Ascii.BS, Ascii.CR]:
                    if len(self.seq) > 0:
                        ret = self.seq
                        self.seq = ""
                        self.lbuf.insert(0, ch)
                        return ret
                    return ch

                if ch == Escape.ESCAPE:  # Escape sequence start character found
                    if len(self.seq) > 0:
                        ret = self.seq
                        self.seq = ch
                        return ret

                    self.seq = ch
                    continue

                self.seq += ch

                if self.seq[0] == Escape.ESCAPE:
                    if self.is_terminated() is True:
                        ret = self.seq
                        self.seq = ""
                        return ret

                    # if self.is_terminator(ch) is True:
                    #     ret = self.seq
                    #     self.seq = ""
                    #     return ret

        except IndexError:
            if len(self.seq) == 0:
                raise StopIteration

            if self.seq[0] == Escape.ESCAPE:
                raise StopIteration

            ret = self.seq
            self.seq = ""
            return ret


@dataclass
class TColor:
    # BLACK : str = "#2e3436"
    BLACK: str = "#000000"
    RED: str = "#cc0000"
    GREEN: str = "#4e9a06"
    YELLOW: str = "#c4a000"
    BLUE: str = "#3465a4"
    MAGENTA: str = "#75507b"
    CYAN: str = "#06989a"
    WHITE: str = "#d3d7cf"
    BRIGHT_BLACK: str = "#555753"
    BRIGHT_RED: str = "#ef2929"
    BRIGHT_GREEN: str = "#8ae234"
    BRIGHT_YELLOW: str = "#fce94f"
    BRIGHT_BLUE: str = "#729fcf"
    BRIGHT_MAGENTA: str = "#ad7fa8"
    BRIGHT_CYAN: str = "#34e2e2"
    BRIGHT_WHITE: str = "#eeeeec"


CC256 = [
    {"name": "Black (SYSTEM)", "hex": "#000000"},
    {"name": "Maroon (SYSTEM)", "hex": "#800000"},
    {"name": "Green (SYSTEM)", "hex": "#008000"},
    {"name": "Olive (SYSTEM)", "hex": "#808000"},
    {"name": "Navy (SYSTEM)", "hex": "#000080"},
    {"name": "Purple (SYSTEM)", "hex": "#800080"},
    {"name": "Teal (SYSTEM)", "hex": "#008080"},
    {"name": "Silver (SYSTEM)", "hex": "#c0c0c0"},
    {"name": "Grey (SYSTEM)", "hex": "#808080"},
    {"name": "Red (SYSTEM)", "hex": "#ff0000"},
    {"name": "Lime (SYSTEM)", "hex": "#00ff00"},
    {"name": "Yellow (SYSTEM)", "hex": "#ffff00"},
    {"name": "Blue (SYSTEM)", "hex": "#0000ff"},
    {"name": "Fuchsia (SYSTEM)", "hex": "#ff00ff"},
    {"name": "Aqua (SYSTEM)", "hex": "#00ffff"},
    {"name": "White (SYSTEM)", "hex": "#ffffff"},
    {"name": "Grey0", "hex": "#000000"},
    {"name": "NavyBlue", "hex": "#00005f"},
    {"name": "DarkBlue", "hex": "#000087"},
    {"name": "Blue3", "hex": "#0000af"},
    {"name": "Blue3", "hex": "#0000d7"},
    {"name": "Blue1", "hex": "#0000ff"},
    {"name": "DarkGreen", "hex": "#005f00"},
    {"name": "DeepSkyBlue4", "hex": "#005f5f"},
    {"name": "DeepSkyBlue4", "hex": "#005f87"},
    {"name": "DeepSkyBlue4", "hex": "#005faf"},
    {"name": "DodgerBlue3", "hex": "#005fd7"},
    {"name": "DodgerBlue2", "hex": "#005fff"},
    {"name": "Green4", "hex": "#008700"},
    {"name": "SpringGreen4", "hex": "#00875f"},
    {"name": "Turquoise4", "hex": "#008787"},
    {"name": "DeepSkyBlue3", "hex": "#0087af"},
    {"name": "DeepSkyBlue3", "hex": "#0087d7"},
    {"name": "DodgerBlue1", "hex": "#0087ff"},
    {"name": "Green3", "hex": "#00af00"},
    {"name": "SpringGreen3", "hex": "#00af5f"},
    {"name": "DarkCyan", "hex": "#00af87"},
    {"name": "LightSeaGreen", "hex": "#00afaf"},
    {"name": "DeepSkyBlue2", "hex": "#00afd7"},
    {"name": "DeepSkyBlue1", "hex": "#00afff"},
    {"name": "Green3", "hex": "#00d700"},
    {"name": "SpringGreen3", "hex": "#00d75f"},
    {"name": "SpringGreen2", "hex": "#00d787"},
    {"name": "Cyan3", "hex": "#00d7af"},
    {"name": "DarkTurquoise", "hex": "#00d7d7"},
    {"name": "Turquoise2", "hex": "#00d7ff"},
    {"name": "Green1", "hex": "#00ff00"},
    {"name": "SpringGreen2", "hex": "#00ff5f"},
    {"name": "SpringGreen1", "hex": "#00ff87"},
    {"name": "MediumSpringGreen", "hex": "#00ffaf"},
    {"name": "Cyan2", "hex": "#00ffd7"},
    {"name": "Cyan1", "hex": "#00ffff"},
    {"name": "DarkRed", "hex": "#5f0000"},
    {"name": "DeepPink4", "hex": "#5f005f"},
    {"name": "Purple4", "hex": "#5f0087"},
    {"name": "Purple4", "hex": "#5f00af"},
    {"name": "Purple3", "hex": "#5f00d7"},
    {"name": "BlueViolet", "hex": "#5f00ff"},
    {"name": "Orange4", "hex": "#5f5f00"},
    {"name": "Grey37", "hex": "#5f5f5f"},
    {"name": "MediumPurple4", "hex": "#5f5f87"},
    {"name": "SlateBlue3", "hex": "#5f5faf"},
    {"name": "SlateBlue3", "hex": "#5f5fd7"},
    {"name": "RoyalBlue1", "hex": "#5f5fff"},
    {"name": "Chartreuse4", "hex": "#5f8700"},
    {"name": "DarkSeaGreen4", "hex": "#5f875f"},
    {"name": "PaleTurquoise4", "hex": "#5f8787"},
    {"name": "SteelBlue", "hex": "#5f87af"},
    {"name": "SteelBlue3", "hex": "#5f87d7"},
    {"name": "CornflowerBlue", "hex": "#5f87ff"},
    {"name": "Chartreuse3", "hex": "#5faf00"},
    {"name": "DarkSeaGreen4", "hex": "#5faf5f"},
    {"name": "CadetBlue", "hex": "#5faf87"},
    {"name": "CadetBlue", "hex": "#5fafaf"},
    {"name": "SkyBlue3", "hex": "#5fafd7"},
    {"name": "SteelBlue1", "hex": "#5fafff"},
    {"name": "Chartreuse3", "hex": "#5fd700"},
    {"name": "PaleGreen3", "hex": "#5fd75f"},
    {"name": "SeaGreen3", "hex": "#5fd787"},
    {"name": "Aquamarine3", "hex": "#5fd7af"},
    {"name": "MediumTurquoise", "hex": "#5fd7d7"},
    {"name": "SteelBlue1", "hex": "#5fd7ff"},
    {"name": "Chartreuse2", "hex": "#5fff00"},
    {"name": "SeaGreen2", "hex": "#5fff5f"},
    {"name": "SeaGreen1", "hex": "#5fff87"},
    {"name": "SeaGreen1", "hex": "#5fffaf"},
    {"name": "Aquamarine1", "hex": "#5fffd7"},
    {"name": "DarkSlateGray2", "hex": "#5fffff"},
    {"name": "DarkRed", "hex": "#870000"},
    {"name": "DeepPink4", "hex": "#87005f"},
    {"name": "DarkMagenta", "hex": "#870087"},
    {"name": "DarkMagenta", "hex": "#8700af"},
    {"name": "DarkViolet", "hex": "#8700d7"},
    {"name": "Purple", "hex": "#8700ff"},
    {"name": "Orange4", "hex": "#875f00"},
    {"name": "LightPink4", "hex": "#875f5f"},
    {"name": "Plum4", "hex": "#875f87"},
    {"name": "MediumPurple3", "hex": "#875faf"},
    {"name": "MediumPurple3", "hex": "#875fd7"},
    {"name": "SlateBlue1", "hex": "#875fff"},
    {"name": "Yellow4", "hex": "#878700"},
    {"name": "Wheat4", "hex": "#87875f"},
    {"name": "Grey53", "hex": "#878787"},
    {"name": "LightSlateGrey", "hex": "#8787af"},
    {"name": "MediumPurple", "hex": "#8787d7"},
    {"name": "LightSlateBlue", "hex": "#8787ff"},
    {"name": "Yellow4", "hex": "#87af00"},
    {"name": "DarkOliveGreen3", "hex": "#87af5f"},
    {"name": "DarkSeaGreen", "hex": "#87af87"},
    {"name": "LightSkyBlue3", "hex": "#87afaf"},
    {"name": "LightSkyBlue3", "hex": "#87afd7"},
    {"name": "SkyBlue2", "hex": "#87afff"},
    {"name": "Chartreuse2", "hex": "#87d700"},
    {"name": "DarkOliveGreen3", "hex": "#87d75f"},
    {"name": "PaleGreen3", "hex": "#87d787"},
    {"name": "DarkSeaGreen3", "hex": "#87d7af"},
    {"name": "DarkSlateGray3", "hex": "#87d7d7"},
    {"name": "SkyBlue1", "hex": "#87d7ff"},
    {"name": "Chartreuse1", "hex": "#87ff00"},
    {"name": "LightGreen", "hex": "#87ff5f"},
    {"name": "LightGreen", "hex": "#87ff87"},
    {"name": "PaleGreen1", "hex": "#87ffaf"},
    {"name": "Aquamarine1", "hex": "#87ffd7"},
    {"name": "DarkSlateGray1", "hex": "#87ffff"},
    {"name": "Red3", "hex": "#af0000"},
    {"name": "DeepPink4", "hex": "#af005f"},
    {"name": "MediumVioletRed", "hex": "#af0087"},
    {"name": "Magenta3", "hex": "#af00af"},
    {"name": "DarkViolet", "hex": "#af00d7"},
    {"name": "Purple", "hex": "#af00ff"},
    {"name": "DarkOrange3", "hex": "#af5f00"},
    {"name": "IndianRed", "hex": "#af5f5f"},
    {"name": "HotPink3", "hex": "#af5f87"},
    {"name": "MediumOrchid3", "hex": "#af5faf"},
    {"name": "MediumOrchid", "hex": "#af5fd7"},
    {"name": "MediumPurple2", "hex": "#af5fff"},
    {"name": "DarkGoldenrod", "hex": "#af8700"},
    {"name": "LightSalmon3", "hex": "#af875f"},
    {"name": "RosyBrown", "hex": "#af8787"},
    {"name": "Grey63", "hex": "#af87af"},
    {"name": "MediumPurple2", "hex": "#af87d7"},
    {"name": "MediumPurple1", "hex": "#af87ff"},
    {"name": "Gold3", "hex": "#afaf00"},
    {"name": "DarkKhaki", "hex": "#afaf5f"},
    {"name": "NavajoWhite3", "hex": "#afaf87"},
    {"name": "Grey69", "hex": "#afafaf"},
    {"name": "LightSteelBlue3", "hex": "#afafd7"},
    {"name": "LightSteelBlue", "hex": "#afafff"},
    {"name": "Yellow3", "hex": "#afd700"},
    {"name": "DarkOliveGreen3", "hex": "#afd75f"},
    {"name": "DarkSeaGreen3", "hex": "#afd787"},
    {"name": "DarkSeaGreen2", "hex": "#afd7af"},
    {"name": "LightCyan3", "hex": "#afd7d7"},
    {"name": "LightSkyBlue1", "hex": "#afd7ff"},
    {"name": "GreenYellow", "hex": "#afff00"},
    {"name": "DarkOliveGreen2", "hex": "#afff5f"},
    {"name": "PaleGreen1", "hex": "#afff87"},
    {"name": "DarkSeaGreen2", "hex": "#afffaf"},
    {"name": "DarkSeaGreen1", "hex": "#afffd7"},
    {"name": "PaleTurquoise1", "hex": "#afffff"},
    {"name": "Red3", "hex": "#d70000"},
    {"name": "DeepPink3", "hex": "#d7005f"},
    {"name": "DeepPink3", "hex": "#d70087"},
    {"name": "Magenta3", "hex": "#d700af"},
    {"name": "Magenta3", "hex": "#d700d7"},
    {"name": "Magenta2", "hex": "#d700ff"},
    {"name": "DarkOrange3", "hex": "#d75f00"},
    {"name": "IndianRed", "hex": "#d75f5f"},
    {"name": "HotPink3", "hex": "#d75f87"},
    {"name": "HotPink2", "hex": "#d75faf"},
    {"name": "Orchid", "hex": "#d75fd7"},
    {"name": "MediumOrchid1", "hex": "#d75fff"},
    {"name": "Orange3", "hex": "#d78700"},
    {"name": "LightSalmon3", "hex": "#d7875f"},
    {"name": "LightPink3", "hex": "#d78787"},
    {"name": "Pink3", "hex": "#d787af"},
    {"name": "Plum3", "hex": "#d787d7"},
    {"name": "Violet", "hex": "#d787ff"},
    {"name": "Gold3", "hex": "#d7af00"},
    {"name": "LightGoldenrod3", "hex": "#d7af5f"},
    {"name": "Tan", "hex": "#d7af87"},
    {"name": "MistyRose3", "hex": "#d7afaf"},
    {"name": "Thistle3", "hex": "#d7afd7"},
    {"name": "Plum2", "hex": "#d7afff"},
    {"name": "Yellow3", "hex": "#d7d700"},
    {"name": "Khaki3", "hex": "#d7d75f"},
    {"name": "LightGoldenrod2", "hex": "#d7d787"},
    {"name": "LightYellow3", "hex": "#d7d7af"},
    {"name": "Grey84", "hex": "#d7d7d7"},
    {"name": "LightSteelBlue1", "hex": "#d7d7ff"},
    {"name": "Yellow2", "hex": "#d7ff00"},
    {"name": "DarkOliveGreen1", "hex": "#d7ff5f"},
    {"name": "DarkOliveGreen1", "hex": "#d7ff87"},
    {"name": "DarkSeaGreen1", "hex": "#d7ffaf"},
    {"name": "Honeydew2", "hex": "#d7ffd7"},
    {"name": "LightCyan1", "hex": "#d7ffff"},
    {"name": "Red1", "hex": "#ff0000"},
    {"name": "DeepPink2", "hex": "#ff005f"},
    {"name": "DeepPink1", "hex": "#ff0087"},
    {"name": "DeepPink1", "hex": "#ff00af"},
    {"name": "Magenta2", "hex": "#ff00d7"},
    {"name": "Magenta1", "hex": "#ff00ff"},
    {"name": "OrangeRed1", "hex": "#ff5f00"},
    {"name": "IndianRed1", "hex": "#ff5f5f"},
    {"name": "IndianRed1", "hex": "#ff5f87"},
    {"name": "HotPink", "hex": "#ff5faf"},
    {"name": "HotPink", "hex": "#ff5fd7"},
    {"name": "MediumOrchid1", "hex": "#ff5fff"},
    {"name": "DarkOrange", "hex": "#ff8700"},
    {"name": "Salmon1", "hex": "#ff875f"},
    {"name": "LightCoral", "hex": "#ff8787"},
    {"name": "PaleVioletRed1", "hex": "#ff87af"},
    {"name": "Orchid2", "hex": "#ff87d7"},
    {"name": "Orchid1", "hex": "#ff87ff"},
    {"name": "Orange1", "hex": "#ffaf00"},
    {"name": "SandyBrown", "hex": "#ffaf5f"},
    {"name": "LightSalmon1", "hex": "#ffaf87"},
    {"name": "LightPink1", "hex": "#ffafaf"},
    {"name": "Pink1", "hex": "#ffafd7"},
    {"name": "Plum1", "hex": "#ffafff"},
    {"name": "Gold1", "hex": "#ffd700"},
    {"name": "LightGoldenrod2", "hex": "#ffd75f"},
    {"name": "LightGoldenrod2", "hex": "#ffd787"},
    {"name": "NavajoWhite1", "hex": "#ffd7af"},
    {"name": "MistyRose1", "hex": "#ffd7d7"},
    {"name": "Thistle1", "hex": "#ffd7ff"},
    {"name": "Yellow1", "hex": "#ffff00"},
    {"name": "LightGoldenrod1", "hex": "#ffff5f"},
    {"name": "Khaki1", "hex": "#ffff87"},
    {"name": "Wheat1", "hex": "#ffffaf"},
    {"name": "Cornsilk1", "hex": "#ffffd7"},
    {"name": "Grey100", "hex": "#ffffff"},
    {"name": "Grey3", "hex": "#080808"},
    {"name": "Grey7", "hex": "#121212"},
    {"name": "Grey11", "hex": "#1c1c1c"},
    {"name": "Grey15", "hex": "#262626"},
    {"name": "Grey19", "hex": "#303030"},
    {"name": "Grey23", "hex": "#3a3a3a"},
    {"name": "Grey27", "hex": "#444444"},
    {"name": "Grey30", "hex": "#4e4e4e"},
    {"name": "Grey35", "hex": "#585858"},
    {"name": "Grey39", "hex": "#626262"},
    {"name": "Grey42", "hex": "#6c6c6c"},
    {"name": "Grey46", "hex": "#767676"},
    {"name": "Grey50", "hex": "#808080"},
    {"name": "Grey54", "hex": "#8a8a8a"},
    {"name": "Grey58", "hex": "#949494"},
    {"name": "Grey62", "hex": "#9e9e9e"},
    {"name": "Grey66", "hex": "#a8a8a8"},
    {"name": "Grey70", "hex": "#b2b2b2"},
    {"name": "Grey74", "hex": "#bcbcbc"},
    {"name": "Grey78", "hex": "#c6c6c6"},
    {"name": "Grey82", "hex": "#d0d0d0"},
    {"name": "Grey85", "hex": "#dadada"},
    {"name": "Grey89", "hex": "#e4e4e4"},
    {"name": "Grey93", "hex": "#eeeeee"},
]


sgr_to_escape_color = {
    SGR.FG_COLOR_BLACK: TColor.BLACK,
    SGR.FG_COLOR_RED: TColor.RED,
    SGR.FG_COLOR_GREEN: TColor.GREEN,
    SGR.FG_COLOR_YELLOW: TColor.YELLOW,
    SGR.FG_COLOR_BLUE: TColor.BLUE,
    SGR.FG_COLOR_MAGENTA: TColor.MAGENTA,
    SGR.FG_COLOR_CYAN: TColor.CYAN,
    SGR.FG_COLOR_WHITE: TColor.WHITE,
    SGR.BG_COLOR_BLACK: TColor.BLACK,
    SGR.BG_COLOR_RED: TColor.RED,
    SGR.BG_COLOR_GREEN: TColor.GREEN,
    SGR.BG_COLOR_YELLOW: TColor.YELLOW,
    SGR.BG_COLOR_BLUE: TColor.BLUE,
    SGR.BG_COLOR_MAGENTA: TColor.MAGENTA,
    SGR.BG_COLOR_CYAN: TColor.CYAN,
    SGR.BG_COLOR_WHITE: TColor.WHITE,
}


sgr_to_escape_color_bold = {
    SGR.FG_COLOR_BLACK: TColor.BRIGHT_BLACK,
    SGR.FG_COLOR_RED: TColor.BRIGHT_RED,
    SGR.FG_COLOR_GREEN: TColor.BRIGHT_GREEN,
    SGR.FG_COLOR_YELLOW: TColor.BRIGHT_YELLOW,
    SGR.FG_COLOR_BLUE: TColor.BRIGHT_BLUE,
    SGR.FG_COLOR_MAGENTA: TColor.BRIGHT_MAGENTA,
    SGR.FG_COLOR_CYAN: TColor.BRIGHT_CYAN,
    SGR.FG_COLOR_WHITE: TColor.BRIGHT_WHITE,
}


@dataclass
class TerminalCoordinate:
    row: int = 1
    column: int = 1


@dataclass
class TerminalAttributeState:
    BOLD: bool = False
    DIM: bool = False
    ITALIC: bool = False
    CROSSED: bool = False
    UNDERLINE: bool = False
    SUPERSCRIPT: bool = False
    SUBSCRIPT: bool = False
    REVERSE: bool = False
    OVERLINE: bool = False
    FG_COLOR: str = TColor.WHITE
    BG_COLOR: str = TColor.BLACK
    CURSOR: bool = False
    DEFAULT_FG_COLOR: str = TColor.WHITE
    DEFAULT_BG_COLOR: str = TColor.BLACK

    def reset(self):
        self.BOLD = False
        self.DIM = False
        self.ITALIC = False
        self.CROSSED = False
        self.UNDERLINE = False
        self.SUPERSCRIPT = False
        self.SUBSCRIPT = False
        self.REVERSE = False
        self.OVERLINE = False
        self.FG_COLOR = self.DEFAULT_FG_COLOR
        self.BG_COLOR = self.DEFAULT_BG_COLOR
        # self.FG_COLOR = TColor.WHITE
        # self.BG_COLOR = TColor.BLACK
        self.CURSOR = False


class TerminalCharacter:
    def __init__(self, ch: str, tas: TerminalAttributeState):
        self.tas = TerminalAttributeState()
        self.tas = copy(tas)
        self.ch = ch
        self.cursor: bool = False


class TerminalLine:
    def __init__(
        self, tas: TerminalAttributeState, id: int = 0, columns: int = 80
    ) -> None:
        self.line = []
        for i in range(0, columns):
            self.line.append(TerminalCharacter(" ", tas))
        self.id = id
        self.text = ""
        self.changed = False
        self.cursor = None

    def __str__(self) -> str:
        text = ""
        for tc in self.line:
            text += tc.ch

        return text

    def clear(self, tas):
        for ch in self.line:
            ch.tas = tas
            ch.ch = " "

    def reset(self):
        self.changed = False

    def has_changed(self, cursor: TerminalCoordinate = None) -> bool:
        # if cursor is not None it means that the cursor is present on this particular row
        self.cursor = cursor
        return self.changed

    def is_reversed(self, tas: TerminalAttributeState) -> bool:
        if tas.CURSOR is True:
            return not tas.REVERSE

        return tas.REVERSE

    def attr_html(self, data: str, tas: TerminalAttributeState) -> str:
        # if tas.REVERSE:
        if self.is_reversed(tas):
            bg_color = tas.FG_COLOR
            fg_color = tas.BG_COLOR
        else:
            fg_color = tas.FG_COLOR
            bg_color = tas.BG_COLOR

        # b = f'<span style="color:{fg_color};background-color:{bg_color};font-size:10pt;line-height:1.38;'
        b = f'<span style="color:{fg_color};background-color:{bg_color};font-size:10pt;'

        if tas.BOLD:
            b += "font-weight:bold;"
        if tas.ITALIC:
            b += "font-style:italic;"
        if tas.UNDERLINE:
            b += "text-decoration:underline;"
        if tas.CROSSED:
            b += "text-decoration:line-through;"
        if tas.OVERLINE:
            b += "text-decoration:overline;"

        b += '">'
        b += data.replace(" ", "&nbsp;").replace("<", "&lt;").replace("<", "&gt;")
        b += "</span>"
        return b

    def line_to_html(self) -> str:
        html = ""
        text = ""
        for idx, tc in enumerate(self.line):
            if idx == 0:
                tas = tc.tas

            if self.cursor is not None:
                # print("XXXX")
                if idx == (self.cursor.column - 1):
                    tas.CURSOR = True
                else:
                    tas.CURSOR = False

            else:
                tas.CURSOR = False

            if tas == tc.tas:
                text += tc.ch
            else:
                html += self.attr_html(text, tas)
                text = tc.ch
                tas = tc.tas

        if len(text) > 0:
            html += self.attr_html(text, tas)

        return html

    def append(self, text: str, tas: TerminalAttributeState, pos: int) -> int:
        # print(f"Append: {text}   Pos: {pos}")
        i = pos - 1
        for ch in text:
            tc = TerminalCharacter(ch, tas)
            try:
                self.line[i] = tc
            except IndexError:
                self.line.append(tc)
            i += 1
        self.update()
        return i + 1

    def erase(self, tas: TerminalAttributeState):
        self.line = []
        # tas = TerminalAttributeState()
        for _ in range(80):
            self.line.append(TerminalCharacter(" ", tas))
        self.update()

    def delete_char(self, column: int, n: int):
        for i in range(column, column + n):
            print(f"Deleting: {self.line[i-1].ch}")
            self.line.pop(i - 1)
        self.update()

    def erase_in_line(self, pos: int, tas, mode: int):
        if mode == 0:  # erase after pos
            erange = range(pos - 1, len(self.line))
        elif mode == 1:  # erase before pos
            erange = range(0, pos)
        elif mode == 2:  # erase entire line
            erange = range(0, len(self.line))

        for i in erange:
            try:
                self.line[i] = TerminalCharacter(" ", tas)
            except IndexError:
                self.line.append(TerminalCharacter(" ", tas))
        self.update()

    def update(self):
        self.changed = True
        self.text = str(self)


class TerminalState(TerminalAttributeState):
    def __init__(self) -> None:
        self.et = EscapeTokenizer()
        self.line_id = 0
        self.tas = TerminalAttributeState()
        self.default_fg_color = TColor.WHITE
        self.default_bg_color = TColor.BLACK
        self.reset()

    def reset(self):
        self.cursor = TerminalCoordinate()
        self.saved_cursor = TerminalCoordinate()
        self.max = TerminalCoordinate(row=24, column=80)
        self.lines: list[TerminalLine] = []
        for _ in range(0, self.max.row):
            self.new_line()
        self.et.clear()
        self.reset_attr()

    def reset_attr(self):
        self.tas.reset()

    def pos_str(self) -> str:
        ps = f"{self.cursor.row=} {self.cursor.column=}"
        return ps

    def clear_line(self, line: int):
        self.lines[self.max.row - line].clear(self.tas)

        # For some reason the following line is needed.
        # A guess is that it might have with html rendering to do
        self.lines[self.max.row - line].append(" ", self.tas, 1)

    def delete(self, n: int = 1):
        for i in range(self.max.row - self.cursor.row, -1, -1):
            self.lines[i].line = self.lines[i - 1].line
            self.lines[i].changed = True

        self.clear_line(self.max.row)

    def insert(self, n: int = 1):
        """insert n row(s) at cursor, existing rows scroll down"""

        pos = self.max.row - self.cursor.row
        logging.debug(f"Insert at: {pos}")

        for i in range(0, pos + 1):
            self.lines[i].line = self.lines[i + 1].line
            self.lines[i].changed = True

        self.clear_line(self.cursor.row)

    def delete_char(self, n: int = 1):
        self.lines[self.max.row - self.cursor.row].delete_char(self.cursor.column, n)

    def new_line(self) -> TerminalLine:
        nl = TerminalLine(tas=self.tas, id=self.line_id, columns=self.max.column)
        nl.append(" ", self.tas, 0)  # For some reason needed
        self.line_id += 1
        self.lines.insert(0, nl)

    def set_pos(self, x=None, y=None):
        if x is not None:
            self.cursor.column = x
            if self.cursor.column < 1:
                self.cursor.column = 1

        if y is not None:
            self.cursor.row = y
            if self.cursor.row < 1:
                self.cursor.row = 1
            if self.cursor.row > self.max.row:
                self.cursor.row = self.max.row

    def erase_line(self, line):
        self.lines[self.max.row - line].erase()

    def erase_in_line(self, mode):
        logging.debug(
            f"Erase in line: {self.cursor.row=}  {self.cursor.column=} {mode=}"
        )
        self.lines[self.max.row - self.cursor.row].erase_in_line(
            self.cursor.column, self.tas, mode
        )

    def erase_in_display(self, mode):
        if mode == 0:  # Clear from cursor to end of screen
            for line in range(self.cursor.row, self.max.row + 1):
                self.lines[self.max.row - line].erase_in_line(1, self.tas, 2)
        elif mode == 1:  # Clear from cursor to beginning of screen
            for line in range(1, self.cursor.row):
                self.lines[self.max.row - line].erase_in_line(1, self.tas, 2)
        elif mode == 2:  # Clear entire screen
            for line in range(1, self.max.row):
                self.lines[self.max.row - line].erase_in_line(1, self.tas, 2)

    def append(self, text):
        self.cursor.column = self.lines[self.max.row - self.cursor.row].append(
            text, self.tas, self.cursor.column
        )
        tok_str = f'"{text}"'
        logging.debug(f"(Text): {tok_str}")

    def update(self, s: str) -> list:
        self.et.append_string(s)
        for i in range(0, 24):
            self.lines[i].reset()

        for token in self.et:
            if Escape.is_escape_seq(token):
                eo = EscapeObj()
                eo.decode(token)

                if eo.c1 == C1.DECSC:  # Save cursor and attributes
                    self.saved_cursor = copy(self.cursor)
                    self.saved_tas = copy(self.tas)

                if eo.c1 == C1.DECRC:  # Restore cursor and attributes
                    self.cursor = copy(self.saved_cursor)
                    self.tas = copy(self.saved_tas)

                if eo.c1 == C1.CSI:
                    if eo.csi == CSI.CURSOR_UP:
                        self.set_pos(y=(self.cursor.row - eo.n))

                    if eo.csi == CSI.CURSOR_DOWN:
                        self.set_pos(y=(self.cursor.row + eo.n))

                    if eo.csi == CSI.CURSOR_FORWARD:
                        self.set_pos(x=(self.cursor.column + eo.n))

                    if eo.csi == CSI.CURSOR_BACK:
                        self.set_pos(x=(self.cursor.column - eo.n))

                    if eo.csi == CSI.CURSOR_NEXT_LINE:
                        self.set_pos(x=1, y=(self.cursor.row + eo.n))

                    if eo.csi == CSI.CURSOR_PREVIOUS_LINE:
                        self.set_pos(x=1, y=(self.cursor.row - eo.n))

                    if eo.csi == CSI.CURSOR_POSITION:
                        self.set_pos(x=eo.m, y=eo.n)

                    # Horizontal and Vertical Position(depends on PUM)
                    if eo.csi == CSI.HVP:
                        self.set_pos(x=eo.m, y=eo.n)

                    if eo.csi == CSI.ERASE_IN_DISPLAY:
                        self.erase_in_display(eo.n)

                    if eo.csi == CSI.ERASE_IN_LINE:
                        self.erase_in_line(eo.n)

                    if eo.csi == CSI.SAVE_CURSOR_POSITION:
                        self.saved_cursor = copy(self.cursor)

                    if eo.csi == CSI.RESTORE_CURSOR_POSITION:
                        self.cursor = copy(self.saved_cursor)

                    if eo.csi == CSI.INSERT_LINE:
                        self.insert(eo.n)

                    if eo.csi == CSI.DELETE_LINE:
                        self.delete(eo.n)

                    if eo.csi == CSI.DELETE_CHAR:
                        self.delete_char(eo.n)

                    if eo.csi == CSI.SET_SCROLLING_REGION:
                        logging.debug(f"{eo.csi.name} is not implemented")

                    if eo.csi == CSI.SGR:
                        for s in eo.sgr:
                            a = s["SGR"]
                            if a == SGR.BOLD:
                                self.tas.BOLD = True

                            if a == SGR.ITALIC:
                                self.tas.ITALIC = True

                            if a == SGR.NOT_ITALIC:
                                self.tas.ITALIC = False

                            if a == SGR.UNDERLINE:
                                self.tas.UNDERLINE = True

                            if a == SGR.NOT_UNDERLINED:
                                self.tas.UNDERLINE = False

                            if a == SGR.CROSSED:
                                self.tas.CROSSED = True

                            if a == SGR.NOT_CROSSED:
                                self.tas.CROSSED = False

                            if a == SGR.SUPERSCRIPT:
                                self.tas.SUPERSCRIPT = True

                            if a == SGR.SUBSCRIPT:
                                self.tas.SUBSCRIPT = True

                            if a == SGR.OVERLINE:
                                self.tas.OVERLINE = True
                                self.tas.UNDERLINE = False
                                self.tas.CROSSED = False

                            if a == SGR.NOT_OVERLINE:
                                self.tas.OVERLINE = False

                            if a == SGR.NORMAL_INTENSITY:
                                self.tas.BOLD = False
                                self.tas.DIM = False

                            if a == SGR.REVERSE_VIDEO:
                                self.tas.REVERSE = True

                            if a == SGR.NOT_REVERSED:
                                self.tas.REVERSE = False

                            if a == SGR.RESET:
                                self.tas.reset()

                            if a == SGR.SLOW_BLINK:
                                self.BLINKING = True

                            if a == SGR.NOT_BLINKING:
                                self.BLINKING = False

                            if a in [
                                SGR.FG_COLOR_BLACK,
                                SGR.FG_COLOR_RED,
                                SGR.FG_COLOR_GREEN,
                                SGR.FG_COLOR_YELLOW,
                                SGR.FG_COLOR_BLUE,
                                SGR.FG_COLOR_MAGENTA,
                                SGR.FG_COLOR_CYAN,
                                SGR.FG_COLOR_WHITE,
                            ]:
                                if self.BOLD:
                                    self.tas.FG_COLOR = sgr_to_escape_color_bold[a]
                                else:
                                    self.tas.FG_COLOR = sgr_to_escape_color[a]

                            if a in [
                                SGR.BG_COLOR_BLACK,
                                SGR.BG_COLOR_RED,
                                SGR.BG_COLOR_GREEN,
                                SGR.BG_COLOR_YELLOW,
                                SGR.BG_COLOR_BLUE,
                                SGR.BG_COLOR_MAGENTA,
                                SGR.BG_COLOR_CYAN,
                                SGR.BG_COLOR_WHITE,
                            ]:
                                self.tas.BG_COLOR = sgr_to_escape_color[a]

                            if a == SGR.SET_FG_COLOR:
                                self.tas.FG_COLOR = CC256[s["color"]]["hex"]

                            if a == SGR.SET_BG_COLOR:
                                self.tas.BG_COLOR = CC256[s["color"]]["hex"]

                            if a == SGR.SET_FG_COLOR_DEFAULT:
                                self.tas.FG_COLOR = self.DEFAULT_FG_COLOR

                            if a == SGR.SET_BG_COLOR_DEFAULT:
                                self.tas.BG_COLOR = self.DEFAULT_BG_COLOR

                if eo.c1 == C1.CSI:
                    if eo.csi == CSI.SGR:
                        for i, s in enumerate(eo.sgr):
                            if i == 0:
                                logging.debug(f'(SGR):  {str(s):29}  "{str(eo.text)}"')
                            else:
                                logging.debug(f"            {str(s):36}")
                    else:
                        t = f'"{str(eo.text)}"'
                        logging.debug(f"(CSI):  {str(eo):34} {t:12} {self.pos_str()}")
                else:
                    logging.debug(f'(C1):   {eo.c1:20}  "{str(eo.text)}"')
                continue

            if token == Ascii.CR:  # carriage return
                self.set_pos(x=1)
                logging.debug(
                    f"(CR)    Carriage Return                             {self.pos_str()}"
                )
                continue

            if token == Ascii.BS:  # backspace
                self.set_pos(x=(self.cursor.column - 1))
                logging.debug(
                    f"(BS)    Backspace                                   {self.pos_str()}"
                )
                continue

            if token == Ascii.NL:  # newline
                if (self.cursor.row) >= self.max.row:
                    self.new_line()

                self.set_pos(x=1, y=(self.cursor.row + 1))

                logging.debug(
                    f"(NL)    Newline                                     {self.pos_str()}"
                )
                continue

            if token in [Ascii.BEL]:  # bell
                continue

            # Adding normal text
            self.append(token)

        lul = []
        for i in range(self.max.row - 1, -1, -1):
            if (i + 1) == self.cursor.row:
                cur = copy(self.cursor)
                logging.debug(f"Cursor on: {self.cursor}")
            else:
                cur = None

            if self.lines[i].has_changed(cur) is True:
                lul.append(self.lines[i])
        return lul


FLAG_BLUE = "\x1b[48;5;20m"
FLAG_YELLOW = "\x1b[48;5;226m"

flag = f"""
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Escape.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Escape.END}
{FLAG_YELLOW}                 {Escape.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Escape.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Escape.END}
"""
escape_attribute_test = f"""  
{Escape.UNDERLINE}Font attributes{Escape.END}
{Escape.RESET}Normal text         {Escape.RESET}
{Escape.BOLD}Bold text           {Escape.NORMAL}Not Bold text{Escape.RESET}
{Escape.DIM}Dim text            {Escape.NORMAL}Not dim text{Escape.RESET}
{Escape.ITALIC}Italic text         {Escape.NOT_ITALIC}Not italic text{Escape.RESET}
{Escape.UNDERLINE}Underline text      {Escape.NOT_UNDERLINED}Not underline text{Escape.RESET}
{Escape.SLOWBLINK}Slow blinking text  {Escape.NOT_BLINKING}Not blinking text{Escape.RESET}
{Escape.FASTBLINK}Fast blinking text  {Escape.NOT_BLINKING}Not blinking text{Escape.RESET}
{Escape.FRAMED}Framed text         {Escape.RESET}
{Escape.SUBSCRIPT}Subscript text      {Escape.NOT_SSCRIPT}Not subscript text{Escape.RESET}
{Escape.SUPERSCRIPT}Superscript text    {Escape.NOT_SSCRIPT}Not superscript text{Escape.RESET}
{Escape.FRACTUR}Fractur/Gothic text {Escape.RESET}
{Escape.CROSSED}Crossed text        {Escape.NOT_CROSSED}Not crossed text{Escape.RESET}
{Escape.OVERLINE}Overlined text      {Escape.NOT_OVERLINE}Not overlined text{Escape.RESET}
{Escape.REVERSE}Reversed text       {Escape.NOT_REVERSED}Not reversed text{Escape.RESET}

{Escape.BOLD}{Escape.ITALIC}{Escape.UNDERLINE}Bold and italic and underlined{Escape.RESET}

{Escape.UNDERLINE}Standard foreground color attributes{Escape.END}

{Escape.BLACK}Black{Escape.END} {Escape.DARKGRAY}Dark Gray{Escape.END}
{Escape.RED}Red{Escape.RESET}     {Escape.BR_RED}Bright Red{Escape.END}
{Escape.GREEN}Green{Escape.END}   {Escape.BR_GREEN}Bright Green{Escape.END}
{Escape.YELLOW}Yellow{Escape.END}  {Escape.BR_YELLOW}Bright Yellow{Escape.END}
{Escape.BLUE}Blue{Escape.END}    {Escape.BR_BLUE}Bright Blue{Escape.END}
{Escape.MAGENTA}Magenta{Escape.END} {Escape.BR_MAGENTA}Bright Magenta{Escape.END}
{Escape.CYAN}Cyan{Escape.END}    {Escape.BR_CYAN}Bright Cyan{Escape.END}
{Escape.WHITE}White{Escape.END}   {Escape.BR_WHITE}Bright White{Escape.END}

{Escape.UNDERLINE}Standard background color attributes{Escape.END}

{Escape.BG_BLACK} Black {Escape.END}
{Escape.BG_RED} Red {Escape.END}
{Escape.BG_GREEN} Green {Escape.END}
{Escape.BG_YELLOW} Yellow {Escape.END}
{Escape.BG_BLUE} Blue {Escape.END}
{Escape.BG_MAGENTA} Magenta {Escape.END}
{Escape.BG_CYAN} Cyan {Escape.END}
"""

cursor_test = f"""
{Escape.DOWN} asdf {Escape.UP}  {Escape.BACK} {Escape.FORWARD} {Escape.FRACTUR}
"""


def color_256_test():
    buf = ""
    for c in range(0, 8):
        buf += f"{Escape.fg_8bit_color(c)}{c:^7}"

    buf += "\n"
    for c in range(8, 16):
        buf += f"{Escape.fg_8bit_color(c)}{c:^7}"
    buf += "\n\n"
    for r in range(0, 36):
        x = 16 + r * 6
        buf2 = ""
        for c in range(x, x + 6):
            buf += f"{Escape.fg_8bit_color(c)}{c:>5}"
            buf2 += f"{Escape.BLACK}{Escape.bg_8bit_color(c)}{c:^5}{Escape.RESET} "

        buf += "  " + buf2

        buf += "\n"

    buf += "\n"

    for c in range(232, 244):
        buf += f"{Escape.fg_8bit_color(c)}{c:>3} "
    buf += "\n"
    for c in range(244, 256):
        buf += f"{Escape.fg_8bit_color(c)}{c:>3} "
    buf += "\n"

    return buf


incomplete_escape_sequence = f"""
{Escape.BR_MAGENTA}Some colored text{Escape.END}
{Escape.GREEN}Some more text with incomplete escape sequence \x1b["""

end_with_newline = "Some text with newline end\n"


def main() -> None:
    logging.basicConfig(
        format="[%(levelname)s] Line: %(lineno)d %(message)s", level=logging.DEBUG
    )

    print(escape_attribute_test)
    # print(flag)

    # dec = EscapeDecoder()
    # dec.append_string(f"Normal color {Esc.RED}Red color {Esc.END}More normal color {Esc.BLUE}Blue angels {Esc.END}White end")
    # for x in dec:
    #     print(f"{x}")

    # print(escape_attribute_test)
    # dec2 = EscapeTokenizer()
    # dec2.append_string(escape_attribute_test)
    # for x in dec2:
    #     pass
    # print(escape_attribute_test)
    # dec2 = EscapeDecoder()
    # dec2.append_string(escape_attribute_test)
    # for x in dec2:
    #     pass

    # print(escape_attribute_test.replace("\x1b", "\\x1b").replace("\x0a", "\\n").replace("\x0d", '\\c'))

    # res = subprocess.Popen(["pmg"], shell=False, stdout=subprocess.PIPE)
    # out, err = res.communicate()
    # dec3 = EscapeDecoder()
    # dec3.append_bytearray(out)
    # #for x in dec3:
    # #    pass

    # dec4 = EscapeDecoder()
    # dec4.append_string(incomplete_escape_sequence)
    # for x in dec4:
    #     pass

    # dec5 = EscapeDecoder()
    # dec5.append_string(end_with_newline)
    # for x in dec5:
    #     pass

    # dec6 = EscapeDecoder()
    # dec6.append_string(cursor_test)
    # for x in dec6:
    #     pass

    # dec6 = EscapeTokenizer()
    # dec6.append_string(cursor_test)
    # for x in dec6:
    #     pass

    et = TerminalState()
    et.update(escape_attribute_test)
    print("Buf:\n" + et.html_buf)


if __name__ == "__main__":
    main()
