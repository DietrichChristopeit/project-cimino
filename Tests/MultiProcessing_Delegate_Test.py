# MIT License Copyright (c) 2021 Dietrich Christopeit

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import threading
from multiprocessing import Process, Condition, Queue
from random import uniform

from bluepy import btle
from time import sleep

stop_flag = False  # Globale Variable, um dem Notif.Thread ein Stopp mitzuteilen


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, rslt: Queue):
        btle.DefaultDelegate.__init__(self)
        self._rslt = rslt

    def handleNotification(self, cHandle, data):  # Eigentliche Callbackfunktion
        # print('Notification erhalten : {}'.format(data.hex()))
        self._rslt.put(data.hex())
        return


Q_rslt: Queue = Queue(maxsize=300)
print('Ich verbinde...')
dev = btle.Peripheral('90:84:2B:5E:CF:1F')  # BLE Device (hier Lego Move Hub)
sleep(1)
dev.withDelegate(MyDelegate(rslt=Q_rslt))  # Instanzierung Delegationsobjekt für dieses Device
sleep(1)
# Client Characteristic Configuration (0x0f) für das Einschalten der Notifications
dev.writeCharacteristic(0x0f, b'\x01\x00')
sleep(1)
# Dummybefehl (LED auf Grün) damit Notifications ausgegeben werden: Programmabsturz!!!!
dev.writeCharacteristic(0x0e, b'\x08\x00\x81\x32\x11\x51\x00\x05')
sleep(1)
# Notifications für grünen Taster aktivieren
dev.writeCharacteristic(0x0e, b'\x05\x00\x01\x02\x02')
sleep(1)
cvNotif: Condition = Condition()


def event_loop():
    global stop_flag
    while not stop_flag:  # Schleife für das Warten auf Notifications
        if dev.waitForNotifications(.001):
            continue
    print('.', end='')
    print('Notification Thread Tschuess!')


def dummyLoop():
    print("dummy_loop started")
    while not stop_flag:
        if not Q_rslt.qsize() == 0:
            print("Notification DATA: {}".format(Q_rslt.get()))
            sleep(uniform(0.001, 0.01))

    print("dummy process shutdown")


# notif_thr = threading.Thread(target=event_loop, daemon=True)  # Event Loop als neuer Process
# notif_thr = threading.Thread(target=event_loop, daemon=True)
notif_thr = threading.Thread(target=event_loop, daemon=True)
notif_thr.start()

dummyProcess = Process(target=dummyLoop, daemon=True)
dummyProcess.start()

sleep(1)
print("ABO ALLE")
dev.writeCharacteristic(0x0f, b'\x01\x00')
sleep(2)
print("ABO MOTOR B")
dev.writeCharacteristic(0x0e, b'\x0a\x00\x41\x01\x02\x01\x00\x00\x00\x01')

dev.writeCharacteristic(0x0e, b'\x0a\x00\x41\x00\x02\x01\x00\x00\x00\x01')
sleep(1)
dev.writeCharacteristic(0x0e, bytes.fromhex('0c0081011109000a64647f03'))
sleep(0.5)
dev.writeCharacteristic(0x0e, bytes.fromhex('0c0081001109000a64647f03'))
sleep(4)
dev.writeCharacteristic(0x0e, bytes.fromhex('0c0081001109000a64647f03'))
sleep(4)
dev.writeCharacteristic(0x0e, b'\x0a\x00\x41\x00\x02\x01\x00\x00\x00\x01')
try:
    while True:
        sleep(1)
        print('+', end='')
except KeyboardInterrupt:
    stop_flag = True  # Notification Thread auslaufen lassen
    sleep(1)
    print('Main Thread Tschuess!')
finally:
    dev.disconnect()