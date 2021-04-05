﻿# coding=utf-8
# **************************************************************************************************
#  MIT License                                                                                     *
#                                                                                                  *
#  Copyright (c) 2021 Dietrich Christopeit                                                         *
#                                                                                                  *
#  Permission is hereby granted, free of charge, to any person obtaining a copy                    *
#  of this software and associated documentation files (the "Software"), to deal                   *
#  in the Software without restriction, including without limitation the rights                    *
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell                       *
#  copies of the Software, and to permit persons to whom the Software is                           *
#  furnished to do so, subject to the following conditions:                                        *
#                                                                                                  *
#  The above copyright notice and this permission notice shall be included in all                  *
#  copies or substantial portions of the Software.                                                 *
#                                                                                                  *
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR                      *
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,                        *
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT_TYPE SHALL THE                     *
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                          *
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,                   *
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE                   *
#  SOFTWARE.                                                                                       *
# **************************************************************************************************
from dataclasses import dataclass, field


# UPS == UPSTREAM === FROM DEVICE
# DNS == DOWNSTREAM === TO DEVICE


@dataclass
class COMMON_MESSAGE_HEADER:
    """This dataclass models the header information common to all Lego(c) messages.

    See https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#common-message-header

    **The length information is added when the actual message is assembled.**

    """

    data: bytearray = field(init=True)

    def __post_init__(self):
        self.m_length: bytearray = self.data[:1]
        print(f"HEADER LENGTH: {self.data[:1]} / {self.data[0]}")
        self.hub_id: bytearray = self.data[1:2]
        print(f"hub ID: {self.data[1:2]} / {self.data[1]}")
        self.m_type: bytearray = self.data[2:3]
        print(f"M_Type: {self.data[2:3]} / {self.data[2]}")

    def __len__(self) -> int:
        return len(self.data)
