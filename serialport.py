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


class State(enum.Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    SUSPENDED = 2
    RECONNECTING = 3


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


class SerialPort(QSerialPort):
    def __init__(self) -> None:
        super().__init__()

        self.clear_counters()
        self.state = State.DISCONNECTED

        self.suspend_timer = QTimer()
        self.suspend_timer.setSingleShot(True)
        self.suspend_timer.timeout.connect(self.suspend_timeout)

        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(400)
        self.reconnect_timer.timeout.connect(self.reconnect_timeout)
        self.reconnect_timer.start()

        self.cntReconnect = 0

    def read_str(self) -> str:
        data = self.read()
        data_str = str(data, "utf-8")
        return data_str

    def read(self):
        data = self.readAll()
        self.rxCnt += data.count()
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

    def open(self):
        if self.isOpen():
            return True
        res = super().open(QIODevice.ReadWrite)
        if res:
            self.set_state(State.CONNECTED)
            self.print()

        return res

    def close(self) -> None:
        super().close()
        self.state = State.DISCONNECTED

    def clear(self) -> None:
        if self.isOpen():
            self.clear()

    def clear_counters(self):
        self.rxCnt = 0
        self.txCnt = 0

    def send_string(self, data: str):
        self.send(bytearray(data, "utf-8"))

    def send(self, data: bytearray):
        if self.isOpen():
            res = self.write(data)
            if res > 0:
                self.txCnt += res
            else:
                logging.error("Could not write data.")

    def set_state(self, newState: State, timeout=4000) -> None:
        if newState == State.SUSPENDED and self.state == State.CONNECTED:
            self.close()
            self.state = State.SUSPENDED
            if timeout != -1:
                self.suspend_timer.start(timeout)

        if newState == State.DISCONNECTED:
            self.state = newState
            self.suspend_timer.stop()

        if newState in [
            State.CONNECTED,
            State.DISCONNECTED,
            State.RECONNECTING,
            State.DISCONNECTED,
        ]:
            self.state = newState

        # self.state = newState
        logging.debug(f"State: {self.state.name}")

    def suspend_timeout(self):
        if self.state == State.SUSPENDED:
            self.set_state(State.RECONNECTING)
            self.state = State.RECONNECTING
            logging.debug("Reconnecting port")

    def reconnect_timeout(self):
        if self.state != State.RECONNECTING:
            self.cntReconnect = 0
            return

        self.cntReconnect += 1
        logging.debug(f"Reconnecting... {self.cntReconnect}")

        self.clear()

        self.open()
        # if self.open():
        # self.set_state(State.CONNECTED)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
