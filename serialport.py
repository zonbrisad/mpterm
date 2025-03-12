#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# serialport handler
#
# File:     serialport.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2023-01-12
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
import enum
import logging
from PyQt5.QtCore import QTimer, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


# class State(enum.Enum):
#     DISCONNECTED = 0
#     CONNECTED = 1
#     # SUSPENDED = 2
#     # RECONNECTING = 3


errors = {
    QSerialPort.NoError: "No error",
    QSerialPort.DeviceNotFoundError: "Device not found",
    QSerialPort.PermissionError: "Permission denied",
    QSerialPort.OpenError: "Failed to open device",
    QSerialPort.NotOpenError: "Port not open",
    QSerialPort.WriteError: "Write fail",
    QSerialPort.ReadError: "Read fail",
    QSerialPort.ResourceError: "Resource error",
    QSerialPort.UnsupportedOperationError: "Unsupported operation",
    QSerialPort.TimeoutError: "Timeout",
    QSerialPort.UnknownError: "Unknown",
}

bitrates = [
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    19200,
    28400,
    57600,
    115200,
    256000,
]


class SerialPort(QSerialPort):
    def __init__(self) -> None:
        super().__init__()

        self.clear_counters()
        # self.serial_state = State.DISCONNECTED

        # self.suspend_timer = QTimer()
        # self.suspend_timer.setSingleShot(True)
        # self.suspend_timer.timeout.connect(self.suspend_timeout)

        # self.reconnect_timer = QTimer()
        # self.reconnect_timer.setInterval(400)
        # self.reconnect_timer.timeout.connect(self.reconnect_timeout)
        # self.reconnect_timer.start()

        self.cntReconnect = 0

    def read_str(self) -> str:
        data = self.read()
        data_str = str(data, "utf-8")
        return data_str

    def read(self):
        data = self.readAll()
        self.cnt_rx += data.count()
        return data

    def print(self) -> None:
        pass
        logging.debug(f"Port: {self.portName()}")
        logging.debug(f"Bitrate: {self.baudRate()}")
        logging.debug(f"Parity: {self.parity()}")
        logging.debug(f"Databits: {self.parity()}")

    def error(self):
        err = super().error()
        return errors[err]

    def open(self) -> bool:
        if self.isOpen():
            return True
        res = super().open(QIODevice.ReadWrite)

        return res

    def close(self) -> None:
        super().close()

    def clear(self) -> None:
        if self.isOpen():
            self.clear()

    def clear_counters(self):
        self.cnt_rx = 0
        self.cnt_tx = 0

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def send(self, data: bytearray):
        if self.isOpen():
            res = self.write(data)
            if res > 0:
                self.cnt_tx += res
            else:
                logging.error("Could not write data.")

    # def set_state(self, new_state: State, timeout=4000) -> None:
    #     if new_state == State.SUSPENDED and self.serial_state == State.CONNECTED:
    #         self.close()
    #         self.serial_state = State.SUSPENDED
    #         if timeout != -1:
    #             self.suspend_timer.start(timeout)

    #     if new_state == State.DISCONNECTED:
    #         self.serial_state = new_state
    #         self.suspend_timer.stop()

    #     if new_state in [
    #         State.CONNECTED,
    #         State.DISCONNECTED,
    #     ]:
    #         self.serial_state = new_state

    #     # self.state = newState
    #     logging.debug(f"State: {self.serial_state.name}")

    # def suspend_timeout(self):
    #     if self.serial_state == State.SUSPENDED:
    #         self.set_state(State.RECONNECTING)
    #         self.serial_state = State.RECONNECTING
    #         logging.debug("Reconnecting port")

    # def reconnect_timeout(self):
    #     if self.serial_state != State.RECONNECTING:
    #         self.cntReconnect = 0
    #         return

    #     self.cntReconnect += 1
    #     logging.debug(f"Reconnecting... {self.cntReconnect}")

    #     self.clear()

    #     self.open()
    # if self.open():
    # self.set_state(State.CONNECTED)

    # def write(self, data) -> None:
    #     super().__write__()

    def bitrates(self):
        """Return a list of supported bitrates"""
        return bitrates


def main() -> None:
    pass


if __name__ == "__main__":
    main()
