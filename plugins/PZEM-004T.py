#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     PCEM-004T.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
# https://github.com/jacopoRodeschini/PZEM-004T/blob/master/pzem.py
#
#

# Imports --------------------------------------------------------------------

from enum import Enum

from mpplugin import MpPlugin

# Variables ------------------------------------------------------------------

doc = """
<br><br>

<br>
"""

# Code -----------------------------------------------------------------------


class PZEM_Cmds(Enum):
    Measure = bytearray([0x01, 0x04, 0x00, 0x00, 0x00, 0x0A, 0x70, 0x0D])
    Settings = bytearray([0x01, 0x03, 0x00, 0x01, 0x00, 0x02, 0x95, 0xCB])
    Reset_energy = bytearray([0x01, 0x42, 0x80, 0x11])


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = "PZEM-004T"
        self.manufacturer = "Peacefair"
        self.model = "PZEM-004T"
        self.description = "PZEM-004T AC power monitor"
        self.date = "2026-02-24"
        self.author = "Peter Malmberg <peter.malmberg@gmail.com>"
        self.cnt = 0
        self.print_data = True

        self.add_button("Read", "Read voltage, current, power, energy, etc.",
                        lambda w: self.pzem_send(PZEM_Cmds.Measure))

        self.add_button("Read Settings", "Read device settings (e.g., address, baud rate, etc.)",
                        lambda w: self.pzem_send(PZEM_Cmds.Settings))

        self.add_button("Reset Energy", "Reset energy counter",
                        lambda w: self.pzem_send(PZEM_Cmds.Reset_energy))

    def pzem_send(self, cmd: PZEM_Cmds) -> None:
        self.send_msg(cmd.value, timeout=100)
        self.cmd = cmd

    def data(self, data: bytearray) -> str:
        ret = ""
        if self.cmd == PZEM_Cmds.Measure:
            if len(data) == 25:
                voltage = (data[3] << 8 | data[4]) / 10.0
                current = (data[5] << 8 | data[6] | data[7] << 24 | data[8] << 16) / 1000.0
                active_power = (data[9] << 8 | data[10] | data[11] << 24 | data[12] << 16) / 10.0
                active_energy = data[13] << 8 | data[14] | data[15] << 24 | data[16] << 16
                frequency = (data[17] << 8 | data[18]) / 10.0
                power_factor = (data[19] << 8 | data[20]) / 100.0
                alarm = data[21] << 8 | data[22]
                ret += f"Voltage:      {voltage:.1f} V\n"
                ret += f"Current:      {current:.2f} A\n"
                ret += f"Power:        {active_power:.1f} W\n"
                ret += f"Energy:       {active_energy} Wh\n"
                ret += f"Frequency:    {frequency:.1f} Hz\n"
                ret += f"Power Factor: {power_factor:.2f}\n"
                ret += f"Alarm:        {alarm}\n"
            else:
                ret += "Invalid data length\n" 
        elif self.cmd == PZEM_Cmds.Settings:
            power_alarm_level = (data[3] << 8 | data[4])
            address = data[6]
            ret += f"Power Alarm Level: {power_alarm_level}\n"
            ret += f"Address: {address}\n"

        self.cmd = None
        self.append_ansi_text(ret)
        return ret


def main() -> None: ...


if __name__ == "__main__":
    main()
