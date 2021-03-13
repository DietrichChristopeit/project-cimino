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
from asyncio import Condition, Event
from asyncio.streams import StreamReader, StreamWriter
from datetime import datetime
from typing import List, Optional, Tuple, Union

from LegoBTLE.Device.AMotor import AMotor
from LegoBTLE.LegoWP.messages.downstream import (
    CMD_MOVE_DEV_ABS_POS, CMD_START_MOVE_DEV, CMD_START_MOVE_DEV_DEGREES,
    CMD_START_MOVE_DEV_TIME, DOWNSTREAM_MESSAGE,
    )
from LegoBTLE.LegoWP.messages.upstream import (
    DEV_GENERIC_ERROR_NOTIFICATION, DEV_PORT_NOTIFICATION, DEV_VALUE, EXT_SERVER_NOTIFICATION, HUB_ACTION_NOTIFICATION,
    HUB_ALERT_NOTIFICATION,
    HUB_ATTACHED_IO_NOTIFICATION, PORT_CMD_FEEDBACK,
    )
from LegoBTLE.LegoWP.types import CMD_FEEDBACK_MSG, MOVEMENT, PERIPHERAL_EVENT, PORT


class SingleMotor(AMotor):
    """Objects from this class represent a single Lego Motor.
    
    """
    
    def __init__(self,
                 server: [str, int],
                 port: Union[PORT, bytes],
                 name: str = 'SingleMotor',
                 gearRatio: float = 1.0,
                 debug: bool = False
                 ):
        """
        This object models a single motor at a certain port.

        :param tuple[str,int] server: Tuple with (Host, Port) Information, e.g., ('127.0.0.1', 8888).
        :param Union[PORT, bytes] port: The port, e.g., b'\x02' of the SingleMotor (LegoBTLE.Constants.Port can be utilised).
        :param str name: A friendly name of the this Motor Device, e.g., 'FORWARD_MOTOR'.
        
        :param float gearRatio: The ratio of the number of teeth of the turning gear to the number of teeth of the
            turned gear.
            
        :param bool debug: Turn on/off debug Output.
        """
        
        self._name: str = name
        if isinstance(port, PORT):
            self._port: bytes = port.value
        else:
            self._port: bytes = port

        self._port_free_condition: Condition = Condition()
        self._port_free: Event = Event()
        self._port_free.set()
        
        self._last_cmd_snt: Optional[DOWNSTREAM_MESSAGE] = None
        self._last_cmd_failed: Optional[DOWNSTREAM_MESSAGE] = None
        
        self._current_cmd_feedback_notification: Optional[PORT_CMD_FEEDBACK] = None
        self._current_cmd_feedback_notification_str: Optional[str] = None
        self._cmd_feedback_log: [CMD_FEEDBACK_MSG] = []
        
        self._server: [str, int] = server
        self._ext_srv_connected: Event = Event()
        self._ext_srv_connected.clear()
        self._ext_srv_notification: Optional[EXT_SERVER_NOTIFICATION] = None
        self._ext_srv_notification_log: List[Tuple[float, EXT_SERVER_NOTIFICATION]] = []
        self._connection: [StreamReader, StreamWriter] = (..., ...)
        
        self._port_notification: Optional[DEV_PORT_NOTIFICATION] = None
        self._port2hub_connected: Event = Event()
        self._port2hub_connected.clear()
        
        self._gearRatio: [float, float] = (gearRatio, gearRatio)
        self._current_value: Optional[DEV_VALUE] = None
        self._last_value: Optional[DEV_VALUE] = None
        
        self._measure_distance_start = None
        self._measure_distance_end = None
        self._abs_max_distance = None
        
        self._error_notification: Optional[DEV_GENERIC_ERROR_NOTIFICATION] = None
        self._error_notification_log: List[Tuple[float, DEV_GENERIC_ERROR_NOTIFICATION]] = []
        
        self._hub_action_notification: Optional[HUB_ACTION_NOTIFICATION] = None
        self._hub_attached_io_notification: Optional[HUB_ATTACHED_IO_NOTIFICATION] = None
        self._hub_alert_notification: Optional[HUB_ALERT_NOTIFICATION] = None
        self._hub_alert_notification_log: List[Tuple[float, HUB_ALERT_NOTIFICATION]] = []
        
        self._debug: bool = debug
        return
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str) -> None:
        """Sets a new friendly name.
        
        :param str name: The name.
        :return: Setter, nothing.
        :rtype: None
        
        """
        self._name = str(name)
        return
    
    @property
    def port(self) -> bytes:
        return self._port
    
    @port.setter
    def port(self, port: bytes) -> None:
        """Sets a new Lego(c)-Hub-Port.
        
        :param bytes port: The new port.
        :returns: Setter, nothing.
        :rtype: None
        
        """
        self._port = port
        return

    @property
    def port2hub_connected(self) -> Event:
        return self._port2hub_connected

    @property
    def port_value(self) -> DEV_VALUE:
        return self._current_value

    @port_value.setter
    def port_value(self, value: DEV_VALUE) -> None:
        """
        
        :param DEV_VALUE value: The device value to set.
        :return: Setter, nothing.
        :rtype: None
        """
        self._last_value = self._current_value
        self._current_value = value

        return
    
    @property
    def port_free_condition(self) -> Condition:
        return self._port_free_condition

    @property
    def port_free(self) -> Event:
        return self._port_free

    @property
    def port_notification(self) -> DEV_PORT_NOTIFICATION:
        return self._port_notification

    @port_notification.setter
    def port_notification(self, notification: DEV_PORT_NOTIFICATION) -> None:
        self._port_notification = notification
        return
    
    @property
    def server(self) -> (str, int):
        return self._server
    
    @server.setter
    def server(self, server: Tuple[int, str]) -> None:
        """
        Sets new Server information.
        
        :param tuple[int, str] server: The host and port of the server.
        :return: None
        """
        self._server = server
    
    @property
    def connection(self) -> Tuple[StreamReader, StreamWriter]:
        return self._connection
    
    @connection.setter
    def connection(self, connection: Tuple[StreamReader, StreamWriter]) -> None:
        """
        Sets a new Server <-> Device Read/write connection.
        
        :param connection: The connection.
        :return: None
        """
        self._connection = connection
        return
    
    @property
    def hub_alert_notification(self) -> HUB_ALERT_NOTIFICATION:
        return self._hub_alert_notification
    
    @hub_alert_notification.setter
    def hub_alert_notification(self, notification: HUB_ALERT_NOTIFICATION) -> None:
        self._hub_alert_notification = notification
        self._hub_alert_notification_log.append((datetime.timestamp(datetime.now()), notification))
        return
    
    @property
    def hub_alert_notification_log(self) -> List[Tuple[datetime.timestamp(datetime.now()), HUB_ALERT_NOTIFICATION]]:
        return self._hub_alert_notification_log
    
    @property
    def error_notification(self) -> DEV_GENERIC_ERROR_NOTIFICATION:
        return self._error_notification
    
    @error_notification.setter
    def error_notification(self, error: DEV_GENERIC_ERROR_NOTIFICATION):
        self._error_notification = error
        self._error_notification_log.append((datetime.timestamp(datetime.now()), error))
        return
    
    @property
    def error_notification_log(self) -> List[Tuple[datetime.timestamp(datetime.now()), DEV_GENERIC_ERROR_NOTIFICATION]]:
        return self._error_notification_log
 
    @property
    def gearRatio(self) -> [float, float]:
        return self._gearRatio
    
    @gearRatio.setter
    def gearRatio(self, gearRatio_motor_a: float = 1.0, gearRatio_motor_b: float = 1.0) -> None:
        self._gearRatio = (gearRatio_motor_a, gearRatio_motor_b)
        return
    
    @property
    def ext_srv_connected(self) -> Event:
        return self._ext_srv_connected
    
    @property
    def ext_srv_notification(self) -> EXT_SERVER_NOTIFICATION:
        return self._ext_srv_notification
    
    @ext_srv_notification.setter
    def ext_srv_notification(self, notification: EXT_SERVER_NOTIFICATION):
        if notification is not None:
            self._ext_srv_notification = notification
            if self._debug:
                self._ext_srv_notification_log.append((datetime.timestamp(datetime.now()), notification))
            
            if self._ext_srv_notification.m_event == PERIPHERAL_EVENT.EXT_SRV_CONNECTED:
                self._ext_srv_connected.set()
                self._port_free.set()
            elif self._ext_srv_notification.m_event == PERIPHERAL_EVENT.EXT_SRV_DISCONNECTED:
                self._ext_srv_connected.clear()
        return
    
    @property
    def ext_srv_notification_log(self) -> List[Tuple[datetime.timestamp(datetime.now()), EXT_SERVER_NOTIFICATION]]:
        return self._ext_srv_notification_log
    
    @property
    def last_cmd_snt(self) -> DOWNSTREAM_MESSAGE:
        return self._last_cmd_snt
    
    @last_cmd_snt.setter
    def last_cmd_snt(self, command: DOWNSTREAM_MESSAGE):
        self._last_cmd_snt = command
        return

    @property
    def last_cmd_failed(self) -> DOWNSTREAM_MESSAGE:
        return self._last_cmd_failed

    @last_cmd_failed.setter
    def last_cmd_failed(self, command: DOWNSTREAM_MESSAGE):
        self._last_cmd_failed = command
        return
    
    @property
    def hub_action_notification(self) -> HUB_ACTION_NOTIFICATION:
        return self._hub_action_notification
    
    @hub_action_notification.setter
    def hub_action_notification(self, action: HUB_ACTION_NOTIFICATION):
        self._hub_action_notification = action
        return
    
    @property
    def hub_attached_io_notification(self) -> HUB_ATTACHED_IO_NOTIFICATION:
        return self._hub_attached_io_notification
    
    @hub_attached_io_notification.setter
    def hub_attached_io_notification(self, io_notification: HUB_ATTACHED_IO_NOTIFICATION):
        self._hub_attached_io_notification = io_notification
        if io_notification.m_io_event == PERIPHERAL_EVENT.IO_ATTACHED:
            self._port2hub_connected.set()
            self._port_free.set()
        elif io_notification.m_io_event == PERIPHERAL_EVENT.IO_DETACHED:
            self._port2hub_connected.clear()
            self._port_free.clear()
        return
    
    @property
    def measure_start(self) -> tuple[float, DEV_VALUE]:
        self._measure_distance_start = (datetime.timestamp(datetime.now()), self._current_value)
        return self._measure_distance_start
    
    @property
    def measure_end(self) -> tuple[float, DEV_VALUE]:
        self._measure_distance_end = (datetime.timestamp(datetime.now()), self._current_value)
        return self._measure_distance_end
    
    async def START_MOVE_DEGREES(
            self,
            start_cond: MOVEMENT = MOVEMENT.ONSTART_EXEC_IMMEDIATELY,
            completion_cond: MOVEMENT = MOVEMENT.ONCOMPLETION_UPDATE_STATUS,
            degrees: int = 0,
            speed: int = None,
            abs_max_power: int = 0,
            on_completion: MOVEMENT = MOVEMENT.BREAK,
            use_profile: int = 0,
            use_acc_profile: MOVEMENT = MOVEMENT.USE_ACC_PROFILE,
            use_decc_profile: MOVEMENT = MOVEMENT.USE_DECC_PROFILE,) -> bool:
        """
        See https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#output-sub-command-startspeedfordegrees-degrees-speed-maxpower-endstate-useprofile-0x0b
        
        :param start_cond:
        :param completion_cond:
        :param degrees:
        :param speed:
        :param abs_max_power:
        :param on_completion:
        :param use_profile:
        :param use_acc_profile:
        :param use_decc_profile:
        :return: True if no errors in cmd_send occurred, False otherwise.
        """
        async with self._port_free_condition:
            print(f"{self._name}.START_MOVE_DEGREES WAITING AT THE GATES...")
            await self._port_free_condition.wait_for(lambda: self._port_free.is_set())
            self._port_free.clear()
            print(f"{self._name}.START_MOVE_DEGREES PASSED THE GATES...")
            current_command = CMD_START_MOVE_DEV_DEGREES(
                synced=False,
                port=self._port,
                start_cond=start_cond,
                completion_cond=completion_cond,
                degrees=degrees,
                speed=speed,
                abs_max_power=abs_max_power,
                on_completion=on_completion,
                use_profile=use_profile,
                use_acc_profile=use_acc_profile,
                use_decc_profile=use_decc_profile)
            
            print(f"{self._name}.START_MOVE_DEGREES SENDING {current_command.COMMAND.hex()}...")
            s = await self.cmd_send(current_command)
            
            self._port_free_condition.notify_all()
            print(f"{self._name}.START_MOVE_DEGREES SENDING COMPLETE...")
        return s
    
    async def START_SPEED_TIME(
            self,
            start_cond: MOVEMENT = MOVEMENT.ONSTART_EXEC_IMMEDIATELY,
            completion_cond: MOVEMENT = MOVEMENT.ONCOMPLETION_UPDATE_STATUS,
            time: int = 0,
            speed: int = None,
            direction: MOVEMENT = MOVEMENT.FORWARD,
            power: int = 0,
            on_completion: MOVEMENT = MOVEMENT.BREAK,
            use_profile: int = 0,
            use_acc_profile: MOVEMENT = MOVEMENT.USE_ACC_PROFILE,
            use_decc_profile: MOVEMENT = MOVEMENT.USE_DECC_PROFILE,) -> bool:
        """
        See https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#output-sub-command-startspeedfortime-time-speed-maxpower-endstate-useprofile-0x09
        
        :param start_cond:
        :param completion_cond:
        :param time:
        :param speed:
        :param direction:
        :param power:
        :param on_completion:
        :param use_profile:
        :param use_acc_profile:
        :param use_decc_profile:
        :return: True if no errors in cmd_send occurred, False otherwise.
        """
        async with self._port_free_condition:
            print(f"{self._name}.START_SPEED_TIME WAITING AT THE GATES...")
            await self._port_free_condition.wait_for(lambda: self._port_free.is_set())
            self._port_free.clear()
            print(f"{self._name}.START_SPEED_TIME PASSED THE GATES...")
            current_command = CMD_START_MOVE_DEV_TIME(
                port=self._port,
                start_cond=start_cond,
                completion_cond=completion_cond,
                time=time,
                speed=speed,
                direction=direction,
                power=power,
                on_completion=on_completion,
                use_profile=use_profile,
                use_acc_profile=use_acc_profile,
                use_decc_profile=use_decc_profile)
            
            print(f"{self._name}.START_SPEED_TIME SENDING {current_command.COMMAND.hex()}...")
            s = await self.cmd_send(current_command)
            
            self._port_free_condition.notify_all()
            print(f"{self._name}.START_SPEED_TIME SENDING COMPLETE...")
        return s
    
    async def GOTO_ABS_POS(
            self,
            start_cond=MOVEMENT.ONSTART_EXEC_IMMEDIATELY,
            completion_cond=MOVEMENT.ONCOMPLETION_UPDATE_STATUS,
            speed=0,
            abs_pos=None,
            abs_max_power=0,
            on_completion=MOVEMENT.BREAK,
            use_profile=0,
            use_acc_profile=MOVEMENT.USE_ACC_PROFILE,
            use_decc_profile=MOVEMENT.USE_DECC_PROFILE,) -> bool:
        """
        See https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#output-sub-command-gotoabsoluteposition-abspos-speed-maxpower-endstate-useprofile-0x0d
        
        :param start_cond:
        :param completion_cond:
        :param speed:
        :param abs_pos:
        :param abs_max_power:
        :param on_completion:
        :param use_profile:
        :param use_acc_profile:
        :param use_decc_profile:
        :return: True if no errors in cmd_send occurred, False otherwise.
        """
        async with self._port_free_condition:
            print(f"{self._name}.GOTO_ABS_POS WAITING AT THE GATES...")
            await self._port_free_condition.wait_for(lambda: self._port_free.is_set())
            self._port_free.clear()
            print(f"{self._name}.GOTO_ABS_POS PASSED THE GATES...")
            current_command = CMD_MOVE_DEV_ABS_POS(
                synced=False,
                port=self._port,
                start_cond=start_cond,
                completion_cond=completion_cond,
                speed=speed,
                abs_pos=abs_pos,
                abs_max_power=abs_max_power,
                on_completion=on_completion,
                use_profile=use_profile,
                use_acc_profile=use_acc_profile,
                use_decc_profile=use_decc_profile)
            
            print(f"{self._name}.GOTO_ABS_POS SENDING {current_command.COMMAND.hex()}...")
            s = await self.cmd_send(current_command)
           
            self._port_free_condition.notify_all()
            print(f"{self._name}.GOTO_ABS_POS SENDING COMPLETE...")
        return s
    
    async def START_SPEED(
            self,
            start_cond: MOVEMENT = MOVEMENT.ONSTART_EXEC_IMMEDIATELY,
            completion_cond: MOVEMENT = MOVEMENT.ONCOMPLETION_UPDATE_STATUS,
            speed_ccw: int = None,
            speed_cw: int = None,
            abs_max_power: int = 0,
            profile_nr: int = 0,
            use_acc_profile: MOVEMENT = MOVEMENT.USE_ACC_PROFILE,
            use_decc_profile: MOVEMENT = MOVEMENT.USE_DECC_PROFILE,) -> bool:
        """
        See https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#output-sub-command-startspeed-speed-maxpower-useprofile-0x07
        
        :param start_cond:
        :param completion_cond:
        :param speed_ccw:
        :param speed_cw:
        :param abs_max_power:
        :param profile_nr:
        :param use_acc_profile:
        :param use_decc_profile:
        :return: True if no errors in cmd_send occurred, False otherwise.
        """
        async with self._port_free_condition:
            print(f"{self._name}.START_SPEED WAITING AT THE GATES...")
            await self._port_free_condition.wait_for(lambda: self._port_free.is_set())
            self._port_free.clear()
            print(f"{self._name}.START_SPEED PASSED THE GATES...")
            current_command = CMD_START_MOVE_DEV(
                synced=False,
                port=self._port,
                start_cond=start_cond,
                completion_cond=completion_cond,
                speed_ccw=speed_ccw,
                speed_cw=speed_cw,
                abs_max_power=abs_max_power,
                profile_nr=profile_nr,
                use_acc_profile=use_acc_profile,
                use_decc_profile=use_decc_profile)

            print(f"{self._name}.START_SPEED SENDING {current_command.COMMAND.hex()}...")
            s = await self.cmd_send(current_command)
            
            self._port_free_condition.notify_all()
            print(f"{self._name}.START_SPEED DONE...")
        return s
      
    @property
    def cmd_feedback_notification(self) -> PORT_CMD_FEEDBACK:
        return self._current_cmd_feedback_notification
    
    @cmd_feedback_notification.setter
    def cmd_feedback_notification(self, notification: PORT_CMD_FEEDBACK):
        if not notification.m_cmd_status[notification.m_port[0]].MSG.EMPTY_BUF_CMD_IN_PROGRESS:
            self._port_free.set()
        else:
            self._port_free.clear()
        
        self._cmd_feedback_log.append(notification.m_cmd_feedback)
        self._current_cmd_feedback_notification = notification
        return
    
    # b'\x05\x00\x82\x10\x0a'
    
    
    @property
    def cmd_feedback_log(self) -> [CMD_FEEDBACK_MSG]:
        return self._cmd_feedback_log

    @property
    def debug(self) -> bool:
        return self._debug
