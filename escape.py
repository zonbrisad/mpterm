#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
# A bashplate like python script
#
# File:    bpp.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2022-05-22
# License: MIT
# Python:  3
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
#

from __future__ import annotations
from dataclasses import dataclass
import subprocess
import enum
import logging
import os
from enum import Enum, auto

class Ascii:
    NULL = "\0"
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

ascii = {  0x00:"NULL",
           0x01:"SOH",
           0x02:"STX",
           0x03:"ETX",
           0x04:"EOT",
           0x05:"ENQ",
           0x06:"ACK",
           0x07:"BEL",
           0x08:"BS",
           0x09:"TAB", # Horizontal tab
           0x0A:"LF",  # Line feed
           0x0B:"VT",  # Vertical tab
           0x0C:"FF",  # Form feed
           0x0D:"CR",  # Carriage return
           0x0E:"SO",
           0x0F:"SI",
           0x10:"DLE",
           0x11:"DC1",
           0x12:"DC2",
           0x13:"DC3",
           0x14:"DC4",
           0x15:"NAK",
           0x16:"SYN",
           0x17:"ETB",
           0x18:"CAN",
           0x19:"EM",
           0x1A:"SUB",
           0x1B:"ESC", # Escape
           0x1C:"FS",
           0x1D:"GS",
           0x1E:"RS",
           0x1F:"US",
           0x20:"Space"
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
    CURSOR_PREVOIUS_LINE = "F"
    CURSOR_HORIZONTAL_ABSOLUTE = "G"
    CURSOR_POSITION = "H"
    ERASE_IN_DISPLAY = "J"
    ERASE_IN_LINE = "K"
    ERASE_SCROLL_UP = "S"
    ERASE_SCROLL_DOWN = "T"
    SGR = "m" # Select graphics rendition (SGR)
    AUX = "i"
    DSR = "n" # Device statur report

    UNSUPPORED = "UNSUP"

    @staticmethod
    def decode(s) -> CSI:
        if not s[0] == Esc.ESCAPE:
            return None

        tc = s[-1] # termination character in Escape sequence

        for x in CSI:
            if tc == x.value:
                logging.debug(f"Found {x}")
                return x

        logging.debug(f"Found {CSI.UNSUPPORED}")
        return CSI.UNSUPPORED

 
class SGR(Enum):
    """Control Sequence Introducer

    Args:
        Enum (_type_): _description_
    """

    # SGR (Select Graphic Rendition)
    RESET = "0" # Reset all attributes
    BOLD = "1" # Bold/increased intensity
    DIM = "2"  # Dim/decreased intensity
    ITALIC = "3"
    UNDERLINE = "4"
    SLOW_BLINK = "5"
    RAPID_BLINK = "6"
    REVERSE_VIDEO = "7"
    CONCEAL = "8"
    CROSSED = "9"
    PRIMARY = "10" # Primary (default) font

    FRACTUR = "20" # Gothic 
    DOUBLE_UNDERLINE = "21" 

    NORMAL_INTENSITY = "22"
    NOT_ITALIC = "23"
    NOT_UNDERLINED = "24"
    NOT_BLINKING = "25"
    NOT_REVERSED = "27"
    REVEAL = "28"
    NOT_CROSSED = "29"
    FG_COLOR_BLACK = "30"
    FG_COLOR_RED = "31"
    FG_COLOR_GREEN = "32"
    FG_COLOR_YELLOW = "33"
    FG_COLOR_BLUE = "34"
    FG_COLOR_MAGENTA = "35"
    FG_COLOR_CYAN = "36"
    FG_COLOR_WHITE = "37"
    
    BG_COLOR_BLACK = "40"
    BG_COLOR_RED = "41"
    BG_COLOR_GREEN = "42"
    BG_COLOR_YELLOW = "43"
    BG_COLOR_BLUE = "44"
    BG_COLOR_MAGENTA = "45"
    BG_COLOR_CYAN = "46"
    BG_COLOR_WHITE = "47"

    FRAMED = "51"

    SUPERSCRIPT = "73"
    SUBSCRIPT = "74"

    UNSUPPORTED = "UNSP"

    @staticmethod
    def is_sgr(s: str) -> bool:
        if s[0] == Esc.ESCAPE and s[-1] == "m":
            return True
        return False
    
    @staticmethod
    def decode(s: str):
        if not SGR.is_sgr(s):
            return None

        x = s[2:-1]
        sp = x.split(";")
        xx = []
        for c in sp:
            if c == "":              # If no number present it is a reset(0)
                xx.append(SGR.RESET)
            else:
                for a in SGR:
                    if c == a.value:
                        xx.append(a)

        # if isinstance(t, SGR):
        logging.debug(f"SGR: {xx}")
        return xx          
                
            
class Esc:
    ESCAPE = "\x1b"

    """ ANSI foreground colors codes """
    BLACK = "\x1b[0;30m"        # Black
    RED = "\x1b[0;31m"          # Red
    GREEN = '\x1b[0;32m'        # Green
    YELLOW = '\x1b[0;33m'       # Yellow
    BLUE = '\x1b[0;34m'         # Blue
    MAGENTA = '\x1b[0;35m'      # Magenta
    CYAN = '\x1b[0;36m'         # Cyan
    WHITE = '\x1b[0;37m'         # Gray
    DARKGRAY = '\x1b[1;30m'     # Dark Gray
    BR_RED = '\x1b[1;31m'       # Bright Red
    BR_GREEN = '\x1b[1;32m'     # Bright Green
    BR_YELLOW = '\x1b[1;33m'    # Bright Yellow
    BR_BLUE = '\x1b[1;34m'      # Bright Blue
    BR_MAGENTA = '\x1b[1;35m'   # Bright Magenta
    BR_CYAN = '\x1b[1;36m'      # Bright Cyan
    BR_WHITE = '\x1b[1;37m'     # White

    # ANSI background color codes
    #
    ON_BLACK = '\x1b[40m'       # Black
    ON_RED = '\x1b[41m'         # Red
    ON_GREEN = '\x1b[42m'       # Green
    ON_YELLOW = '\x1b[43m'      # Yellow
    ON_BLUE = '\x1b[44m'        # Blue
    ON_MAGENTA = '\x1b[45m'     # Magenta
    ON_CYAN = '\x1b[46m'        # Cyan
    ON_WHITE = '\x1b[47m'       # White

    # ANSI Text attributes
    ATTR_NORMAL = "\x1b[0m"       # Reset attributes
    ATTR_BOLD = "\x1b[1m"         # bold font
    ATTR_LOWINTENSITY = "\x1b[2m" # Low intensity/faint/dim
    ATTR_ITALIC = "\x1b[3m"       # Low intensity/faint/dim
    ATTR_UNDERLINE = "\x1b[4m"    # Underline
    ATTR_SLOWBLINK = "\x1b[5m"    # Slow blink
    ATTR_FASTBLINK = "\x1b[6m"    # Fast blink
    ATTR_REVERSE = "\x1b[7m"      # Reverse video
    ATTR_CROSSED = "\x1b[9m"      # Crossed text
    ATTR_FRACTUR = "\x1b[20m"     # Gothic
    ATTR_FRAMED = "\x1b[51m"      # Framed 
    ATTR_OVERLINED = "\x1b[53m"   # Overlined 
    ATTR_SUPERSCRIPT = "\x1b[73m" # Superscript
    ATTR_SUBSCRIPT = "\x1b[74m"   # Subscript
    
    END = "\x1b[0m"
    CLEAR = "\x1b[2J"
    RESET = "\x1b[m"
    
    WONR = "\x1b[1;47\x1b[1;31m"

    # ANSI cursor operations
    #
    RETURN = "\x1b[F"           # Move cursor to begining of line
    UP = "\x1b[A"               # Move cursor one line up
    DOWN = "\x1b[B"             # Move cursor one line down
    FORWARD = "\x1b[C"          # Move cursor forward
    BACK = "\x1b[D"             # Move cursor backward
    HIDE = "\x1b[?25l"          # Hide cursor
    END = "\x1b[m"              # Clear Attributes

    # ANSI movement codes 
    CUR_UP = '\x1b[A'         # cursor up
    CUR_DOWN = '\x1b[B'       # cursor down
    CUR_FORWARD = '\x1b[C'    # cursor forward
    CUR_BACK = '\x1b[;D'       # cursor back
    CUR_RETURN = '\x1b[F'     # cursor return
    
    CUR_HIDE = '\x1b[?25l'      # hide cursor
    CUR_SHOW = '\x1b[?25h'      # show cursor

    KEY_HOME = '\x1b[1~'      # Home
    KEY_INSERT = '\x1b[2~'    # 
    KEY_DELETE = '\x1b[3~'    # 
    KEY_END = '\x1b[4~'       # 
    KEY_PGUP = '\x1b[5~'      # 
    KEY_PGDN = '\x1b[6~'      # 
    KEY_HOME = '\x1b[7~'      # 
    KEY_END = '\x1b[8~'       # 
    KEY_F0 = '\x1b[10~'       # F
    KEY_F1 = '\x1b[11~'       # F
    KEY_F2 = '\x1b[12~'       # F
    KEY_F3 = '\x1b[13~'       # F
    KEY_F4 = '\x1b[14~'       # F
    KEY_F5 = '\x1b[15~'       # F
    KEY_F6 = '\x1b[17~'       # F
    KEY_F7 = '\x1b[18~'       # F
    KEY_F8 = '\x1b[19~'       # F
    KEY_F9 = '\x1b[20~'       # F
    KEY_F10 = '\x1b[21~'      # F
    KEY_F11 = '\x1b[23~'      # F
    KEY_F12 = '\x1b[24~'      # F
    KEY_F13 = '\x1b[25~'      # F
    KEY_F14 = '\x1b[26~'      # F
    KEY_F15 = '\x1b[28~'      # F
    KEY_F16 = '\x1b[29~'      # F

    KEY_CTRL_C = '\x1b[4c'

    # KEY_ = '\x1b[1~'         # 
    # KEY_ = '\x1b[1~'         # 
    # KEY_ = '\x1b[1~'         # 
    
    
    E_RET  = 100
    E_UP   = 101
    E_DOWN = 102
    
    x = [ CUR_RETURN, CUR_UP, CUR_DOWN ]
    y = { E_RET:CUR_RETURN, 
          E_UP:CUR_UP, 
          E_DOWN:CUR_DOWN }

    @staticmethod
    def findEnd(data, idx):
        i = idx
        while (i-idx) < 12:
            ch = data.at(i)
            if ch.isalpha():
                return i
            else:
                i += 1
        return -1

    @staticmethod
    def is_escape_seq(s: str) -> bool:
        if s[0] == Esc.ESCAPE:
            return True
        else:
            return False


# escape2html = {
#     SGR.FG_COLOR_BLACK: [ Esc.BLACK, "black"],
#     SGR.FG_COLOR_RED: [ Esc.RED, "red"],
#     SGR.FG_COLOR_GREEN: [ Esc.GREEN, "green"],
#     SGR.FG_COLOR_YELLOW: [ Esc.YELLOW, "yellow"],
#     SGR.FG_COLOR_BLUE: [ Esc.BLUE, "blue"],
#     SGR.FG_COLOR_MAGENTA: [ Esc.MAGENTA, "magenta"],
#     SGR.FG_COLOR_CYAN: [ Esc.CYAN, "cyan"],
#     SGR.FG_COLOR_WHITE: [ Esc.WHITE, "white"],
#     #SGR.FG_COLOR_BR_BLACK: [ Esc.DARKGRAY, "darkgray"],
#     # SGR.FG_COLOR_BR_RED: [ Esc.BR_RED, "red"],
#     # SGR.FG_COLOR_BR_GREEN: [ Esc.BR_GREEN, "green"],
#     # SGR.FG_COLOR_BR_YELLOW: [ Esc.BR_YELLOW, "yellow"],
#     # SGR.FG_COLOR_BR_BLUE: [ Esc.BR_BLUE, "blue"],
#     # SGR.FG_COLOR_BR_MAGENTA: [ Esc.BR_MAGENTA, "magenta"],
#     # SGR.FG_COLOR_BR_CYAN: [ Esc.BR_CYAN, "cyan"],
#     # SGR.FG_COLOR_BR_WHITE: [ Esc.BR_WHITE, "white"],

#     # ANSI background color codes
#     #
#     SGR.BG_COLOR_BLACK: [ Esc.ON_BLACK, "black"],
#     SGR.BG_COLOR_RED: [ Esc.ON_RED, "red"],
#     SGR.BG_COLOR_GREEN: [ Esc.ON_GREEN, "green"],
#     SGR.BG_COLOR_YELLOW: [ Esc.ON_YELLOW, "yellow"],
#     SGR.BG_COLOR_BLUE: [ Esc.ON_BLUE, "blue"],
#     SGR.BG_COLOR_MAGENTA: [ Esc.ON_MAGENTA, "magenta"],
#     SGR.BG_COLOR_CYAN: [ Esc.ON_CYAN, "cyan"],
#     SGR.BG_COLOR_WHITE: [ Esc.ON_WHITE, "white"],

#     # ANSI Text attributes
#     SGR.RESET: [ Esc.ATTR_NORMAL, "normal"],
#     SGR.BOLD: [ Esc.ATTR_BOLD, "bold"],
#     SGR.DIM: [ Esc.ATTR_LOWINTENSITY, ""],
#     SGR.ITALIC: [ Esc.ATTR_ITALIC, ""],
#     SGR.UNDERLINE: [ Esc.ATTR_UNDERLINE, ""],
#     SGR.SLOW_BLINK: [ Esc.ATTR_SLOWBLINK, ""],
#     SGR.RAPID_BLINK: [ Esc.ATTR_FASTBLINK, ""],
#     SGR.REVERSE_VIDEO: [ Esc.ATTR_REVERSE, ""],
#     SGR.FRACTUR: [ Esc.ATTR_FRACTUR, ""],
#     SGR.FRAMED: [ Esc.ATTR_FRAMED, ""],
#     SGR.CROSSED: [ Esc.ATTR_OVERLINED, ""],
#     SGR.SUPERSCRIPT: [ Esc.ATTR_SUPERSCRIPT, ""],
#     SGR.SUBSCRIPT: [ Esc.ATTR_SUBSCRIPT, ""],
#     SGR.RESET: [ Esc.END, "" ]
# }


class EscapeDecoder():
    nls = ["\n", "\x0d", "\x1b"]
    
    def __init__(self):
        self.idx = 0
        self.seq = False
        self.clear()
        
    def clear(self):
        self.buf = ""

    def append_string(self, s:str) -> None:
        self.buf += s

    def append_bytearray(self, ba: bytearray) -> None:
        self.buf += ba.decode("utf-8")

    def len(self):
        return len(self.buf)

    def is_nls(self, s) -> bool:
        if s in self.nls:
            return True
        return False

    def next_char(self):
        pass

    def __iter__(self):
        self.i = 0
        return self 

    def __next__(self):
        l = len(self.buf)
        if l == 0:                     # Buffer is empty, abort iteration
            raise StopIteration

        j = 0

        if self.buf[j] == Esc.ESCAPE:  # Escape sequence start character found
            while j<l and not self.buf[j].isalpha():
                j += 1
            if j == l:
                raise StopIteration
            
            if self.buf[j].isalpha():  # Termination character found
                res = self.buf[0:j+1]
                self.buf = self.buf[j+1:]
                logging.debug(f"Found escape sequence: '\\x1b{res[1:]}' ")

                csi = CSI.decode(res)
                if csi == CSI.SGR:
                    SGR.decode(res)
                return res
            
            # Escape sequence not complete, abort iteration
            raise StopIteration
            
        if  self.buf[j] == Ascii.NL:
            logging.debug(f"Found newline:")
            res = self.buf[0:j+1]
            self.buf = self.buf[j+1:]
            return res
        
        if  self.buf[j] == Ascii.CR:
            logging.debug(f"Found carriage return:")
            res = self.buf[0:j+1]
            self.buf = self.buf[j+1:]
            return res

        # Handle normal text    
        #if self.buf[j] != Esc.ESCAPE: 
        while j<l and not self.is_nls(self.buf[j]):
           j += 1
        res = self.buf[0:j]
        self.buf = self.buf[j:]
        logging.debug(f"Found text sequence: '" + res.replace("\x1b", "\\x1b").replace("\x0a", "\\n").replace("\x0d", '\\c')+"'")
        return res


class EscapeTokenizer():
    
    def __init__(self):
        self.idx = 0
        self.seq = False
        self.clear()
        
    def clear(self):
        self.buf = ""

    def append_string(self, s:str) -> None:
        self.buf += s

    def append_bytearray(self, ba: bytearray) -> None:
        self.buf += ba.decode("utf-8")

    def __iter__(self):
        self.i = 0
        return self 

    def __next__(self) -> str:
        l = len(self.buf)
        if l == 0:                     # Buffer is empty, abort iteration
            raise StopIteration

        j = 0

        if self.buf[j] == Esc.ESCAPE:  # Escape sequence start character found
            while j<l and not self.buf[j].isalpha():
                j += 1
            if j == l:
                raise StopIteration
            
            if self.buf[j].isalpha():  # Termination character found
                res = self.buf[0:j+1]
                self.buf = self.buf[j+1:]
                logging.debug(f"Found escape sequence: '\\e{res[1:]}' ")
                return res
            
            # Escape sequence not complete, abort iteration
            raise StopIteration
            
        # Handle normal text    
        while j<l and self.buf[j] != Esc.ESCAPE:
           j += 1
        res = self.buf[0:j]
        self.buf = self.buf[j:]
        logging.debug(f"Found text sequence: '" + res.replace("\x1b", "\\e").replace("\x0a", "\\n").replace("\x0d", '\\r')+"'")
        return res


@dataclass
class TColor():
    BLACK : str = "#2e3436"
    RED : str = "#cc0000"
    GREEN : str = "#4e9a06"
    YELLOW : str = "#c4a000"
    BLUE : str = "#3465a4"
    MAGENTA : str = "#75507b"
    CYAN : str = "#06989a"
    WHITE : str = "#d3d7cf"
    BRIGHT_BLACK : str = "#555753"
    BRIGHT_RED : str = "#ef2929"
    BRIGHT_GREEN : str = "#8ae234"
    BRIGHT_YELLOW : str = "#fce94f"
    BRIGHT_BLUE : str = "#729fcf"
    BRIGHT_MAGENTA : str = "#ad7fa8"
    BRIGHT_CYAN : str = "#34e2e2"
    BRIGHT_WHITE : str = "#eeeeec"





class TerminalState:
    bold : bool = False
    faint : bool = False
    italic : bool = False
    underline : bool = False
    slow_blink : bool = False
    rapid_blink : bool = False
    reverse_video : bool = False
    crossed : bool = False
    superscript : bool = False
    subscript : bool = False
    
    color : bool = False
    bg_color:SGR = SGR.BG_COLOR_WHITE
    attribute:SGR = SGR.RESET
    cur_x = None
    cur_y = None

    default_fg_color: SGR = SGR.FG_COLOR_BLACK
    default_bg_color: SGR = SGR.BG_COLOR_WHITE

    buf : str = ""

    def __init__(self) -> None:
        self.et = EscapeTokenizer()
        self.reset()
        
    def reset(self):
        self.bold = False
        self.faint = False
        self.italic = False
        self.underline = False
        self.slow_blink = False
        self.rapid_blink = False
        self.reverse_video = False
        self.crossed = False
        self.color = False
        self.bg_color = SGR.BG_COLOR_WHITE
        self.buf = ""
        self.superscript = False
        self.subscript = False
        self.et.clear()
        
    def update(self, s : str) -> None:
        self.et.append_string(s)

        for token in self.et:
            if Esc.is_escape_seq(token):
                x = CSI.decode(token)
                if x == CSI.SGR:
                    y = SGR.decode(token)
                    for a in y:
                        if a == SGR.BOLD:
                            self.buf += "<b>"
                            self.bold = True
                        if a == SGR.ITALIC:
                            self.buf += "<i>"
                            self.italic = True
                        if a == SGR.UNDERLINE:
                            self.buf += "<u>"
                            self.underline = True
                        if a == SGR.CROSSED:
                            self.buf += "<s>"
                            self.crossed = True
                        if a == SGR.SUPERSCRIPT:
                            self.buf += "<sup>"
                            self.superscript = True
                        if a == SGR.SUBSCRIPT:
                            self.buf += "<sub>"
                            self.subscript = True

                        if a == SGR.FG_COLOR_BLACK:
                            self.buf += f"<span style=\"color:{TColor.BLACK}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_RED:
                            self.buf += f"<span style=\"color:{TColor.RED}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_GREEN:
                            self.buf += f"<span style=\"color:{TColor.GREEN}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_YELLOW:
                            self.buf += f"<span style=\"color:{TColor.YELLOW}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_BLUE:
                            self.buf += f"<span style=\"color:{TColor.BLUE}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_MAGENTA:
                            self.buf += f"<span style=\"color:{TColor.MAGENTA}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_CYAN:
                            self.buf += f"<span style=\"color:{TColor.CYAN}\">"
                            self.color = True
                        if a == SGR.FG_COLOR_WHITE:
                            self.buf += f"<span style=\"color:{TColor.WHITE}\">"
                            self.color = True
                            
                        if a == SGR.BG_COLOR_BLACK:
                            self.buf += f"<span style=\"background-color:{TColor.BLACK}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_RED:
                            self.buf += f"<span style=\"background-color:{TColor.RED}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_GREEN:
                            self.buf += f"<span style=\"background-color:{TColor.GREEN}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_YELLOW:
                            self.buf += f"<span style=\"background-color:{TColor.YELLOW}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_BLUE:
                            self.buf += f"<span style=\"background-color:{TColor.BLUE}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_MAGENTA:
                            self.buf += f"<span style=\"background-color:{TColor.MAGENTA}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_CYAN:
                            self.buf += f"<span style=\"background-color:{TColor.CYAN}\">"
                            self.color = True
                        if a == SGR.BG_COLOR_WHITE:
                            self.buf += f"<span style=\"background-color:{TColor.WHITE}\">"
                            self.color = True
                            
                        if a == SGR.RESET:
                            if self.color is True: 
                                self.color = False
                                self.buf += "</span>"
                            if self.bold is True:
                                self.bold = False
                                self.buf += "</b>"
                            if self.italic is True:
                                self.italic = False
                                self.buf += "</i>"
                            if self.underline is True:
                                self.underline = False
                                self.buf += "</u>"
                            if self.crossed is True:
                                self.crossed = False
                                self.buf += "</s>"
                            if self.superscript is True:
                                self.superscript = False
                                self.buf += "</sup>"
                            if self.subscript is True:
                                self.subscript = False
                                self.buf += "</sub>"
                                
            else:
                self.buf += token       


    def state2html(self, s: str) -> str:
        #x = f"""<span style="color:{esc2html(self.color)};background-color:{};font-weight:{}">{s}</span>"""
        #x = f"""<pre><span style="color:{esc2html(self.color)}">{s}</span></pre>"""
        #logging.debug(x)
        #return x
        return ""

    def get_buf(self):
        x = self.buf
        self.buf = ""
        return x
        


FLAG_BLUE="\x1b[48;5;20m"
FLAG_YELLOW="\x1b[48;5;226m"

flag = f"""
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Esc.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Esc.END}
{FLAG_YELLOW}                 {Esc.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Esc.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Esc.END}
"""
escape_attribute_test = f"""  
{Esc.ATTR_NORMAL}Normal text{Esc.END}
{Esc.ATTR_BOLD}Bold text{Esc.ATTR_NORMAL}
{Esc.ATTR_LOWINTENSITY}Dim text{Esc.ATTR_NORMAL}
{Esc.ATTR_ITALIC}Italic text{Esc.ATTR_NORMAL}
{Esc.ATTR_UNDERLINE}Underline text{Esc.ATTR_NORMAL}
{Esc.ATTR_SLOWBLINK}Slow blinking text{Esc.ATTR_NORMAL}
{Esc.ATTR_FASTBLINK}Fast blinking text{Esc.ATTR_NORMAL}
{Esc.ATTR_FRAMED}Framed text{Esc.ATTR_NORMAL}
Subscript{Esc.ATTR_SUBSCRIPT}text{Esc.ATTR_NORMAL}
Superscript{Esc.ATTR_SUPERSCRIPT}text{Esc.ATTR_NORMAL}
{Esc.ATTR_FRACTUR}Fractur/Gothic text{Esc.ATTR_NORMAL}
{Esc.ATTR_CROSSED}Crossed text{Esc.ATTR_NORMAL}

{Esc.BLACK}Black{Esc.END}
{Esc.RED}Red{Esc.ATTR_NORMAL}
{Esc.GREEN}Green{Esc.END}
{Esc.YELLOW}Yellow{Esc.END}
{Esc.BLUE}Blue{Esc.END}
{Esc.MAGENTA}Magenta{Esc.END}
{Esc.CYAN}Cyan{Esc.END}
{Esc.WHITE}WHITE{Esc.END}
{Esc.WHITE}White{Esc.END}
{Esc.DARKGRAY}Dark Gray{Esc.END}
{Esc.BR_RED}Bright Red{Esc.END}
{Esc.BR_GREEN}Bright Green{Esc.END}
{Esc.BR_YELLOW}Bright Yellow{Esc.END}
{Esc.BR_BLUE}Bright Blue{Esc.END}
{Esc.BR_MAGENTA}Bright Magenta{Esc.END}
{Esc.BR_CYAN}Bright Cyan{Esc.END}

{Esc.ON_BLACK} Black {Esc.END}
{Esc.ON_RED} Red {Esc.END}
{Esc.ON_GREEN} Green {Esc.END}
{Esc.ON_YELLOW} Yellow {Esc.END}
{Esc.ON_BLUE} Blue {Esc.END}
{Esc.ON_MAGENTA} Magenta {Esc.END}
{Esc.ON_CYAN} Cyan {Esc.END}
"""

cursor_test = f"""
{Esc.CUR_DOWN} asdf {Esc.CUR_UP}  {Esc.CUR_BACK} {Esc.CUR_FORWARD} {Esc.ATTR_FRACTUR}
"""


incomplete_escape_sequence = f"""
{Esc.BR_MAGENTA}Some colored text{Esc.END}
{Esc.GREEN}Some more text with incomplete escape sequence \x1b["""

end_with_newline = "Some text with newline end\n"
    
def main() -> None:
    logging.basicConfig(format="[%(levelname)s] Line: %(lineno)d %(message)s", level=logging.DEBUG)
   
    #print(escape_attribute_test)
    #print(flag)

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
    print("Buf:\n" + et.buf)
    


if __name__ == "__main__":
    main()
