''' docstring '''
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
#import random
import socket
import time

#from PyQt5.QtCore import pyqtSignal, QObject
#from PyQt5 import QtWidgets
#from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import *

from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QPushButton, QAction, QFileDialog, QApplication, QSizePolicy,
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QComboBox, QDesktopWidget)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname()  # get local machine name
TCP_PORT = 9999  # set port
BUFFER_SIZE = 1024  # set 1024 bytes as buffer
ORIGINAL_DATASET = 'dataset_original.txt'
REDUCED_DATASET = 'dataset_reduced.txt'


class Window(QMainWindow):
    ''' docstring '''

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        #self.com = Communicate()
        # self.com.closeApp.connect(self.close)
        self.connStatus = False

        self.custimWid = MainWidget(self)
        self.custimWid.controlWid.connectButton.clicked.connect(
            self.connectServer)
        self.custimWid.controlWid.openButton.clicked.connect(self.openFile)
        self.custimWid.controlWid.closeButton.clicked.connect(self.closeApp)
        # self.custimWid.controlWid.closeButton.clicked.connect(QApplication.instance().quit)
        # self.custimWid.controlWid.closeButton.clicked.connect(QApplication.instance().quit)

        self.setCentralWidget(self.custimWid)
        self.statusBar()
        self.statusBar().showMessage('Ready')
        #self.setGeometry(300, 300, 1280, 720)
        self.resize(1280, 720)
        self.center()
        self.setWindowTitle('Trajectory Mapping - Client App')
        self.show()

    def center(self):
        ''' docstring '''

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def connectServer(self):
        ''' docstring '''
        # create a socket object
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connection to hostname on the port.
        self.sckt.connect((TCP_HOST, TCP_PORT))
        self.connStatus = True

        # send message to server
        msgToSend = 'Houssem'
        self.sckt.send(msgToSend.encode('ascii'))

        # Receive no more than BUFFER_SIZE bytes
        msg = self.sckt.recv(BUFFER_SIZE)

        # print received reply
        print(msg.decode('ascii'))
        self.statusBar().showMessage(msg.decode('ascii'))

    def openFile(self):
        ''' docstring '''
        if self.connStatus:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

            if fname[0]:
                f = open(fname[0], 'rb')
                with f:
                    data_buffer = f.read(BUFFER_SIZE)
                    while (data_buffer):
                        self.sckt.send(data_buffer)
                        data_buffer = f.read(BUFFER_SIZE)
                print('File opened and sent toserver')
                self.statusBar().showMessage('File opened and sent to server')
                self.receiveFiles()
        else:
            self.statusBar().showMessage('First connect to server')

    def closeApp(self):
        ''' docstring '''
        if self.connStatus:
            self.sckt.close()
        QApplication.instance().quit()

    def receiveFiles(self):
        ''' docstring'''
        time.sleep(5)
        self.statusBar().showMessage('Files received from server')


class MainWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.controlWid = ControlWidget(self)
        self.canvasWid = CanvasWidget(self)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.controlWid, 1, 0)
        grid.addWidget(self.canvasWid, 1, 1, 1, 7)
        self.setLayout(grid)


class ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        ''' docstring '''
        super(ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.connectButton = QPushButton("Connect to Server")
        self.openButton = QPushButton("Open File")
        self.plotButton = QPushButton("Plot Trajectory")
        self.queryButton = QPushButton("Query")
        self.closeButton = QPushButton("Close")

        self.comboBox = QComboBox(self)
        self.comboBox.setToolTip(
            "Choose between the full dataset, or the reduced one")
        self.comboBox.addItem("Full Dataset")
        self.comboBox.addItem("Reduced Dataset")

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.connectButton)
        self.vbox.addWidget(self.openButton)
        self.vbox.addWidget(self.comboBox)
        self.vbox.addWidget(self.plotButton)
        self.vbox.addWidget(self.queryButton)
        self.vbox.addWidget(self.closeButton)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)


class CanvasWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(CanvasWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.canvas)

        self.setLayout(self.vbox)


class Networking():
    ''' doc string '''


if __name__ == '__main__':

    APP = QApplication(sys.argv)
    ex = Window()
    sys.exit(APP.exec_())
