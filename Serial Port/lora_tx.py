import serial
import serial.tools.list_ports
import time
import sys
import random
from datetime import datetime
import json


class Serial_class():
    def __init__(self, port_name, baudrate, timeout):
        self.Ser = serial.Serial()
        self.Ser.port = port_name
        self.Ser.baudrate = baudrate
        self.Ser.timeout = timeout
        if(self.Ser.isOpen() == False):
            self.Ser.open()

    def send_Data(self, Data):
        self.Ser.write(Data.encode('utf-8'))

    def read_Data(self):
        val = ''
        veri = self.Ser.readlines()
        for i in range(0, len(veri)):
            val += str(veri[i].decode('utf-8'))
        return val


if __name__ == "__main__":
    print("[LORA][SERIAL]: ")

    Ports = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        Ports.append(port.device)
    print(Ports)

    Serial = Serial_class(Ports[0], 9600, 0.1)

    Serial.send_Data('AT\r\n')
    print(Serial.read_Data())
    Serial.send_Data('AT+MODE=TEST\r\n')
    print(Serial.read_Data())
    Serial.send_Data('AT+TEST=RFCFG,433\r\n')
    print(Serial.read_Data())
    try:
        while True:
            data = "G05_" + str(random.randint(0, 100)) + "_" + str(random.randint(
                0, 100)) + "_" + str(random.randint(0, 100)) + "_" + str(random.randint(0, 100))
            TX = "AT+TEST = TXLRSTR," + str(data) + "\r\n"
            print(TX)
            Serial.send_Data(TX)
            print(Serial.read_Data())
            time.sleep(2)
    except KeyboardInterrupt:
        print("Bye Bye!!!")
        sys.exit()
