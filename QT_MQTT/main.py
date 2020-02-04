from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
import time
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QAction, QGroupBox, QTableWidget, QTableWidgetItem, QWidget
from PyQt5.QtCore import QTimer, QTime, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QPixmap, QCloseEvent, QColor
import random
from playsound import playsound
import os
import paho.mqtt.client as mqtt
import json
from datetime import datetime


App = QtWidgets.QApplication([])


log = uic.loadUi("guis\\main_1.ui")


if __name__ == "__main__":

    log.show()
    sys.exit(App.exec())
