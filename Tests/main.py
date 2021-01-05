import concurrent.futures
import logging
import threading

from signal import SIGINT, signal
from sys import exit
from time import sleep

from Controller.Hub import HubNo2
from Geraet.Motor import EinzelMotor, KombinierterMotor
from Konstanten.Anschluss import Anschluss
from Konstanten.KMotor import KMotor
from MessageHandling.MessageQueue import MessageQueue
from MessageHandling.PubDPSub import PublishingDelegate


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    event.set()
    exit(0)


class EnumTest:
    def __init__(self):
        print("Links {}".format(KMotor.LINKS))
        print("Rechts {}".format(KMotor.RECHTS))
        print("Vor {}".format(KMotor.VOR))
        print("Zurück {}".format(KMotor.ZURUECK))


class TestMessaging:
    def __init__(self, friendlyName: str, MACaddress: str = '90:84:2B:5E:CF:1F', withDelegate=None,
                 messageQueue: MessageQueue = None):
        print("Verbinde mit {}...".format(MACaddress))
        self._jeep = HubNo2(friendlyName, MACaddress, delegate=withDelegate, messageQueue=messageQueue)

    @property
    def jeep(self):
        return self._jeep


def producer(pipeline, event):
    """Pretend we're getting a number from the network."""
    while not event.is_set():
        message = 100
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")


class Testscripts:
    def __init__(self, MACaddress: str = '90:84:2B:5E:CF:1F', withDelegate: bool = False):
        """Testscript-Sammlung"""
        print("Verbinde mit {}...".format(MACaddress))
        self.jeep = HubNo2(MACaddress, "Lego Hub 2", withDelegate)

    def alleMotoren(self):
        """Testet alle Motoren.
            * Vorderradantrieb / Hinterradantrieb einzeln /gemeinsam für Zeiten t mit Kraft 50% / 70% / 100%
            * Lenkung links / rechts 55° / 100°

        :return:
        """
        print("Verbunden...")
        print('Controller Name:', self.jeep.controllerName)
        vorderradantrieb = EinzelMotor(Anschluss.A, uebersetzung=2.67, name="Vorderradantrieb")
        self.jeep.registriere(vorderradantrieb)
        print("Vorderradantrieb Anschluss \"{}\" hinzugefügt...".format(vorderradantrieb.anschluss))
        self.jeep.fuehreBefehlAus(vorderradantrieb.reset(), mitRueckMeldung=True)
        sleep(1)
        hinterradantrieb = EinzelMotor(Anschluss.B, uebersetzung=2.67, name="Hinterradantrieb")
        self.jeep.registriere(hinterradantrieb)
        print("Hinterradantrieb an Anschluss \"{}\" hinzugefügt...".format(hinterradantrieb.anschluss))
        self.jeep.fuehreBefehlAus(hinterradantrieb.reset(), mitRueckMeldung=True)
        sleep(1)
        gemeinsamerAntrieb = KombinierterMotor(vorderradantrieb, hinterradantrieb, uebersetzung=2.67,
                                               name="Vorder- und Hinterrad gemeinsam")
        self.jeep.registriere(gemeinsamerAntrieb)
        print("gemeinsamer MotorTyp: \"{}\" hinzugefügt...".format(gemeinsamerAntrieb.nameMotor))
        self.jeep.fuehreBefehlAus(gemeinsamerAntrieb.reset(), mitRueckMeldung=True)
        sleep(1)
        lenkung = EinzelMotor(Anschluss.C, uebersetzung=1.00, name="Lenkung")
        self.jeep.registriere(lenkung)
        print("Lenkung hinzugefügt...")
        self.jeep.fuehreBefehlAus(lenkung.reset(), mitRueckMeldung=True)
        sleep(1.5)
        print("Drehe Vorderräder für 2560ms mit halber Kraft vorwärts...")
        sleep(0.5)
        dreheVorderrad = vorderradantrieb.dreheMotorFuerT(2560, KMotor.VOR, 50, KMotor.BREMSEN)
        self.jeep.fuehreBefehlAus(dreheVorderrad, mitRueckMeldung=True)
        sleep(1.5)
        print("Drehe Hinterräder für 2560ms mit halber Kraft vorwärts...")
        sleep(0.5)
        dreheHinterrad = hinterradantrieb.dreheMotorFuerT(2560, KMotor.VOR, 70, KMotor.AUSLAUFEN)
        self.jeep.fuehreBefehlAus(dreheHinterrad, mitRueckMeldung=True)
        sleep(1.5)
        print("Drehe Vorder- und Hinterräder gemeinsam NICHT SYNCHRONISIERT für 4000ms mit voller Kraft rückwärts..")
        sleep(0.5)
        dreheVorderrad = vorderradantrieb.dreheMotorFuerT(4000, KMotor.ZURUECK, 100, KMotor.AUSLAUFEN)
        dreheHinterrad = hinterradantrieb.dreheMotorFuerT(4000, KMotor.ZURUECK, 100, KMotor.BREMSEN)
        self.jeep.fuehreBefehlAus(dreheVorderrad, mitRueckMeldung=True)
        self.jeep.fuehreBefehlAus(dreheHinterrad, mitRueckMeldung=True)
        sleep(1.5)
        print("Drehe Vorder- und Hinterräder gemeinsam SYNCHRONISIERT für 4000ms mit voller Kraft vorwärts..")
        sleep(0.5)
        dreheGemeinsamenAntrieb = gemeinsamerAntrieb.dreheMotorFuerT(4000, KMotor.VOR, 100, zumschluss=KMotor.BREMSEN)
        self.jeep.fuehreBefehlAus(dreheGemeinsamenAntrieb, mitRueckMeldung=True)
        sleep(6)
        print("Lenke um 55° mit halber Kraft nach links...")
        sleep(0.5)
        lenkeLinks = lenkung.dreheMotorFuerGrad(55, KMotor.LINKS, 50, KMotor.BREMSEN)
        self.jeep.fuehreBefehlAus(lenkeLinks, mitRueckMeldung=True)
        sleep(1.5)
        print("Lenke um 100° mit halber Kraft nach rechts...")
        sleep(0.5)
        lenkeRechts = lenkung.dreheMotorFuerGrad(100, KMotor.RECHTS, 50, KMotor.BREMSEN)
        self.jeep.fuehreBefehlAus(lenkeRechts, mitRueckMeldung=True)
        sleep(1.5)
        Testscripts.stopTests(self.jeep)

    @staticmethod
    def stopTests(jeep: HubNo2):
        print("Trenne Verbindung...")
        jeep.schalteAus()
        print("***Programmende***")


if __name__=='__main__':
    signal(SIGINT, handler)

    p = MessageQueue()
    publisher = PublishingDelegate("Pipeline on Hub", p)

    test = TestMessaging("Jeep", '90:84:2B:5E:CF:1F', publisher, p)



    # event.wait()
    #notif_thr = threading.Thread(target=test.jeep.receiveNotification(event))  # Event Loop als neuer Thread
    #notif_thr.start()
    #sleep(1)

    test.jeep.fuehreBefehlAus(bytes.fromhex('0a004100020100000001'), mitRueckMeldung=True)
    print("Noch da")
