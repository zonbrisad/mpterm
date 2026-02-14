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

plugin_name = "XDM1041"
plugin_manufacturer = "OWON"
plugin_model = "XDM1041"
plugin_description = "OWON XDM1041 Digital Multimeter" 
plugin_date = "2026-02-14"
plugin_author = "Peter Malmberg <peter.malmberg@gmail.com>"

# Code -----------------------------------------------------------------------

# OWON XDM1041 protocol documentation
#
# https://www.owon.com.cn/upload/2020/09/24/1600964418.pdf


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


class MpTermPlugin(MpPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = plugin_name
        self.manufacturer = plugin_manufacturer
        self.model = plugin_model
        self.description = plugin_description
        self.date = plugin_date
        self.author = plugin_author
        self.cnt = 0

        self.add_button("Read Id", "Read unit ID string", self.send_scpi,
                        data=SCPI_CMDS.ReadID.value)

        self.add_button("Reset", "Reset unit", self.send_scpi,
                        data=SCPI_CMDS.Reset.value)
        
        self.add_button("Measure", "Measure voltage, current, resistance, etc.", self.send_scpi,
                        data=SCPI_CMDS.Meas.value)
        
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
