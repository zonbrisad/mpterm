#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     OWON_XDM1041.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
# https://www.owon.com.cn/upload/2020/09/24/1600964418.pdf
#
#

# Imports --------------------------------------------------------------------

from enum import Enum
from mpplugin import MpPlugin, MpPluginWidget, MpPluginWidgetType
from escape import Ansi
# Variables ------------------------------------------------------------------

doc = """
<br><br>

<br>
"""

# Code -----------------------------------------------------------------------E
# OWON XDM1041 protocol documentation
#
# https://www.owon.com.cn/upload/2020/09/24/1600964418.pdf
# https://files.owon.com.cn/software/Application/XDM1000_Digital_Multimeter_Programming_Manual.pdf
#

class SCPI_CMDS(Enum):
    ReadID = "*IDN?"  # Unit id
    Reset = "*RST"  # Reset unit
    Meas = "MEAS?"  # Measurement command, e.g. MEAS:VOLT:DC? to measure DC voltage
    ReadVolt = "MEAS:VOLT?"  # Read voltage
    ReadCurr = "MEAS:CURR?"  # Read current
    ReadRes = "MEAS:RES?"  # Read resistance
    ReadFreq = "MEAS:FREQ?"  # Read frequency
    ReadTemp = "MEAS:TEMP?"  # Read temperature
    ReadCap = "MEAS:CAP?"  # Read capacitance
    ReadDiode = "MEAS:DIOD?"  # Read diode
    ReadCont = "MEAS:CONT?"  # Read continuity
    ReadDuty = "MEAS:DUTY?"  # Read duty cycle
    ReadFreq2 = "MEAS:FREQ2?"  # Read frequency 2
    ReadPeriod = "MEAS:PER?"  # Read period
    ReadPeriod2 = "MEAS:PER2?"  # Read period 2
    ReadVoltAC = "MEAS:VOLT:AC?"  # Read AC voltage
    ReadCurrAC = "MEAS:CURR:AC?"  # Read AC current
    ReadVoltDC = "MEAS:VOLT:DC?"  # Read DC voltage
    ReadCurrDC = "MEAS:CURR:DC?"  # Read DC current
    ReadRes2 = "MEAS:RES2?"  # Read resistance 2
    
    LocalMode = "SYSTem:LOCal"  # Set local mode
    RemoteMode = "SYSTem:REMote"  # Set remote mode
    BeeperOn = "SYSTem:BEEPer ON"  # Turn buzzer on
    BeeperOff = "SYSTem:BEEPer OFF"  # Turn buzzer off
    BeeperState = "SYSTem:BEEPer?"  # Query buzzer state


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = "XDM1041"
        self.manufacturer = "OWON"
        self.model = "XDM1041"
        self.description = "OWON XDM1041 Digital Multimeter"
        self.date = "2026-02-14"
        self.author = "Peter Malmberg <peter.malmberg@gmail.com>"
        self.cnt = 0

        self.add_button("Read Id", "Read unit ID string", self.send_scpi,
                        data=SCPI_CMDS.ReadID.value)

        self.add_button("Reset", "Reset unit", self.send_scpi,
                        data=SCPI_CMDS.Reset.value)

        self.add_button("Measure", "Measure voltage, current, resistance, etc.",
                        self.send_scpi,
                        data=SCPI_CMDS.Meas.value)

        self.add_button("Local Mode", "Set local mode", self.send_scpi,
                        data=SCPI_CMDS.LocalMode.value)

        self.add_button("Remote Mode", "Set remote mode", self.send_scpi,
                        data=SCPI_CMDS.RemoteMode.value)
        
        self.add_button("Beeper On", "Turn beeper on", self.send_scpi,
                        data=SCPI_CMDS.BeeperOn.value)
        self.add_button("Beeper Off", "Turn beeper off", self.send_scpi,
                        data=SCPI_CMDS.BeeperOff.value)
        self.add_button("Beeper State", "Query beeper state", self.send_scpi,
                        data=SCPI_CMDS.BeeperState.value)

    def data(self, data: bytearray) -> str:
        ret = ""
        self.append_ansi_text(f"[{Ansi.BR_GREEN}Recv{Ansi.RESET}] {data}\n")
        return ret

    def send_scpi(self, widget) -> None:
        self.send_string(widget.data+"\n")
        self.append_ansi_text(f"Send SCPI command: {widget.data}\n")


    def main() -> None: ...


if __name__ == "__main__":
    main()
