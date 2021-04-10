# encoding: utf-8
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
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE                     *
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                          *
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,                   *
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE                   *
#  SOFTWARE.                                                                                       *
# **************************************************************************************************

"""This Module shall provide an Exception Framework for things that can go wrong

Things that can go wrong are for instance:

* There is no Hub-Instance to connect to the Server.
* Wrong answer from Server
"""
from typing import List

from LegoBTLE.Device.ADevice import Device
from LegoBTLE.LegoWP.types import C


class ExperimentException(Exception):
    
    def __init__(self, message):
        self._message = message
        
        super().__init__(self._message)
        return
    
    def args(self):
        return self._message


class LegoBTLENoHubToConnectError(ExperimentException):
    
    def __init__(self, devices: List[Device], message: str = "No Hub given. Cannot connect to server "
                                                             "without one Hub Instance."):
        self._message = message
        self._devices = devices
        
        super().__init__(message=message)
        return
    
    def __str__(self):
        return f"{self._devices} -> {self._message}"


class ServerClientRegisterError(ExperimentException):
    
    def __init__(self, message: str):
        self._message = "CLIENT OPENED CONNECTION BUT DID NOT REQUEST REGISTRATION: " + message
        
        super().__init__(message=message)
        return
    
    def __str__(self):
        return f"{C.BOLD}{C.FAIL}{self._message}{C.ENDC}"