from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import time
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QAction, QGroupBox, QTableWidget, QTableWidgetItem, QWidget
from PyQt5.QtCore import QTimer, QTime, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QPixmap, QCloseEvent, QColor
import os
from datetime import datetime
import urllib.request
import socket
import serial
import serial.tools.list_ports
import sys
import numpy as np


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('guis\\main.ui', self)
        self.Time = QTimer()
        self.Time.timeout.connect(self.showTime)
        self.Time.start(1000)

    def showTime(self):
        hour = np.random.randint(100, size=10)
        temperature = np.random.randint(100, size=10)
        self.graphWidget.plot(hour, temperature)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
