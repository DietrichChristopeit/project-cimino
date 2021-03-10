﻿# **************************************************************************************************
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
import asyncio
from abc import ABC, abstractmethod
from asyncio import Condition, Event, StreamReader, StreamWriter

from LegoBTLE.LegoWP.messages.downstream import (
    CMD_EXT_SRV_CONNECT_REQ, CMD_EXT_SRV_DISCONNECT_REQ,
    CMD_PORT_NOTIFICATION_DEV_REQ, DOWNSTREAM_MESSAGE,
    )
from LegoBTLE.LegoWP.messages.upstream import (
    DEV_GENERIC_ERROR_NOTIFICATION, DEV_PORT_NOTIFICATION, DEV_VALUE, EXT_SERVER_NOTIFICATION,
    HUB_ACTION_NOTIFICATION,
    HUB_ALERT_NOTIFICATION, HUB_ATTACHED_IO_NOTIFICATION, PORT_CMD_FEEDBACK, UpStreamMessageBuilder,
    )
from LegoBTLE.LegoWP.types import CMD_FEEDBACK_MSG, MESSAGE_TYPE


class Device(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The friendly name of the Device.
        
        :return: The string name
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def connection(self) -> [StreamReader, StreamWriter]:
        """
        A tuple holding the read and write connection to the Server Module given to each Device at instantiation.
        
        :return: tuple[StreamReader, StreamWriter]
        """
        raise NotImplementedError
    
    @connection.setter
    @abstractmethod
    def connection(self, connection: [StreamReader, StreamWriter]) -> None:
        """
        Sets a new connection for the device. The Device then only has the connection information and will send
        commands to the new destination.
        Beware: The device will not get not re-register at the destination AUTOMATICALLY. Registering at the
        destination must be invoked MANUALLY.
        
        :param connection: The new destination information as tuple[Streamreader, Streamwriter].
        :return: None
        :returns: None
        """
        raise NotImplementedError

    @property
    def socket(self) -> int:
        """
        The socket information for the Device's connection.
        
        :return: The socket nr.
        :returns: int
        """
        return self.connection[1].get_extra_info('socket')
    
    @property
    @abstractmethod
    def server(self) -> tuple[str, int]:
        """
        The Server information (host, port)
        
        :return: The Server Information.
        :returns: tuple[str, int]
        """
        raise NotImplementedError

    @property
    def host(self) -> str:
        """
        For convenience, the host part alone.
        
        :returns: str
        """
        return self.server[0]

    @property
    def srv_port(self) -> int:
        """
        For convenience, the server-port part alone.
        
        :return: int
        """
        return self.server[1]
    
    @property
    @abstractmethod
    def port(self) -> bytes:
        """
        Property for the Devices's Port at the Lego Hub.
        
        :return: bytes
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def port_free_condition(self) -> Condition:
        """
        Locking condition for when the Lego Port is not occupied with command execution for this Device's Lego-Port.
        
        :return: Condition
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def port_free(self) -> Event:
        """
        The Event for indicating whether the Device's Lego-Hub-Port is free (Event set) or not (Event cleared).
        
        :return: Event
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def port_value(self) -> DEV_VALUE:
        """
        The current value (for motors degrees (SI deg) of the Device. Setting different units can be achieved by
        setting the Device's capabilities (guess) - currently not investigated further.
        
        :return: UPSTREAM_MESSAGE
        """
        raise NotImplementedError
    
    @port_value.setter
    @abstractmethod
    def port_value(self, port_value: DEV_VALUE) -> None:
        """
        Sets the current value (for motors degrees (SI deg) of the Device. Setting different units can be achieved by
        setting the Device's capabilities (guess) - currently not investigated further.

        :return: None
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def port_notification(self) -> DEV_PORT_NOTIFICATION:
        """
        The device's Lego-Hub-Port notification as UPSTREAM_MESSAGE.
        Response to a PORT_NOTIFICATION_REQ.
        
        :return: UPSTREAM_MESSAGE
        """
        raise NotImplementedError

    @port_notification.setter
    @abstractmethod
    def port_notification(self, port_notification: DEV_PORT_NOTIFICATION) -> None:
        """
        Sets the device's Lego-Hub-Port notification as UPSTREAM_MESSAGE.
        Response to a PORT_NOTIFICATION_REQ.

        :return: None
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def port2hub_connected(self) -> Event:
        """
        Event indicating if the Lego-Hub-Port is connected to the Server module.
        Not used.
        
        :return: Event
        :deprecated:
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def last_cmd_snt(self) -> DOWNSTREAM_MESSAGE:
        raise NotImplementedError

    @last_cmd_snt.setter
    @abstractmethod
    def last_cmd_snt(self, command: DOWNSTREAM_MESSAGE):
        raise NotImplementedError

    @property
    @abstractmethod
    def last_cmd_failed(self) -> DOWNSTREAM_MESSAGE:
        raise NotImplementedError

    @last_cmd_failed.setter
    @abstractmethod
    def last_cmd_failed(self, command: DOWNSTREAM_MESSAGE):
        raise NotImplementedError

    @property
    @abstractmethod
    def hub_alert_notification(self) -> HUB_ALERT_NOTIFICATION:
        raise NotImplementedError
    
    @hub_alert_notification.setter
    def hub_alert_notification(self, hub_alert_notification: HUB_ALERT_NOTIFICATION):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def ext_srv_connected(self) -> Event:
        raise NotImplementedError
    
    @property
    def ext_srv_notification(self) -> EXT_SERVER_NOTIFICATION:
        raise NotImplementedError
    
    @ext_srv_notification.setter
    def ext_srv_notification(self, ext_srv_notification: EXT_SERVER_NOTIFICATION):
        raise NotImplementedError
    
    async def connect_srv(self) -> bool:
        current_command = CMD_EXT_SRV_CONNECT_REQ(port=self.port)
        print(f"CONNECT_REQ: {current_command.COMMAND.hex()}")
        async with self.port_free_condition:
            await self.port_free_condition.wait_for(lambda: self.port_free.is_set())
            self.port_free.clear()
            s = await self.cmd_send(current_command)
            self.port_free.set()
            self.port_free_condition.notify_all()
        return s
    
    async def EXT_SRV_DISCONNECT_REQ(self) -> bool:
        current_command = CMD_EXT_SRV_DISCONNECT_REQ(port=self.port)

        async with self.port_free_condition:
            await self.port_free_condition.wait_for(lambda: self.port_free.is_set())
            self.port_free.clear()
            s = await self.cmd_send(current_command)
            self.port_free.set()
            self.port_free_condition.notify_all()
        return s

    async def REQ_PORT_NOTIFICATION(self) -> bool:
        current_command = CMD_PORT_NOTIFICATION_DEV_REQ(port=self.port)
        async with self.port_free_condition:
            await self.port_free_condition.wait_for(lambda: self.port_free.is_set())
            self.port_free.clear()
            s = await self.cmd_send(current_command)
            self.last_cmd_snt = current_command
            self.port_free.set()
            self.port_free_condition.notify_all()
        return s
    
    async def EXT_SRV_CONNECT_REQ(self, host: str = '127.0.0.1', srv_port: int = 8888) -> bool:
        try:
            # device.ext_srv_notification = None
            self.ext_srv_connected.clear()
            print(
                    f"[CLIENT]-[MSG]: ATTEMPTING TO REGISTER [{self.name}:{self.port.hex()}] WITH SERVER "
                    f"[{self.server[0]}:"
                    f"{self.server[1]}]...")
            self.connection = await asyncio.open_connection(host=self.server[0], port=self.server[1])
        except ConnectionError:
            raise ConnectionError(
                    f"COULD NOT CONNECT [{self.name}:{self.port}] with [{self.server[0]}:{self.server[1]}...")
        else:
            self.ext_srv_connected.set()
            # send a Request for Registration to Server
            s = await self.connect_srv()
            # self.connection[1].write(REQUEST_MESSAGE.COMMAND[:2])
            # await self.connection[1].drain()
            # self.connection[1].write(REQUEST_MESSAGE.COMMAND[1:])
            # await self.connection[1].drain()  # CONN_REQU sent
            bytesToRead: bytes = await self.connection[0].readexactly(1)  # waiting for answer from Server
            data = bytearray(await self.connection[0].readexactly(int(bytesToRead.hex(), 16)))
            print(f"[{self.name}:{self.port.hex()}]-[MSG]: RECEIVED CON_REQ ANSWER: {data.hex()}")
            self.dispatch_upstream_msg(data=data)
            await self.ext_srv_connected.wait()
            return s
    
    async def listen_srv(self) -> bool:
        print(f"[{self.name}:{self.port.hex()}]-[MSG]: LISTENING ON SOCKET [{self.socket}]...")
        while self.ext_srv_connected.is_set():
            try:
                bytes_to_read = await self.connection[0].readexactly(n=1)
                data = bytearray(await self.connection[0].readexactly(n=int(bytes_to_read.hex(), 16)))
            except (ConnectionError, IOError):
                self.ext_srv_connected.clear()
            else:
                print(f"[{self.name}:{self.port.hex()}]-[MSG]: RECEIVED DATA WHILE LISTENING: {data.hex()}")
                self.dispatch_upstream_msg(UpStreamMessageBuilder(data).build())
            await asyncio.sleep(.001)
        print(f"[{self.server[0]}:{self.server[1]}]-[MSG]: CONNECTION CLOSED...")
        return False
    
    async def cmd_send(self, cmd: DOWNSTREAM_MESSAGE) -> bool:
        try:
            self.connection[1].write(cmd.COMMAND[:2])
            await self.connection[1].drain()
            self.connection[1].write(cmd.COMMAND[1:])
            await self.connection[1].drain()  # cmd sent
        except ConnectionError as ce:
            print(f"[{self.name}:{self.port}]-[MSG]: SENDING {cmd.COMMAND.hex()} OVER {self.socket} FAILED: {ce.args}...")
            self.last_cmd_failed = cmd
            return False
        else:
            self.last_cmd_snt = cmd
            return True
        
    def dispatch_upstream_msg(self, data: bytearray) -> bool:
        RETURN_MESSAGE = UpStreamMessageBuilder(data).build()
        if data[2] == int(MESSAGE_TYPE.UPS_DNS_EXT_SERVER_CMD.hex(), 16):
            self.ext_srv_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_PORT_VALUE:
            self.port_value = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_PORT_CMD_FEEDBACK:
            self.cmd_feedback_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_HUB_GENERIC_ERROR:
            self.generic_error_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_PORT_NOTIFICATION:
            self.port_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_DNS_EXT_SERVER_CMD:
            self.ext_srv_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_HUB_ATTACHED_IO:
            self.hub_attached_io_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_DNS_HUB_ACTION:
            self.hub_action_notification = RETURN_MESSAGE
        elif RETURN_MESSAGE.m_type == MESSAGE_TYPE.UPS_DNS_HUB_ALERT:
            self.hub_alert_notification = RETURN_MESSAGE
        else:
            raise TypeError
        return True
    
    @property
    @abstractmethod
    def generic_error_notification(self) -> DEV_GENERIC_ERROR_NOTIFICATION:
        """
        Contains the current notification for a Lego-Hub-Error.
        
        :return: The ERROR-Notification
        """
        raise NotImplementedError
    
    @generic_error_notification.setter
    @abstractmethod
    def generic_error_notification(self, error: DEV_GENERIC_ERROR_NOTIFICATION) -> None:
        """
        Sets a Lego-Hub-ERROR_NOTIFICATION.
        
        :param error: The Lego-Hub-ERROR_NOTIFICATION.
        :return: None
        """
        raise NotImplementedError
    
    @property
    def last_error(self) -> tuple[bytes, bytes]:
        """
        The last (current) ERROR-Message as tuple of bytes indicating the erroneous command and the status of it.
        
        :return: tuple[bytes, bytes]
        """
        if self.generic_error_notification is not None:
            return self.generic_error_notification.m_error_cmd, self.generic_error_notification.m_cmd_status
        else:
            return b'', b''
    
    @property
    @abstractmethod
    def hub_action_notification(self) -> HUB_ACTION_NOTIFICATION:
        """
        Indicates what the Lego-Hub is about to do (SHUTDOWN, DISCONNECT etc.).
        
        :return: The imminent action.
        """
        raise NotImplementedError
    
    @hub_action_notification.setter
    @abstractmethod
    def hub_action_notification(self, action: HUB_ACTION_NOTIFICATION) -> None:
        """
        Sets the notification of about what the Lego-Hub is about to do (SHUTDOWN, DISCONNECT etc.).

        :return: None.
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def hub_attached_io_notification(self) -> HUB_ATTACHED_IO_NOTIFICATION:
        """
        A Lego-Hub-Notification for the status of attached Devices (ATTACHED, DETACHED, etc.)
        
        :return: The HUB_ATTACHED_IO_NOTIFICATION .
        """
        raise NotImplementedError
    
    @hub_attached_io_notification.setter
    @abstractmethod
    def hub_attached_io_notification(self, io_notification: HUB_ATTACHED_IO_NOTIFICATION) -> None:
        """
        A Lego-Hub-Notification for the status of attached Devices (ATTACHED, DETACHED, etc.)

        :return: None.
        """
        raise NotImplementedError
      
    @property
    @abstractmethod
    def cmd_feedback_notification(self) -> PORT_CMD_FEEDBACK:
        raise NotImplementedError
    
    @cmd_feedback_notification.setter
    def cmd_feedback_notification(self, notification: PORT_CMD_FEEDBACK):
        raise NotImplementedError

    @property
    def cmd_feedback_notification_str(self) -> str:
        return self.cmd_feedback_notification.__str__()
    
    @property
    @abstractmethod
    def command_feedback_log(self) -> list[CMD_FEEDBACK_MSG]:
        """
        A log of all past Command Feedback Messages.
    
        :return: the Log
        """
        raise NotImplementedError
    
    @command_feedback_log.setter
    @abstractmethod
    def command_feedback_log(self, feedback_msb: CMD_FEEDBACK_MSG) -> None:
        """
       Add an Entry to the log of all past Command Feedback Messages.

       :param feedback: The current Command Feedback Message.
       :return: None
       """
        raise NotImplementedError
