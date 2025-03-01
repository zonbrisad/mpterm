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
from typing import Any


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
        self.vslider = self.add_slider(
            "Voltage", "Set Voltage", self.action_voltage_slider, 0, 3000
        )
        self.add_button("Set Voltage", "Set voltage", self.cmd_set_voltage)
        self.current_label = self.add_label("0.0")
        self.islider = self.add_slider(
            "Current", "Set current", self.action_current_slider, 0, 500
        )
        self.add_button("Set Current", "Set Current", self.cmd_set_current)

        self.cmd = None
        self.set_voltage(0)
        self.set_current(0)

    def data(self, data: bytearray) -> None:
        sdata = str(data, "utf-8")
        self.append_ansi_text(f"[{Ansi.BR_GREEN}Recv{Ansi.RESET}] {sdata}\n")
        if self.cmd == KAxxxxP.VoltSet:
            volt = float(sdata)
            self.set_voltage(volt)
            self.vslider.widget.setSliderPosition(int(round(volt * 100, 2)))
        if self.cmd == KAxxxxP.CurSet:
            current = float(sdata)
            self.set_current(current)
            self.islider.widget.setSliderPosition(int(round(current * 100, 2)))

        self.cmd = None

    def send_command(
        self, cmd: KAxxxxP, arg: str = "", desc: str = "", timeout: int = 100
    ) -> None:
        self.cmd = cmd
        self.send(f"{cmd.value}{arg}", desc, timeout)

    def send(self, cmd: str, desc: str = "", timeout: int = 100) -> None:
        self.send_msg_string(cmd, timeout)
        self.append_ansi_text(
            f"[{Ansi.BR_RED}Send{Ansi.RESET}] {cmd:20}{Ansi.CYAN}{desc}{Ansi.RESET}\n"
        )

    def cmd_read_id(self) -> None:
        self.send_command(KAxxxxP.ReadID, desc="Read unit Id")

    def cmd_enable(self) -> None:
        self.send_command(KAxxxxP.Enable, desc="Enable output", timeout=0)

    def cmd_disable(self) -> None:
        self.send_command(KAxxxxP.Disable, desc="Disable output", timeout=0)

    def cmd_get_set_voltage(self) -> None:
        self.send_command(KAxxxxP.VoltSet, desc="Set voltage")

    def cmd_get_set_current(self) -> None:
        self.send_command(KAxxxxP.CurSet, desc="Set current")

    def cmd_get_voltage(self) -> None:
        self.send_command(KAxxxxP.Voltage, desc="Read set Voltage")

    def cmd_get_current(self) -> None:
        self.send_command(KAxxxxP.Current, desc="Read set Current")

    def set_voltage(self, value: float) -> None:
        self.vval = value
        self.voltage_label.set_text(f"  {value:>9.2f} V")

    def set_current(self, value: float) -> None:
        self.ival = value
        self.current_label.set_text(f"  {value:>7.2f} A")

    def action_voltage_slider(self, value: int) -> None:
        voltage = float(value / 100)
        self.vval = voltage
        self.set_voltage(voltage)

    def cmd_set_voltage(self) -> None:
        self.send_command(
            KAxxxxP.SetVolt,
            arg=f"{self.vval:.2f}",
            desc="Set voltage",
            timeout=0,
        )

    def action_current_slider(self, value: int) -> None:
        current = float(value / 100)
        self.ival = current
        self.set_current(current)

    def cmd_set_current(self) -> None:
        self.send_command(
            KAxxxxP.SetCurr, arg=f"{self.ival:.2f}", desc="Set Current", timeout=0
        )


def main() -> None:
    pass


# Main run_ext_program handle
if __name__ == "__main__":
    main()
