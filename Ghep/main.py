from PyQt5 import QtWidgets, uic, QtGui, QtCore # uic gọi file gui,
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QAction, QGroupBox, QTableWidget, QTableWidgetItem, QWidget
from PyQt5.QtCore import QTimer, QTime, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QPixmap, QCloseEvent, QColor

import sys,time,random,os,json,pprint,socket    # library in python

import paho.mqtt.client as mqtt # mqtt

import urllib.request # check xem co mang ko
import minimalmodbus    # modbus
import serial       # serial
import serial.tools.list_ports

from datetime import datetime   # date_time

# library programer development
import constant as CONSTANT
import db_handler as DB 

# library programer development
from gateway import Gateway
from Lora import Gateway1

'''                                                                                                                             
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
'''

# Qt designer
App = QtWidgets.QApplication([])


app = uic.loadUi("guis\\main.ui")
# app.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

#end


# MQTT
check = 1

MQTT_HOST = '212.237.29.129'
MQTT_USER = 'nhungdaika'
MQTT_PWD = '12354'
MQTT_TOPIC_SEND = 'send_data'
MQTT_TOPIC_CONTROL = 'controller'
MQTT_TOPIC_STATUS = 'control_status'

# device: R1 R2
# status: 1 0

def chang_status_RL(device, status): # thay đổi trạng thái của ảnh
    if (device == "R1"):
        if (status == 1):
            app.img_1.setPixmap(QtGui.QPixmap("icons\\wplum_on.png"))
        elif (status == 0):
            app.img_1.setPixmap(QtGui.QPixmap("icons\\wplum_off.jpg"))
        else:
            pass
    elif (device == "R2"):
        if (status == 1):
            app.img_2.setPixmap(QtGui.QPixmap("icons\\curtain_on.png"))
        elif (status == 0):
            app.img_2.setPixmap(QtGui.QPixmap("icons\\curtain_off.png"))
        else:
            pass
    else:
        return -1

def ctr_R1_bat():
    GW.control_RL(1, 1) # GateWay(Xanh) điểu khien Relay - GW dinh nghia o dau the
    chang_status_RL("R1", 1)
    if (check_internet() == 1):
        get_status_all()

def ctr_R1_tat():
    GW.control_RL(1, 0)
    chang_status_RL("R1", 0)
    if (check_internet() == 1):
        get_status_all()

def ctr_R2_bat():
    GW.control_RL(2, 1)
    chang_status_RL("R2", 1)
    if (check_internet() == 1):
        get_status_all()
  
def ctr_R2_tat():
    GW.control_RL(2, 0)
    chang_status_RL("R2", 0)
    if (check_internet() == 1):
        get_status_all()
    

def UI_init(): # khởi tạo
    global GW
    app.btn_rl1_bat.clicked.connect(ctr_R1_bat)
    app.btn_rl1_tat.clicked.connect(ctr_R1_tat)
    app.btn_rl2_bat.clicked.connect(ctr_R2_bat)
    app.btn_rl2_tat.clicked.connect(ctr_R2_tat)

    ports = serial.tools.list_ports.comports()
    check_device = ''

    if(len(ports) > 0): # khởi tạo để kết nối với GateWay(Xanh)
        for port in ports:
            # print(port)
            if ("USB-SERIAL CH340" in str(port)):
                check_device = port.device
                break
        if (check_device != ''):
            GW = Gateway(CONSTANT.GW_NAME)   #Define GW kế thừa CONSTANT.GW_NAME
            # QMessageBox.information(
            #     app, "KẾT NỐI THÀNH CÔNG", "CHÀO MỪNG BẠN ĐẾN VỚI VƯỜN CỦA NHUNG ĐẠI KA")
            app.lbl_com.setText("ĐÃ KẾT NỐI " + check_device)
            # GW.control_RL(1, 0)
            # GW.control_RL(2, 0)
        else:
            QMessageBox.critical(app, "LỖI KẾT NỐI",
                                      "KHÔNG ĐÚNG THIẾT BỊ")
            sys.exit()
    else:
        QMessageBox.critical(app, "LỖI KẾT NỐI",
                                  "KHÔNG CÓ COM NÀO ĐƯỢC KẾT NỐI")
        sys.exit()

def Lora_init():
    global GW1, app
    ports = serial.tools.list_ports.comports() # mảng những ports các kết nối vào máy tính nhúng
    check_device = ''

    if(len(ports) > 0):
        for port in ports:
            if ("USB-SERIAL CH340" in str(port) or "USB-to-Serial" in str(port)):
                check_device = port.device
                print(check_device)
                break
        if (check_device != ''):
            GW1 = Gateway1(CONSTANT.GW1_NAME, 9600, 0.2)

            app.lbl_com.setText("ĐÃ KẾT NỐI "+str(check_device))
        else:
            print("Không đúng thiết bị!")
            QMessageBox.critical(app, "LỖI KẾT NỐI COM",
                                      "KHÔNG ĐÚNG THIẾT BỊ!")
            sys.exit() # đóng phần mềm
    else:
        QMessageBox.critical(app, "LỖI KẾT NỐI COM",
                                  "KHÔNG CÓ COM NÀO KẾT NỐI!")
        sys.exit()
    try: # đưa GateWay(đỏ) vào mode nhận
        GW1.open()
        GW1.write_data("AT\r\n")
        print(GW1.read_data())
        GW1.write_data("AT+MODE=TEST\r\n")
        print(GW1.read_data())
        GW1.write_data("AT+TEST=RFCFG,433\r\n")
        print(GW1.read_data())
        GW1.write_data("AT+TEST=RXLRPKT\r\n")
        print(GW1.read_data())
    except:
        QMessageBox.critical(app, "LỖI KẾT NỐI COM",
                                  "KHÔNG THỂ KẾT NỐI")

def showTime():
    if (datetime.now().hour < 10):
        h = '0' + str(datetime.now().hour)
    else:
        h = str(datetime.now().hour)
    if (datetime.now().minute < 10):
        m = '0' + str(datetime.now().minute)
    else:
        m = str(datetime.now().minute)
    if (datetime.now().second < 10):
        s = '0' + str(datetime.now().second)
    else:
        s = str(datetime.now().second)
    Str = h + ':' + m + ':' + s
    if (Str == "00:00:00" and datetime.now().day == 1):
        DB.Delete_all_tb()
        
    app.lcdNumber.display(Str)

def status_data():
    global client
    try:
        data = {
            'id': 'G00',
            'RL1_status': "0"+str(GW.get_status_RL(1)),
            'RL2_status': "1"+str(GW.get_status_RL(2))
        }
        if (check_internet() == True):
            client.publish(MQTT_TOPIC_STATUS,
                           json.dumps(data))
    except:
        logErorr("0x03")
    
def check_internet():
    try:
        urllib.request.urlopen('http://google.com')  # Python 3.x-
        return True
    except:
        return False

def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC_CONTROL)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    # print("Data nhan duoc: ", data)
    # print(data['relay_1'])
    if ("relay_1" in data):
        # print("Máy 1")
        if (data['relay_1']['value'] == '1'):
            ctr_R1_bat()
        if (data['relay_1']['value'] == '0'):
            ctr_R1_tat()
    if ("relay_2" in data):
        # print("Máy 2")
        if (data['relay_2']['value'] == '1'):
            ctr_R2_bat()
        if (data['relay_2']['value'] == '0'):
            ctr_R2_tat()
    

def closeEvent(event: QCloseEvent):
    QMessageBox.critical(app, "LỖI NGUY HIỂM","KHÔNG NÊN TẮT PHẦN MỀM KHI KHÔNG CẦN THIẾT!!!\nNẾU TẮT PHẦN MỀM SẼ KHÔNG ĐỌC ĐƯỢC DỮ LIỆU CŨNG NHƯ GỬI DỮ LIỆU CHO SERVER!!\nMONG BẠN HÃY CÂN NHẮC!!")

def update_data(payload): # cập dữ liệu cho thanh progressBar
    global app
    app.progressBar_temp.setValue(int(payload['temp_1']['value']))
    app.progressBar_hum_1.setValue(int(payload['hum_1']['value']))
    app.progressBar_hum_2.setValue(
        int(payload['hum_2']['value'].split('.')[0]))
    # app.progressBar_ph.setValue(int(payload['ph1']['value']))
    app.progressBar_soil_1.setValue(int(payload['soil_1']['value']))
    print(int(float(payload['soil_2']['value'])))
    app.progressBar_soil_3.setValue(
        int(float(payload['soil_2']['value'])))
    

def read_data():
    global check, GW1,client,GW,app
    check = 1

    now = datetime.now()
    timestamp = int(datetime.timestamp(now))
    now = datetime.fromtimestamp(timestamp)

    data = GW1.read_data()# đọc dữ liệu từ con đỏ
    try:
        if (len(data) != 0):
            for i in range(0, len(data)):
                data[i] = data[i].decode('utf-8') # giải mãi hex sang string
            Str = data[0] #  Str dòng thứ nhất chứa thống LEN, vv...
            Str1 = data[1] # Str1 chứa giá trị nhận
            now = datetime.now()
            timestamp = int(datetime.timestamp(now))
            now = datetime.fromtimestamp(timestamp)
            payload = {
                'LEN': Str[Str.find('LEN:') + len("LEN:"):Str.find(',', Str.find('LEN:') + len("LEN:"))],
                'RSSI': Str[Str.find('RSSI:') + len("RSSI:"):Str.find(',', Str.find('RSSI:') + len("RSSI:"))],
                'SNR': Str[Str.find("SNR:") + len("SNR:"):len(Str) - 2],
                'DATA': bytes.fromhex(Str1[Str1.find("\"") +
                                        1: Str1.find("\"", 1 + int(Str1.find("\"")))]).decode('utf-8'),
                'TIME': now}
            # print(payload)

            Data = payload['DATA'].split('_')
            if (int(payload['RSSI']) >= -54 and int(payload['RSSI']) <= 0):
                signal = "RẤT TỐT"
            elif (int(payload['RSSI']) >= -69 and int(payload['RSSI']) <= -55):
                signal = "TỐT"
            elif (int(payload['RSSI']) >= -79 and int(payload['RSSI']) <= -70):
                signal = "TRUNG BÌNH"
            elif (int(payload['RSSI']) >= -100 and int(payload['RSSI']) <= -80):
                signal = "YẾU"
            else:
                signal = "YẾU"
            x = float(Data[6])
            z = (x - 2.8)/(3.3-2.8) # phần trăm tin coi 2.8 đến 3.3 là 100%
            payload_1 = { # tạo chuỗi JSON cho a Vững
                'sub_id': "G05",
                "temp_1": { # tên của node
                    "RF_signal": signal,
                    'value': Data[2],
                    'battery': int(z*100)
                },
                "hum_1": {
                    "RF_signal": signal,
                    'value': Data[3],
                    'battery':  int(z*100)
                },
                "hum_2": {
                    "RF_signal": GW.get_RFsignal(3), # lấy RSSI
                    'value': str(GW.get_main_parameter(3)),
                    'battery': GW.get_battery(3)
                },
                "soil_1": {
                    "RF_signal": signal,
                    'value': Data[1],
                    'battery':  int(z*100)
                },
                "soil_2": {
                    "RF_signal": GW.get_RFsignal(2),
                    'value': GW.get_main_parameter(2),
                    'battery': GW.get_battery(2)
                },
                "ph_1": {
                    "RF_signal": signal,
                    'value': Data[5],
                    'battery':  int(z*100)
                },
                "time": int(round(time.time() * 1000)),
            }

            print(payload_1)
            
            if (int(payload_1['soil_1']['value']) < 10):# check nhỏ hơn 10 bật máy bơm + nên sét một khoảng, comment lại để sửa
                ctr_R1_bat()
            else:
                ctr_R1_tat()
            update_data(payload_1)
            # if (int(float(payload_1['soil_2']['value'])) < 10):
            #     # print("Bat may bom")
            #     ctr_R1_bat()
            # else:
            #     # print("Tat may bom")
            #     ctr_R1_tat()
            update_data(payload_1)

            


        if (check_internet() == True): # nếu có mạng gửu chuỗi cho a vững
            client.publish(MQTT_TOPIC_SEND,
                           json.dumps(payload_1))
        else:
            print("Khong co mang")
    except:
        pass       
def get_status_all(): # lấy trạng thái hiện tại của các thiết bị
    global client,GW
    payload_data = {
        'sub_id': "G05",
        "relay_1": {
            "RF_signal": GW.get_RFsignal(1),
            'value': str(GW.get_status_RL(1)),
            'battery': 100
        },
        "relay_2": {
            "RF_signal": GW.get_RFsignal(1),
            'value': str(GW.get_status_RL(2)),
            'battery': 100
        },
    }
    client.publish(MQTT_TOPIC_STATUS, json.dumps(payload_data)) # gửu cho a vững

def requirePort():
    GW_NAME  = input("Lua chon COM cho GateWay Xanh: ")
    GW1_NAME = input("Lua chon COM cho GateWay Do: ")
    
if __name__ == "__main__":

    app.closeEvent = closeEvent # khi close, gọi sự kiện closeEvent
    Lora_init()

    Time = QTimer() # timer của Qt
    Time.timeout.connect(showTime) # Cứ khi đếm nó  nhảy vào showTime để thực hiện

    read = QTimer()
    UI_init()
    read.timeout.connect(read_data)
    
    read.start(CONSTANT.TIME_OUT) 
    Time.start(1000)
    # khi mình khởi động tắt tất cả thiết bị và cập nhập trạng thái off trên app
    GW.control_RL(1, 0)
    chang_status_RL("R1", 0)
    GW.control_RL(2, 0)
    chang_status_RL("R2", 0)

    # if (check_internet() == True): # kiểm tra internet nếu có gửu cho a vững
    #     client = mqtt.Client()
    #     client.username_pw_set(MQTT_USER,MQTT_PWD)
    #     client.connect(MQTT_HOST, 1883)
    #     client.on_connect = on_connect
    #     client.on_message = on_message
    #     client.loop_start()
    #     get_status_all()
    # else:
    #     print("Khong co mang")

    app.show()
    sys.exit(App.exec())
