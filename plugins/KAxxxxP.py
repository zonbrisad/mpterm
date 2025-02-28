#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Driver for Korad KAxxxxP line of Lab PSU's
#
#
# File:     KAxxxxP.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
# Not complete nor correct
# https://github.com/syssi/esphome-atorch-dl24/blob/main/docs/protocol-design.md#type-indicator
#
#

# Imports --------------------------------------------------------------------

from enum import Enum
from mpplugin import MpPlugin
from escape import Ansi


# Variables ------------------------------------------------------------------

plugin_name = "KAxxxxP"
plugin_description = "KAxxxP power supply"
plugin_date = "2025-02-27"
plugin_author = "Peter Malmberg <peter.malmberg@gmail.com>"

# Code -----------------------------------------------------------------------

# Korad KAxxxxP PSU protocol documentation
#
# https://sigrok.org/wiki/Korad_KAxxxxP_series


class KAxxxxP(Enum):
    ReadID = "*IDN?"  # Unit id
    Disable = "OUT0"  # Disable output
    Enable = "OUT1"  # Enable output
    VoltSet = "VSET1?"  # Read set voltage
    CurSet = "ISET1?"  # Read set current
    Voltage = "VOUT1?"  # Read outgoing voltage
    Current = "IOUT1?"  # Read outgoing current
    SetVolt = "VSET1:"  # Set voltage
    SetCurr = "ISET1:"  # Set current

    @staticmethod
    def SetV(voltage: float) -> str:
        return f"{KAxxxxP.SetVolt.value}{voltage:.2f}"

    @staticmethod
    def SetC(current: float) -> str:
        return f"{KAxxxxP.SetCurr.value}{current:.2f}"


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = plugin_name
        self.description = plugin_description
        self.date = plugin_date
        self.author = plugin_author

        self.add_button("Read Id", "Read unit ID string", self.cmd_read_id)
        self.add_button("Voltage", "Read output voltage", self.cmd_get_voltage)
        self.add_button("Current", "Read output current", self.cmd_get_current)
        self.add_button(
            "Set Voltage", "Read voltage set by user", self.cmd_get_set_voltage
        )
        self.add_button(
            "Set Current", "Read current set by user", self.cmd_get_set_current
        )
        self.add_button("Enable", "Enable output", self.cmd_enable)
        self.add_button("Disable", "Disable output", self.cmd_disable)
        self.voltage_label = self.add_label("0.0")
        self.add_slider("Voltage", "Set Voltage", self.action_voltage_slider, 0, 3000)
        self.add_button("Set Voltage", "Set voltage", self.cmd_set_voltage)
        self.current_label = self.add_label("0.0")
        self.vslider = self.add_slider(
            "Current", "Set current", self.action_current_slider, 0, 500
        )
        self.add_button("Set Current", "Set Current", self.cmd_set_current)
        self.vval = 0
        self.ival = 0

    def data(self, data: bytearray) -> None:
        ans = str(data, "utf-8")
        self.append_ansi_text(f"[{Ansi.BR_GREEN}Recv{Ansi.RESET}] {ans}\n")

    def send_command(self, cmd: KAxxxxP, desc: str = "", timeout: int = 100) -> None:
        self.send(cmd.value, desc, timeout)

    def send(self, cmd: str, desc: str = "", timeout: int = 100) -> None:
        self.send_msg_string(cmd, timeout)
        self.append_ansi_text(f"[{Ansi.BR_RED}Send{Ansi.RESET}] {cmd:12}{desc}\n")

    def cmd_read_id(self) -> None:
        self.send_command(KAxxxxP.ReadID, "Read unit Id")

    def cmd_enable(self) -> None:
        self.send_command(KAxxxxP.Enable, "Enable output", timeout=0)

    def cmd_disable(self) -> None:
        self.send_command(KAxxxxP.Disable, "Disable output", timeout=0)

    def cmd_get_set_voltage(self) -> None:
        self.send_command(KAxxxxP.VoltSet, "Set voltage")

    def cmd_get_set_current(self) -> None:
        self.send_command(KAxxxxP.CurSet, "Set current")

    def cmd_get_voltage(self) -> None:
        self.send_command(KAxxxxP.Voltage, "Current")

    def cmd_get_current(self) -> None:
        self.send_command(KAxxxxP.Current, "Current")

    def action_voltage_slider(self, value: int) -> None:
        voltage = float(value / 100)
        self.vval = voltage
        self.voltage_label.set_text(f"{str(voltage):>7} V")

    def cmd_set_voltage(self) -> None:
        self.send(f"{KAxxxxP.SetV(self.vval)}", "Set voltage", timeout=0)

    def action_current_slider(self, value: int) -> None:
        current = float(value / 100)
        self.ival = current
        self.current_label.set_text(f"{str(current):>7} A")

    def cmd_set_current(self) -> None:
        self.send(f"{KAxxxxP.SetC(self.ival)}", "Set Current", timeout=0)


def main() -> None:
    pass


# Main run_ext_program handle
if __name__ == "__main__":
    main()
