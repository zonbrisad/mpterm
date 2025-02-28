#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# Basic dataframe class
#
# File:     mpframe
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:     2024-07-10
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------


class MpFrame:
    def __init__(self) -> None:
        self.sync_string = []
        self.flength = 1
        self.clear()

    def clear(self) -> None:
        self.frame = []
        self.sync_index = 0

    def append_byte(self, byte: int) -> None:
        self.frame.append(byte)

    def nr_of_bytes(self) -> int:
        return len(self.frame)

    def frame_length(self) -> int:
        return self.flength

    def set_sync_string(self, sync_list: list[int]) -> None:
        self.sync_string = sync_list

    def set_frame_length(self, frame_length: int) -> None:
        self.flength = frame_length

    def is_full_length(self) -> bool:
        """Determines if frame has reached full length

        Returns:
            bool: True if frame i full length
        """
        return self.nr_of_bytes() == self.frame_length()

    def add_byte(self, byte: int) -> bool:

        if len(self.sync_string) == 0:
            self.frame.append(byte)
        else:
            if self.sync_index >= len(self.sync_string):
                self.frame.append(byte)
            else:
                if byte == self.sync_string[self.sync_index]:
                    self.sync_index += 1
                    self.frame.append(byte)
                else:
                    self.clear()
                    return False

        if self.is_full_length():
            return True

        return None

    def hex_str(self) -> str:
        return " ".join("{:02x}".format(byte) for byte in self.frame)

    def __str__(self) -> str:
        return self.hex_str()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
