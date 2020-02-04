from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
import time
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QAction, QGroupBox, QTableWidget, QTableWidgetItem, QWidget
from PyQt5.QtCore import QTimer, QTime, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QPixmap, QCloseEvent, QColor
import random
import os
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import pprint
import urllib.request
import socket



import constant as CONSTANT


import db_handler as DB 
App = QtWidgets.QApplication([])


app = uic.loadUi("guis\\main.ui")
# app.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)


MQTT_HOST = '212.237.29.129'
MQTT_USER = 'nhungdaika'
MQTT_PWD = '12354'
MQTT_TOPIC_SEND = 'send_data'
MQTT_TOPIC_CONTROL = 'control'
MQTT_TOPIC_STATUS = 'control_status'

# device: R1 R2
# status: 1 0


def chang_status_RL(device, status):
    if (device == "R1"):
        if (status == 1):
            app.img_1.setPixmap(QtGui.QPixmap("icons\\RL1_on.png"))
        elif (status == 0):
            app.img_1.setPixmap(QtGui.QPixmap("icons\\light_off.png"))
        else:
            pass
    elif (device == "R2"):
        if (status == 1):
            app.img_2.setPixmap(QtGui.QPixmap("icons\\fan_on.png"))
        elif (status == 0):
            app.img_2.setPixmap(QtGui.QPixmap("icons\\fan_off.png"))
        else:
            pass
    else:
        return -1







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


def load_data():
    try:
        payload_data = {
            'sub_id': "G00",
            'sensor_1': {
                'id': str(random.randint(0,100)),
                'name': CONSTANT.STATUS_NODE[str(random.randint(1,12))],
                "RF_signal": CONSTANT.RSSI[str(random.randint(1,4))]
            },
            "sensor_2": {
                "RF_signal": CONSTANT.RSSI[str(random.randint(1,4))],
                "id": str(random.randint(0,100)),
                'name': CONSTANT.STATUS_NODE[str(random.randint(1,12))],
                'EOC': random.randint(0,100),
                'value': random.randint(0,100),
                'battery': random.randint(0,100)
            },
            "sensor_3": {
                "RF_signal": CONSTANT.RSSI[str(random.randint(1,4))],
                "id": str(random.randint(0,100)),
                'name': CONSTANT.STATUS_NODE[str(random.randint(1,12))],
                'EOC': random.randint(0,100),
                'value': random.randint(0,100),
                'battery': random.randint(0,100)
            },
            "time": int(round(time.time() * 1000)),
        }
      
        app.lbl_1_name.setText(payload_data['sensor_1']['name'])
        app.lbl_1_id.setText('ID: ' + payload_data['sensor_1']['id'])
        app.lbl_1_rf.setText('TÍN HIỆU ' + payload_data['sensor_1']['RF_signal'])

        app.lbl_2_name.setText(payload_data['sensor_2']['name'])
        app.lbl_2_id.setText('ID: ' + payload_data['sensor_2']['id'])
        app.lbl_2_rf.setText('TÍN HIỆU ' + payload_data['sensor_2']['RF_signal'])

        app.progressBar_2_pin.setValue(payload_data['sensor_2']['battery'])
        app.progressBar_2_soil.setValue(payload_data['sensor_2']['value'])
        app.progressBar_2_eoc.setValue(payload_data['sensor_2']['EOC'])

        # handler sensor 3
        app.lbl_3_name.setText(payload_data['sensor_3']['name'])
        app.lbl_3_id.setText('ID: ' + payload_data['sensor_3']['id'])
        app.lbl_3_rf.setText('TÍN HIỆU ' + payload_data['sensor_3']['RF_signal'])

        app.progressBar_3_pin.setValue(payload_data['sensor_3']['battery'])
        app.progressBar_3_hum.setValue(payload_data['sensor_3']['value'])
        app.progressBar_3_eoc.setValue(payload_data['sensor_3']['EOC'])

        if (check_internet()):
            app.lbl_internet.setStyleSheet(
                "QLabel {color: green; border-radius: 9px;border: 2px solid}")
            app.lbl_C.setStyleSheet(
                "QLabel {border-radius: 25px;border: 2px solid red;background-color: rgb(0, 255, 0)}")
            app.lbl_internet.setText("KẾT NỐI INTERNET")
            client.publish(MQTT_TOPIC_SEND,
                        json.dumps(payload_data))
        else:
            try:
                DB.insert_data(payload_data['sensor_2']['name'], payload_data['sensor_2']
                            ['id'], payload_data['sensor_2']['RF_signal'], payload_data['sensor_2']['battery'], payload_data['sensor_2']['value'], payload_data['sensor_2']['EOC'])

                DB.insert_data(payload_data['sensor_3']['name'], payload_data['sensor_3']
                            ['id'], payload_data['sensor_3']['RF_signal'], payload_data['sensor_3']['battery'], payload_data['sensor_3']['value'], payload_data['sensor_3']['EOC'])
            except:
                logErorr("0x02")

            app.lbl_internet.setStyleSheet(
                "QLable {color: red; border-radius: 9px;border: 2px solid}")
            app.lbl_C.setStyleSheet(
                "QLabel {border-radius: 25px;border: 2px solid green;background-color: rgb(255, 0, 0)}")
            app.lbl_internet.setText("KHÔNG CÓ INTERNET")
    except:
        logErorr("0x01")
        app.lbl_com.setText("MẤT KẾT NỐI")
        app.lbl_C_2.setStyleSheet(
            "QLabel {border-radius: 25px;border: 2px solid green;background-color: rgb(255, 0, 0)}")
        QMessageBox.critical(app, "LỖI CỰC KỲ NGUY HIỂM",
                             "MẤT KẾT NỐI VỚI THIẾT BỊ")
        sys.exit()
    

def status_data():
    global client
    try:
        data = {
            'id': 'G00',
            'RL1_status': "0"+str(random.randint(0,1)),
            'RL2_status': "1"+str(random.randint(0,1))
        }
        if (check_internet() == True):
            client.publish(MQTT_TOPIC_STATUS,
                           json.dumps(data))
    except:
        logErorr("0x03")
    

def check_internet():
    try:
        urllib.request.urlopen('http://google.com')  # Python 3.x
        return True
    except:
        return False


def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC_CONTROL)




def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    # print(data)
    if(data['status'][0] == '0'):
        if (data['status'][1] == '1'):
            ctr_R1_bat()
        else:
            ctr_R1_tat()
    if(data['status'][0] == '1'):
        if (data['status'][1] == '1'):
            ctr_R2_bat()
        else:
            ctr_R2_tat()


def logErorr(code):
    file = open("logs\\error_code.txt", "a")
    file.write(code + ': '+str(datetime.now().hour) +':'+
            str(datetime.now().minute)+':'+str(datetime.now().second)+'\n')
    file.close()


def closeEvent(event: QCloseEvent):
    QMessageBox.critical(app, "LỖI NGUY HIỂM","KHÔNG NÊN TẮT PHẦN MỀM KHI KHÔNG CẦN THIẾT!!!\nNẾU TẮT PHẦN MỀM SẼ KHÔNG ĐỌC ĐƯỢC DỮ LIỆU CŨNG NHƯ GỬI DỮ LIỆU CHO SERVER!!\nMONG BẠN HÃY CÂN NHẮC!!")

if __name__ == "__main__":

    app.closeEvent = closeEvent

    Time = QTimer()
    Time.timeout.connect(showTime)

    Load_Data = QTimer()
    Load_Data.timeout.connect(load_data)

    Control = QTimer()
    Control.timeout.connect(status_data)

    
    Time.start(1000)
    
    Control.start(1000)
    Load_Data.start(CONSTANT.TIME_OUT)

    try:
        payload_data = {
            'sub_id': "G00",
            'sensor_1': {
                'id': str(random.randint(0,100)),
                'name': CONSTANT.STATUS_NODE[str(random.randint(1,12))],
                "RF_signal": CONSTANT.RSSI[str(random.randint(1,4))]
            },
            "sensor_2": {
                "RF_signal": CONSTANT.RSSI[str(random.randint(1,4))],
                "id": str(random.randint(0,100)),
                'name': CONSTANT.STATUS_NODE[str(random.randint(1,12))],
                'EOC': random.randint(0,100),
                'value': random.randint(0,100),
                'battery': random.randint(0,100)
            },
            "sensor_3": {
                "RF_signal": CONSTANT.RSSI[str(random.randint(1,4))],
                "id": str(random.randint(0,100)),
                'name': CONSTANT.STATUS_NODE[str(random.randint(1,12))],
                'EOC': random.randint(0,100),
                'value': random.randint(0,100),
                'battery': random.randint(0,100)
            },
            "time": int(round(time.time() * 1000)),
        }
        print(payload_data)
        # chang_status_RL("R1", GW.get_status_RL(1))
        # chang_status_RL("R2", GW.get_status_RL(2))

        app.lbl_1_name.setText(payload_data['sensor_1']['name'])
        app.lbl_1_id.setText('ID: ' + payload_data['sensor_1']['id'])
        app.lbl_1_rf.setText(
            'TÍN HIỆU ' + payload_data['sensor_1']['RF_signal'])

        app.lbl_2_name.setText(payload_data['sensor_2']['name'])
        app.lbl_2_id.setText('ID: ' + payload_data['sensor_2']['id'])
        app.lbl_2_rf.setText(
            'TÍN HIỆU ' + payload_data['sensor_2']['RF_signal'])

        app.progressBar_2_pin.setValue(payload_data['sensor_2']['battery'])
        app.progressBar_2_soil.setValue(payload_data['sensor_2']['value'])
        app.progressBar_2_eoc.setValue(payload_data['sensor_2']['EOC'])

        # handler sensor 3
        app.lbl_3_name.setText(payload_data['sensor_3']['name'])
        app.lbl_3_id.setText('ID: ' + payload_data['sensor_3']['id'])
        app.lbl_3_rf.setText('TÍN HIỆU ' + payload_data['sensor_3']['RF_signal'])

        app.progressBar_3_pin.setValue(payload_data['sensor_3']['battery'])
        app.progressBar_3_hum.setValue(payload_data['sensor_3']['value'])
        app.progressBar_3_eoc.setValue(payload_data['sensor_3']['EOC'])
    except:
        app.lbl_com.setText("MẤT KẾT NỐI")
        app.lbl_C_2.setStyleSheet(
            "QLabel {border-radius: 25px;border: 2px solid green;background-color: rgb(255, 0, 0)}")
        QMessageBox.critical(app, "LỖI CỰC KỲ NGUY HIỂM",
                             "MẤT KẾT NỐI VỚI THIẾT BỊ")
        sys.exit()
    

    if (check_internet()):
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER,MQTT_PWD)
        client.connect(MQTT_HOST, 1883)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_start()
        
        # data = {
        #     'id': 'G00',
        #     'status': '0'+str(GW.get_status_RL(1))
        # }
        # client.publish(MQTT_TOPIC_STATUS,
        #            json.dumps(data))
        # data = {
        #     'id': 'G00',
        #     'status': '1'+str(GW.get_status_RL(2))
        # }

        # client.publish(MQTT_TOPIC_STATUS,
        #                json.dumps(data))

        # client.publish(MQTT_TOPIC_SEND,
        #                json.dumps(payload_data))
        app.lbl_C.setStyleSheet(
            "QLabel {border-radius: 25px;border: 2px solid red;background-color: rgb(0, 255, 0)}")
        app.lbl_internet.setText("KẾT NỐI INTERNET")
        app.lbl_internet.setStyleSheet("QLabel {color: green; border-radius: 9px;border: 2px solid}")
        app.lbl_C_2.setStyleSheet(
            "QLabel {border-radius: 25px;border: 2px solid red;background-color: rgb(0, 255, 0)}")
        
    else:
        try:
            DB.insert_data(payload_data['sensor_2']['name'], payload_data['sensor_2']
                           ['id'], payload_data['sensor_2']['RF_signal'], payload_data['sensor_2']['battery'], payload_data['sensor_2']['value'], payload_data['sensor_2']['EOC'])

            DB.insert_data(payload_data['sensor_3']['name'], payload_data['sensor_3']
                                   ['id'], payload_data['sensor_3']['RF_signal'], payload_data['sensor_3']['battery'], payload_data['sensor_3']['value'], payload_data['sensor_3']['EOC'])
        except:
            logErorr("0x01")

        app.lbl_C.setStyleSheet(
            "QLabel {border-radius: 25px;border: 2px solid green;background-color: rgb(255, 0, 0)}")
        app.lbl_internet.setText("KHÔNG CÓ INTERNET")
        app.lbl_internet.setStyleSheet("QLabel {color:red;border-radius:9px;border: 2px solid}")
    
    app.show()
    sys.exit(App.exec())
