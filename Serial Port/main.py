import minimalmodbus
import serial
import serial.tools.list_ports
import constant as CONSTANT
import time
import threading
import paho.mqtt.client as mqtt
import json
import sys
import urllib.request
import socket
import pymongo
from datetime import datetime
import pprint
from colorama import Fore, Back, Style,init





MQTT_HOST = '212.237.29.129'

USER = 'nhungdaika'
PWD = '12354'

ART = '''
  ____  __  __    _    ____ _____   _____ _    ____  __  __ _ _ _
 / ___||  \/  |  / \  |  _ \_   _| |  ___/ \  |  _ \|  \/  | | | |
 \___ \| |\/| | / _ \ | |_) || |   | |_ / _ \ | |_) | |\/| | | | |
  ___) | |  | |/ ___ \|  _ < | |   |  _/ ___ \|  _ <| |  | |_|_|_|
 |____/|_|  |_/_/   \_\_| \_\|_|   |_|/_/   \_\_| \_\_|  |_(_|_|_)
'''

class gateway():
    # init MOSBUS RTU
    def __init__(self, port_name, id_device=1):
        self.instrument = minimalmodbus.Instrument(port_name, id_device)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout = 0.05
        self.instrument.mode = minimalmodbus.MODE_RTU  # seconds
    # convert data to int 16

    def convert_data(self, data):
        value = ''
        for i in range(0, len(data)):
            value += hex(data[i])
        value = value.replace('0x', '')
        value = '0x'+value
        return int(value, 16)
    # get number of node of Wriless

    def get_num_of_node(self):
        data = self.instrument.read_registers(
            registeraddress=272, number_of_registers=2, functioncode=3)
        value = self.convert_data(data)
        return value
    # get id of node
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_node_id(self, option):
        value = ''
        if (option == 1):
            data = self.instrument.read_registers(
                registeraddress=273, number_of_registers=2, functioncode=3)
            value = self.convert_data(data)
            return value
        elif (option == 2):
            data = self.instrument.read_registers(
                registeraddress=275, number_of_registers=2, functioncode=3)
            value = self.convert_data(data)
            return value
        elif (option == 3):
            data = self.instrument.read_registers(
                registeraddress=277, number_of_registers=2, functioncode=3)
            value = self.convert_data(data)
            return value
        else:
            print("Khong co device nay!")
            return - 1
    # read mosbus adr

    def get_modbus_adr(self):
        data = self.instrument.read_registers(
            registeraddress=256, number_of_registers=1, functioncode=3)
        value = self.convert_data(data)
        return value
    # read mosbus baudrate

    def get_modbus_baudrate(self):
        data = self.instrument.read_registers(
            registeraddress=257, number_of_registers=1, functioncode=3)
        value = self.convert_data(data)
        return value
    # read mosbus parity

    def get_modbus_parity(self):
        data = self.instrument.read_registers(
            registeraddress=258, number_of_registers=1, functioncode=3)
        value = self.convert_data(data)
        return value
    # get main parmeter
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_main_parameter(self, option=1):
        if (option == 1):
            data = self.instrument.read_float(
                registeraddress=41217, number_of_registers=2, functioncode=3)
            return data
        elif (option == 2):
            data = self.instrument.read_registers(
                registeraddress=41473, number_of_registers=1, functioncode=3)
            return data[0]/10
        elif (option == 3):
            data = self.instrument.read_float(
                registeraddress=41729, number_of_registers=2, functioncode=3)
            return data
    # get temperater of
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_second_parameter(self, option=1):
        if (option == 1):
            data = self.instrument.read_float(
                registeraddress=41220, number_of_registers=2, functioncode=3)
            return data
        elif (option == 2):
            data = self.instrument.read_float(
                registeraddress=41476, number_of_registers=2, functioncode=3)
            return data
        elif (option == 3):
            data = self.instrument.read_float(
                registeraddress=41732, number_of_registers=2, functioncode=3)
            return data
    # get Batterry
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_battery(self, option=1):
        if (option == 1):
            data = self.instrument.read_register(
                41216)
        elif (option == 2):
            data = self.instrument.read_register(
                41472)
        elif (option == 3):
            data = self.instrument.read_register(
                41728)
        return CONSTANT.BATTERY[str(data)]
    # get Status Node
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_status_node(self, option=1):
        if (option == 1):
            data = self.instrument.read_register(
                41219)
        elif (option == 2):
            data = self.instrument.read_register(
                41475)
        elif (option == 3):
            data = self.instrument.read_register(
                41731)
        return CONSTANT.STATUS_NODE[str(data)]
    # get RF signal
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_RFsignal(self, option=1):
        data = self.instrument.read_registers(
            registeraddress=68, number_of_registers=1, functioncode=3)
        data = hex(data[0]).replace('0x', '')
        hi_byte = data[0]
        lo_byte = data[len(data) - 1]
        if (option % 2 != 0):
            if (option == 1):
                return CONSTANT.RSSI[str(hi_byte)]
            else:
                data = self.instrument.read_registers(
                    registeraddress=69, number_of_registers=1, functioncode=3)
                data = hex(data[0]).replace('0x', '')
                hi_byte = data[0]
                lo_byte = data[len(data) - 1]
                return CONSTANT.RSSI[str(hi_byte)]
        else:
            return CONSTANT.RSSI[str(lo_byte)]
    #  have 2 relay
    # option: 1 or 2
    # 1 is on 0 is off

    def control_RL(self, option, status):
        if (option == 1):
            self.instrument.write_register(registeraddress=2000, value=status,
                                           number_of_decimals=0, functioncode=16, signed=False)
        else:
            self.instrument.write_register(registeraddress=2001, value=status,
                                           number_of_decimals=0, functioncode=16, signed=False)
    # get status of relay
    def get_status_RL(self, option):
        if (option == 1):
            data = self.instrument.read_registers(
                registeraddress=2000, number_of_registers=1, functioncode=3)
        else:
            data = self.instrument.read_registers(
                registeraddress=2001, number_of_registers=1, functioncode=3)
        return data[0]



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+ str(rc))
    client.subscribe("control",0)


def on_message(client, userdata, msg):
    global GW
    data = json.loads(msg.payload.decode('utf-8'))
    # print(Style.BRIGHT + Fore.CYAN + data['status'])
    if (data['status'][0] == '0'):
        if(data['status'][1]=='1'):
            GW.control_RL(1, 1)
        else:
            GW.control_RL(1, 0)
    elif(data['status'][0] == '1'):
        if(data['status'][1] == '1'):
            GW.control_RL(2, 1)
        else:
            GW.control_RL(2, 0)
    else:
        print("KHÔNG CÓ ĐÈN")


def check_internet():
    try:
        urllib.request.urlopen('http://google.com')  # Python 3.x
        return True
    except:
        return False

if __name__ == "__main__":
    # log.show()
    init()
    print(Fore.GREEN + '[SMART_FARM]')
    print(Style.BRIGHT + ART)
    print(Fore.RESET + '')
    print(Style.NORMAL + '')
    # print(ART)
    ports = serial.tools.list_ports.comports()
    check_device = ''

    if(len(ports)>0):
        for port in ports:
            if ("USB-SERIAL CH340" in str(port)):
                check_device = port.device
                print(check_device)
                break
        if (check_device != ''):
            GW = gateway(check_device)
        else:
            print(Style.BRIGHT + Fore.YELLOW+"Không đúng thiết bị!")
            sys.exit()
    else:
        print(Style.BRIGHT + Fore.YELLOW+"Không có kết nối COM nào!!!")
        sys.exit()

    myMG = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myMG["SMART_FARM_DB"]

    if (check_internet() == True):
        client = mqtt.Client()
        client.username_pw_set(USER,PWD)
        client.connect(MQTT_HOST, 1883)
        IPaddress = socket.gethostbyname(socket.gethostname())
        print(IPaddress)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_start()
    else:
        print("Vui lòng kiểm tra kết nối Internet")
        sys.exit()

    try:
        while True:
            data_payload = {
                "GW_name": "G00",
                "sensor_1": {
                    "id":  GW.get_node_id(1),
                    "name": GW.get_status_node(1),
                    "RF_signal": GW.get_RFsignal(1),
                    "relay_status1": GW.get_status_RL(1),
                    "realy_status2": GW.get_status_RL(2)
                },
                "sensor_2": {
                    "id": GW.get_node_id(2),
                    "name": GW.get_status_node(2),
                    "value": GW.get_main_parameter(2),
                    "temp_of_EC": GW.get_second_parameter(2),
                    "RF_signal":  GW.get_RFsignal(2),
                    "battery":  GW.get_battery(2)
                },
                "sensor_3": {
                    "id": GW.get_node_id(3),
                    "name": GW.get_status_node(3),
                    "value": GW.get_main_parameter(3),
                    "temp_of_EC": GW.get_second_parameter(3),
                    "RF_signal": GW.get_RFsignal(3),
                    "battery": GW.get_battery(3)
                },
                "time": int(round(time.time()* 1000)),
                "status": "LỖI CỰC KỲ NGUY HIỂM!!!! HÃY TRÁNH XA THIẾT BỊ"

            }
            print(Fore.BLUE+Style.BRIGHT+'data_send: ')
            pprint.pprint(data_payload)
            if(check_internet()==True):
                table_name = "data_of_"+str(datetime.now().day) + "_" + \
                    str(datetime.now().month) + "_" + str(datetime.now().year)
                mycol_successfully = mydb[str(table_name)]
                client.publish('send_data', json.dumps(data_payload))
                mycol_successfully.insert_one(data_payload)
            else:
                print(Style.BRIGHT + Fore.WHITE+"Không có internet, Không thể gửi dữ liệu cho SERVER")
                table_name = "data_err_of_"+str(datetime.now().day) + "_" + \
                    str(datetime.now().month) + "_" + str(datetime.now().year)
                mycol_error = mydb[str(table_name)]
                mycol_error.insert_one(data_payload)
            time.sleep(5)
    except:
        # pass
        print(Style.BRIGHT + Fore.RED + "LỖI CỰC KỲ NGUY HIỂM!!!! HÃY TRÁNH XA THIẾT BỊ")
    sys.exit()
    client.loop_stop()
