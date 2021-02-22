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
from LegoBTLE.Constants.MotorConstant import M_Constants, MotorConstant
from LegoBTLE.Constants.Port import Port
# UPSTREAM === TO DEVICE
# DOWNSTREAM === FROM DEVICE


class Message(dict):
    
    DEVICE_TYPE = {
        b'\x01': b'INTERNAL_MOTOR',
        b'\x02': b'SYSTEM_TRAIN_MOTOR',
        b'\x05': b'BUTTON',
        b'\x08': b'LED',
        b'\x14': b'VOLTAGE',
        b'\x15': b'CURRENT',
        b'\x16': b'PIEZO_TONE',
        b'\x17': b'RGB_LIGHT',
        b'\x22': b'EXTERNAL_TILT_SENSOR',
        b'\x23': b'MOTION_SENSOR',
        b'\x25': b'VISION_SENSOR',
        b'\x2e': b'EXTERNAL_MOTOR',
        b'\x2f': b'EXTERNAL_MOTOR_WITH_TACHO',
        b'\x27': b'INTERNAL_MOTOR_WITH_TACHO',
        b'\x28': b'INTERNAL_TILT'
        }
    
    HUB_ACTIONS = {
        b'\x01': b'HUB_SWITCH_OFF',
        b'\x02': b'HUB_DISCONNECT',
        b'\x03': b'HUB_VCC_PORT_CTRL_ON',
        b'\x04': b'HUB_VCC_PORT_CTRL_OFF',
        b'\x05': b'HUB_INDICATE_BUSY_ON',
        b'\x06': b'HUB_INDICATE_BUSY_OFF',
        b'\x2F': b'HUB_FAST_SHUTDOWN'
        }
    
    STATUS = {
        b'\x00': b'DISABLED',
        b'\x01': b'ENABLED'
        }
        
    HUB_ALERT_TYPES = {
        b'\x01': b'LOW_V',
        b'\x02': b'HIGH_CURRENT',
        b'\x03': b'LOW_SIG_STRENGTH',
        b'\x04': b'OVER_PWR_COND'
        }
        
    EVENT = {
        b'\x00': b'IO_DETACHED',
        b'\x01': b'IO_ATTACHED',
        b'\x02': b'VIRTUAL_IO_ATTACHED'
        }
       
    RETURN_CODE = {
        RFR: bytes = b'\x00'
        DCD: bytes = b'\xff'
        ACK: bytes = b'\x01'
        MACK: bytes = b'\x02'
        BUFFER_OVERFLOW: bytes = b'\x03'
        TIMEOUT: bytes = b'\x04'
        COMMAND_NOT_RECOGNIZED: bytes = b'\x05'
        INVALID_USE: bytes = b'\x06'
        OVERCURRENT: bytes = b'\x07'
        INTERNAL_ERROR: bytes = b'\x08'
        EXEC_FINISHED: bytes =b'\x0a'
    }
       
    SUBCOMMAND = {
         T_UNREGULATED: bytes= b'\x01'
         T_UNREGULATED_SYNC: bytes= b'\x02'
         P_SET_TIME_TO_FULL: bytes= b'\x05'
         P_SET_TIME_TO_ZERO: bytes= b'\x06'
         T_UNLIMITED: bytes= b'\x07'
         T_UNLIMITED_SYNC: bytes= b'\x08'
         T_FOR_DEGREES: bytes= b'\x0b'
         T_FOR_TIME: bytes= b'\x09'
         T_FOR_TIME_SYNC: bytes= b'\x0a'
         SND_DIRECT: bytes= b'\x51'
         REG_W_SERVER: bytes= b'\x00'
        }
     
    DIRECTCOMMAND = {
        b'\x02': b'D_RESET'
        }


    def MESSAGE(payload: bytearray):
    
        MESSAGE_TYPES: dict = {
            
            }
        
        COMMON_HEADER: dict = {
            'length': bytes(payload[0]),
            'hub_id': b'x00',
            'm_type': MESSAGE_TYPES.get(bytes(payload[2]), b''),
            
            
            }
        
        
        
        schema: dict = {
            b'\x01' b'UPS_GENERAL_HUB_NOTIFICATIONS', DEVICE_TYPE},
            b'\x02' b'HUB_ACTION_TYPE', HUB_ACTIONS},
            b'\x03' b'HUB_ALERT_TYPE', HUB_ALERT_TYPES},
            b'\x04' b'DNS_GENERAL_HUB_NOTIFICATIONS', (DEVICE_TYPE, )},
            b'\x05' b'DNS_ERROR', },
            b'\x61' b'SND_COMMAND_SETUP_SYNC_MOTOR', },
            b'\x81' b'SND_MOTOR_COMMAND', },
            b'\x82' b'RCV_COMMAND_STATUS', },
            b'\x45' b'RCV_DATA', },
            b'\x41' b'SND_REQ_DEVICE_NOTIFICATION', },
            b'\x47' b'RCV_PORT_STATUS', },
            b'\x00' b'SND_SERVER_ACTION', },
            b' '    'EOM'
            }
        
        return schema.get(bytes(payload[3]))
    
    """The UpStreamMessage class models a UpStreamMessage sent to the Hub as well as the feedback, i.e., the port_status, following
    command execution.
    """
    
    def __init__(self, payload: bytes = b''):
        """The data structure for a command which is sent to the Hub for execution.
        The entire byte sequence that comprises length, cmd op_code, cmd parameter values etc is called
        payload here.

        :param payload:
            The byte sequence comprising the command.
        """
        super().__init__()
        
        self._payload: bytearray = bytearray(payload.strip(b' '))
        
        self._length: int = self._payload[0]
        self._type = MESSAGE_TYPE.get(self._payload[2].to_bytes(1, 'little', signed=False), None)
        self._port: bytes = b''
        self._port_status: bytes = b''
        self._subCommand: bytes = b''
        self._deviceType: bytes = b''
        self._directCommand: bytes = b''
        self._powerA: bytes = b''
        self._powerB: bytes = b''
        self._final_action: bytes = b''
        self._return_code: bytes = b''
        self._payload: bytearray = bytearray(b' ')
        
        if self._type == b'SND_SERVER_ACTION':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._subCommand: bytes = SUBCOMMAND.get(self._payload[4].to_bytes(1, 'little', signed=False), None)
            self._return_code = RETURN_CODE.get(self._payload[5].to_bytes(1, 'little', signed=False), None)
        if self._type == b'RCV_DEVICE_INIT':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._event: bytes = EVENT.get(self._payload[4].to_bytes(1, 'little', signed=False), None)
            self._deviceType: bytes = DEVICE_TYPE.get(self._payload[5].to_bytes(1, 'little', signed=False), None)
        elif self._type == b'ALERT':
            pass
        elif self._type == b'RCV_ERROR':
            self._error_trigger_cmd: bytes = MESSAGE_TYPE.get(self._payload[3].to_bytes(1, 'little', signed=False),
                                                              None)
            self._return_code: bytes = RETURN_CODE.get(self._payload[4].to_bytes(1, 'little', signed=False), None)
            self._return_code: bytes = self._payload[4:]
        elif self._type == b'RCV_COMMAND_STATUS':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._return_code: bytes = RETURN_CODE.get(self._payload[4].to_bytes(1, 'little', signed=False), None)
        elif self._type == b'RCV_DATA':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._return_code: bytes = self._payload[4:]
        elif self._type == b'SND_REQ_DEVICE_NOTIFICATION':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._port_status: bytes = STATUS.get(self._payload[self._length - 1].to_bytes(1, 'little', signed=False),
                                                  None)
            self._return_code: bytes = STATUS.get(self._payload[self._length - 1].to_bytes(1, 'little', signed=False),
                                                  None)
        elif self._type == b'SND_MOTOR_COMMAND':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._sac: bytes = self._payload[4].to_bytes(1, 'little', signed=False)
            self._subCommand: bytes = SUBCOMMAND.get(self._payload[5].to_bytes(1, 'little', signed=False), None)
            if self._subCommand == b'SND_DIRECT':
                self._directCommand = DIRECTCOMMAND.get(self._payload[6].to_bytes(1, 'little', signed=False), None)
                self._return_code: bytes = self._payload[7:]
            else:
                self._powerA: bytes = self._payload[self._length - 4].to_bytes(1, 'little', signed=False)
                self._powerB: bytes = self._payload[self._length - 3].to_bytes(1, 'little', signed=False)
                self._finalAction = M_Constants.get(self._payload[self._length - 2].to_bytes(1, 'little', signed=False),
                                                    None)
        elif self._type == b'RCV_PORT_STATUS':
            self._port: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            self._port_status: bytes = STATUS.get(self._payload[self._length - 1].to_bytes(1, 'little', signed=False),
                                                  None)
            self._return_code: bytes = STATUS.get(self._payload[self._length - 1].to_bytes(1, 'little', signed=False),
                                                  None)
        elif self._type == b'SND_COMMAND_SETUP_SYNC_MOTOR':
            self._port_1 = Port.get(self._payload[self._length - 2].to_bytes(1, 'little', signed=False), b'')
            self._port_2 = Port.get(self._payload[self._length - 1].to_bytes(1, 'little', signed=False), b'')
        self._payload: bytearray = bytearray(self._payload + b' ')
        return
    
    def __missing__(self, missingkey) -> bytes:
        return b''
    
    def decode(self) -> bytearray:
        
        return bytearray(b'')
    
    def encode(self, payload: bytearray) -> Message:
        if payload == b'':
            return {}
        else:
            message: dict = {}
            message['payload']: bytearray = bytearray(payload.strip(b' '))
            message['length']: bytes = payload[0]
            message['m_type']: bytes = MESSAGE_TYPE.get(bytes(payload[2]), b'')
            if message['m_type'] == b'HUB_ACTION_TYPE':
                message['cmd'] = payload[3]
            if message['m_type'] == b'HUB_ALERT_TYPE':
                message['s_type'] = HUB_ALERT_TYPES[bytes(payload[4])]
            if message['type'] == b'RCV_DEVICE_INIT':
                pass
            if message['type'] == b'RCV_ERROR':
                pass
            if message['type'] == b'SND_COMMAND_SETUP_SYNC_MOTOR':
                pass
            if message['type'] == b'SND_MOTOR_COMMAND':
                pass
            if message['type'] == b'RCV_COMMAND_STATUS':
                pass
            if message['type'] == b'RCV_DATA':
                pass
            if message['type'] == b'SND_REQ_DEVICE_NOTIFICATION':
                pass
            if message['type'] == b'RCV_PORT_STATUS':
                pass
            if message['type'] == b'SND_SERVER_ACTION':
                pass
            message['subCommand']: bytes = b''
            message['port']: bytes = self._payload[3].to_bytes(1, 'little', signed=False)
            message['port_status']: bytes = STATUS.get(payload[payload[0] - 1].to_bytes(1, 'little', signed=False),
                                                       b'')
            message['event']: bytes = b''
            message['deviceType']: bytes = b''
            message['directCommand']: bytes = b''
            message['powerA']: bytes = b''
            message['powerB']: bytes = b''
            message['port_1']: bytes = Port.get(payload[payload[0] - 2].to_bytes(1, 'little', signed=False), b'')
            message['port_2']: bytes = Port.get(payload[payload[0] - 1].to_bytes(1, 'little', signed=False), b'')
            message['final_action']: bytes = b''
            message['return_code']: bytes = b''
        return message
    
    @property
    def payload(self) -> bytes:
        return self._payload
    
    @payload.setter
    def payload(self, p: bytes):
        self._payload = p
        return
    
    @property
    def port(self) -> bytes:
        return self._port
    
    @property
    def port_status(self) -> bytes:
        return self._port_status
    
    @property
    def m_type(self) -> bytes:
        return self._type
    
    @property
    def return_code(self) -> bytes:
        return self._return_code
    
    @property
    def return_code_str(self) -> str:
        return RETURN_CODE_val[RETURN_CODE_key.index(bytes(self._return_code[0]))].decode('utf-8')
    
    @property
    def dev_type(self) -> bytes:
        return self._deviceType
    
    @property
    def event(self) -> bytes:
        return self._event
    
    @property
    def error_trigger_cmd(self) -> bytes:
        return self._error_trigger_cmd
    
    @property
    def cmd(self) -> bytes:
        return self._subCommand
    
    @property
    def cmd_direct(self) -> bytes:
        return self._directCommand
    
    @property
    def powerA(self) -> bytes:
        return self._powerA
    
    @property
    def powerB(self) -> bytes:
        return self._powerB
    
    @property
    def final_action(self) -> MotorConstant:
        return self._finalAction