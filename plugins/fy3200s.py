#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     fy3200s.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
# https://integrac.sk/wp-content/uploads/2018/02/FY3200S-DDS-Protocol-EN-DRAFT-.pdf
#

# Imports --------------------------------------------------------------------

from enum import Enum
from mpplugin import MpPlugin, MpPluginWidget, MpPluginWidgetType
from mpframe import MpFrame

# Variables ------------------------------------------------------------------
plugin_name = "FY3200S"
plugin_description = "FeelTech FY3200S Dual channel function generator"
plugin_date = "2024-07-25"
plugin_author = "Peter Malmberg <peter.malmberg@gmail.com>"

# plugin_info = MpPluginInfo(
#     name="FY3200S",
#     description="FeelTech FY3200S Dual channel function generator",
#     date="2024-07-25",
#     author="Peter Malmberg <peter.malmberg@gmail.com>",
# )


# Code -----------------------------------------------------------------------


class Fy3200Cmd(Enum):
    SetMainWaveform = "bw"
    SetMainFreq = "bf"
    GetMainFreq = "cf"


class Fy3200Waveform(Enum):
    Sine = 0
    Square = 1
    Pulse = 2
    Triangle = 3
    Sawtooth = 4
    NSawtooth = 5
    DC = 6
    PRE1 = 7
    PRE2 = 8
    PRE3 = 9
    PRE4 = 10
    PRE5 = 11
    PRE6 = 12
    PRE7 = 13
    PRE8 = 14
    PRE9 = 15
    PRE10 = 16
    ARB1 = 17
    ARB2 = 18
    ARB3 = 19
    ARB4 = 20


class Fy3200:

    # def __init__(self) -> None:
    #     self.clear()

    # def clear(self) -> None:
    #     self.msg = []

    @staticmethod
    def msg_set_waveform(waveform: Fy3200Waveform) -> str:
        return f"bw{waveform.value}\n"

    @staticmethod
    def _msg(cmd: Fy3200Cmd, data: str) -> str:
        return f"{cmd.value}{data}\n"

    @staticmethod
    def msg_set_freq(freq: float) -> str:
        return Fy3200._msg(Fy3200Cmd.SetMainFreq, f"{freq*100:09.0f}")

    @staticmethod
    def msg_get_freq() -> str:
        return Fy3200._msg(Fy3200Cmd.GetMainFreq, "")


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = plugin_name
        self.description = plugin_description
        self.date = plugin_date
        self.author = plugin_author

        self.waveform = Fy3200Waveform.Sine
        self.frequency = 1000

        self.timer.timeout.connect(self.timeout)

        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.ComboBox,
                "",
                "Waveform",
                combo_data={wf.name: wf for wf in Fy3200Waveform},
                action=self.change_waveform,
            )
        )
        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Button,
                "Set waveform",
                "",
                action=self.cmd_set_waveform,
            )
        )

        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.LineEdit,
                "",
                "Frequency",
                value=self.frequency,
                action=self.change_frequency,
            )
        )

        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Button,
                "Set Frequency",
                "",
                action=self.cmd_set_freq,
            )
        )
        self.add_widget(
            MpPluginWidget(
                MpPluginWidgetType.Button,
                "Get Frequency",
                "",
                action=self.cmd_get_freq,
            )
        )

    def data(self, data: bytearray) -> str:
        # self.data.join(data)
        self.data = bytearray(data)
        # for d in data:
        # self.append_ansi_text(str(data))
        # self.append_ansi_text("\n")
        # ret = ""
        # for i in range(0, data.count()):
        #     byte = int.from_bytes(data.at(i), "big")
        #     if self.frame.add_byte(byte) is True:
        #         ret += self.frame.to_html()
        #         self.frame.clear()

        return ""

    def timeout(self) -> None:
        print(self.data)

    def send_command(self, cmd: str) -> None:
        self.send_string(cmd)
        self.append_ansi_text(f"Command: {cmd}")

    def cmd_set_waveform(self) -> None:
        self.send_command(Fy3200.msg_set_waveform(self.waveform))

    def cmd_set_freq(self) -> None:
        self.send_command(Fy3200.msg_set_freq(self.frequency))

    def cmd_get_freq(self) -> None:
        # self.data = bytearray()
        self.start_timer(1000)
        self.send_command(Fy3200.msg_get_freq())

    def change_waveform(self, waveform: Fy3200Waveform) -> None:
        self.waveform = waveform

    def change_frequency(self, freq) -> None:
        if freq is None:
            return

        self.frequency = freq


def main() -> None:
    pass


# Main run_ext_program handle
if __name__ == "__main__":
    main()
