#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# 
#
# File:     param.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2022-11-24
# License:  
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
import argparse

from enum import Enum, auto
from dataclasses import dataclass

class ParamType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    
    

@dataclass
class Param:
    """"""
    value: None 
    type: ParamType = ParamType.Integer
     
        




def main() -> None:
    parser = argparse.ArgumentParser(
        prog=App.NAME,
        description=App.DESCRIPTION,
        epilog="",
        add_help=True)
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Print debug messages")
    parser.add_argument("--version", action="version",
                        version=f"{App.NAME} {App.VERSION}",
                        help="Print version information")
    args = parser.parse_args()
    # parser.print_help()


if __name__ == "__main__":
    main()
