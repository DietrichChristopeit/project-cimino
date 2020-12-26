from abc import ABC

from Motor.EinzelMotor import EinzelMotor
from Motor.Motor import Motor


class KombinierterMotor(Motor, ABC):
    '''Kombination aus 2 (zwei) verschiedenen Motoren. Kommandos-Ausführung ist synchronisiert.
    '''

    def __init__(self, ersterMotor: EinzelMotor, zweiterMotor: EinzelMotor, name: str = None):
        """

        :param ersterMotor:
        :param zweiterMotor:
        :param name:
        """
        self.ersterMotorPort = ersterMotor.anschlussDesMotors
        self.zweiterMotorPort = zweiterMotor.anschlussDesMotors
        self.virtualPort = None
        self.name = name

    @property
    def nameDesMotors(self):
        return self.name

    @property
    def anschlussDesMotors(self):
        return self.virtualPort
