#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# mpterm plugin
#
# File:     mpplugin
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2024-07-06
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class MpPluginInfo:
    name: str = ""
    description: str = ""
    date: str = ""
    author: str = ""


class MpPlugin:
    def __init__(self) -> None:
        self.plugin_info = None

    def info(self) -> MpPluginInfo:
        return self.plugin_info


def main() -> None:
    pass


if __name__ == "__main__":
    main()
