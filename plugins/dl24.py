#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:     dl24.py
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
from mpplugin import MpPluginData
from mpframe import MpFrame

# Variables ------------------------------------------------------------------


# Code -----------------------------------------------------------------------


class AtorchMessageType(Enum):
    Report = 0x01
    Reply = 0x02
    Command = 0x11
    NoMessage = 0xFF


class AtorchDeviceType(Enum):
    AC_Meter = 0x01
    DC_Meter = 0x02
    USB_Meter = 0x03
    NoDevice = 0xFF


class AtorchCommandType(Enum):
    Reset_Wh = 0x01
    Reset_Ah = 0x02
    Reset_Duration = 0x03
    Reset_All = 0x04
    Plus = 0x11
    Minus = 0x12
    Backlight = 0x21
    NoCmd = 0xFF


class AtorchReply(Enum):
    Ok = 0x0101
    Unsupported = 0x0103
    Unknown = 0xFFFF


class AtorchFrame(MpFrame):

    def __init__(self, dev_type: AtorchDeviceType) -> None:
        super().__init__()
        self.set_sync_string([0xFF, 0x55])
        self.set_frame_length(36)
        self.dev_type = dev_type
        self.frm = []

    def correct_checksum(self) -> bool: ...

    def frame_length(self) -> int:
        if self.message_type() == AtorchMessageType.Report:
            return 2 + 1 + 32 + 1

        if self.message_type() == AtorchMessageType.Command:
            return 2 + 1 + 6 + 1

        if self.message_type() == AtorchMessageType.Reply:
            return 2 + 1 + 4 + 1

        return 36

    def is_full_length(self) -> bool:
        if len(self.frame) < 3:
            return False

        if len(self.frame) >= self.frame_length():
            return True

        return False

    def checksum(self) -> int:
        return self.frame[-1]

    def message_type(self) -> AtorchMessageType:
        for amt in AtorchMessageType:
            if self.frame[2] == amt.value:
                return amt
        return AtorchMessageType.NoMessage

    def device_type(self) -> AtorchDeviceType:
        for adt in AtorchDeviceType:
            if self.frame[3] == adt.value:
                return adt
        return AtorchDeviceType.NoDevice

    def command_type(self) -> AtorchCommandType:
        for act in AtorchCommandType:
            if self.frame[4] == act.value:
                return act
        return AtorchCommandType.NoCmd

    def reply_type(self) -> AtorchReply:
        reply = self.hex_to_value(0x03, 2)
        for ar in AtorchReply:
            if reply == ar.value:
                return ar
        return AtorchReply.Unknown

    def frame_to_str(self) -> str:
        return self.hex_to_str(0, len(self.frame))

    def hex_to_value(self, index: int, bytes: int) -> int:
        val = 0
        if (index + bytes) > len(self.frame):
            return -1
        for x in range(bytes):
            val = 0x100 * val
            val += self.frame[x + index]
        return val

    def hex_to_str(self, index: int, bytes: int) -> int:
        lst = []
        if (index + bytes) > len(self.frame):
            return -1
        for i in range(bytes):
            lst.append(f"{self.frame[index+i]:02x}")

        return " ".join(lst)

    def voltage(self) -> float:
        return self.hex_to_value(4, 3) / 10

    def current(self) -> float:
        return self.hex_to_value(7, 3) / 1000

    def energy_mah(self) -> float:
        return self.hex_to_value(0x0A, 3) / 10

    def energy_wh(self) -> float:
        return self.hex_to_value(0x0D, 3) / 100

    def temperature(self) -> float:
        return self.hex_to_value(0x18, 2)

    def hour(self) -> int:
        return self.hex_to_value(0x1A, 2)

    def minute(self) -> int:
        return self.hex_to_value(0x1C, 1)

    def second(self) -> int:
        return self.hex_to_value(0x1D, 1)

    def add_row(self, data, value, desc) -> None:
        self.frm.append(f"{data:12} | {value:12} | {desc}<br>")

    def to_html(self) -> str:
        self.frm = []
        self.frm.append("<pre>")
        self.frm.append(self.frame_to_str())
        self.frm.append("<br>")
        self.add_row(
            self.hex_to_str(0x00, 2),
            "",
            "Magic header",
        )

        self.add_row(
            self.hex_to_str(0x02, 1),
            self.message_type().name,
            "Message type",
        )

        if self.message_type() == AtorchMessageType.Command:
            ...

        if self.message_type() == AtorchMessageType.Reply:
            self.add_row(
                self.hex_to_str(0x03, 2),
                self.reply_type().name,
                "Reply",
            )

        if self.message_type() == AtorchMessageType.Report:

            self.add_row(
                self.hex_to_str(0x03, 1), self.device_type().name, "Device type"
            )

            self.add_row(
                self.hex_to_str(0x04, 3),
                self.voltage(),
                "Voltage",
            )

            self.add_row(
                self.hex_to_str(0x07, 3),
                self.current(),
                "Current",
            )

            self.add_row(
                self.hex_to_str(0x0A, 3),
                self.energy_mah(),
                "Energy mAh",
            )

            self.add_row(
                self.hex_to_str(0x0D, 3),
                self.energy_wh(),
                "Energy Wh",
            )

            self.add_row(
                self.hex_to_str(0x18, 2),
                self.temperature(),
                "Temperature",
            )
            self.add_row(
                self.hex_to_str(0x1A, 2),
                self.hour(),
                "Hour",
            )
            self.add_row(
                self.hex_to_str(0x1C, 1),
                self.minute(),
                "Minute",
            )
            self.add_row(
                self.hex_to_str(0x1D, 1),
                self.second(),
                "Second",
            )

        self.add_row(
            self.hex_to_str(self.nr_of_bytes() - 1, 1),
            f"{self.checksum():02x}",
            "Checksum",
        )
        self.frm.append("<br></pre>")
        return "".join(self.frm)

    def calc_checksum(self) -> int:
        acc = 0
        for byte in self.frame[2:-1]:
            acc += byte

        return (acc & 0xFF) ^ 0x44

    def append_header(self, message_type: AtorchMessageType) -> None:
        self.clear()
        self.append_byte(0xFF)
        self.append_byte(0x55)
        self.append_byte(message_type.value)

    def append_checksum(self):
        self.append_byte(0x00)
        cs = self.calc_checksum()
        self.frame[-1] = cs

    def command(self, command: AtorchCommandType, value=0x00):
        self.append_header(AtorchMessageType.Command)
        self.append_byte(self.dev_type.value)
        self.append_byte(command.value)
        self.append_byte(0x00)
        self.append_byte(0x00)
        self.append_byte(0x00)
        self.append_byte(value & 0xFF)
        self.append_checksum()


class MpTermPlugin:
    def __init__(self) -> None:
        self.info = MpPluginData(
            name="Dl24", description="Dl24 electronic load", date="2024-07-05"
        )
        self.frame = AtorchFrame(AtorchDeviceType.DC_Meter)
        self.frm = []

    def get_info(self) -> MpPluginData:
        return self.info

    def data(self, data: bytearray) -> str:
        ret = ""
        for i in range(0, data.count()):
            byte = int.from_bytes(data.at(i), "big")
            if self.frame.add_byte(byte) is True:
                ret += self.frame.to_html()
                self.frame.clear()

        return ret

    def process(self) -> None:
        print("Dl24 plugin")


def main() -> None:

    real_frame = [
        0xFF,
        0x55,
        0x01,
        0x02,
        0x00,
        0x00,
        0x81,
        0x00,
        0x00,
        0x00,
        0x00,
        0x01,
        0xA7,
        0x00,
        0x00,
        0x00,
        0x04,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x1B,
        0x00,
        0x15,
        0x1C,
        0x27,
        0x3C,
        0x00,
        0x00,
        0x00,
        0x00,
        0x9B,
    ]

    aframe = AtorchFrame(AtorchDeviceType.DC_Meter)

    aframe.command(AtorchCommandType.Reset_Wh)
    print(aframe.frame_to_str())
    aframe.command(AtorchCommandType.Reset_Ah)
    print(aframe.frame_to_str())
    aframe.command(AtorchCommandType.Reset_Duration)
    print(aframe.frame_to_str())
    aframe.command(AtorchCommandType.Reset_All)
    print(aframe.frame_to_str())
    aframe.command(AtorchCommandType.Backlight, 2)
    print(aframe.frame_to_str())


# Main run_ext_program handle
if __name__ == "__main__":
    main()
