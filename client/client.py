#!/usr/bin/python3
"""
client-app.py
"""

import sys
#import random
import socket
#import time
import os
import mplleaflet

#from PyQt5.QtCore import QUrl
#from PyQt5.QtCore import pyqtSignal, QObject
#from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import *

#from PyQt5.QtWebEngineWidgets import QWebEnginePage
#from PyQt5.QtWebEngineWidgets import QWebEngineView
#from PyQt5.QtWebEngineWidgets import QWebEngineSettings

#from PyQt5.QtWebKitWidgets import QWebPage as QWebEnginePage
#from PyQt5.QtWebKitWidgets import QWebView as QWebEngineView
#from PyQt5.QtWebKit import QWebSettings as QWebEngineSettings

#from PyQt5.QtWebKit import QWebSettings
#from PyQt5.QtWebKitWidgets import QWebPage, QWebView

#from PyQt5.QtWidgets import (QAction, QHBoxLayout, QTextEdit, QSizePolicy )
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QApplication,
    QVBoxLayout, QWidget, QGridLayout, QComboBox, QDesktopWidget, QInputDialog)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname()  # get local machine name
TCP_PORT = 9999  # set port
BUFFER_SIZE = 1024  # set 1024 bytes as buffer
ORIGINAL_DATASET_FILE = 'dataset_original.txt'
REDUCED_DATASET_FILE = 'dataset_reduced.txt'


class Window(QMainWindow):
    ''' docstring '''

    def __init__(self):
        super().__init__()
        self.conn_status = False
        self.sckt = None
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        #self.com = Communicate()
        # self.com.close_app.connect(self.close)

        self.custom_wid = MainWidget(self)
        self.custom_wid.control_wid.connect_btn.clicked.connect(
            self.connect_server)
        self.custom_wid.control_wid.open_btn.clicked.connect(self.open_file)
        self.custom_wid.control_wid.close_btn.clicked.connect(self.close_app)
        # self.custom_wid.control_wid.close_btn.clicked.connect(QApplication.instance().quit)
        # self.custom_wid.control_wid.close_btn.clicked.connect(QApplication.instance().quit)

        self.setCentralWidget(self.custom_wid)
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

    def connect_server(self):
        ''' docstring '''

        new_tcp_host, ok = QInputDialog.getText(self, 'Connect to Server', 
            'Enter server IP address:')
        
        if ok:
            # create a socket object
            self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            print(new_tcp_host)
            self.sckt.connect((new_tcp_host, TCP_PORT))
            self.conn_status = True

            # send message to server
            msg_to_send = 'Houssem'
            self.sckt.send(msg_to_send.encode('utf-8'))

            # Receive no more than BUFFER_SIZE bytes
            msg = self.sckt.recv(BUFFER_SIZE)

            # print received reply
            print(msg.decode('utf-8'))
            self.statusBar().showMessage(msg.decode('utf-8'))

    def open_file(self):
        ''' docstring '''
        if self.conn_status:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

            if fname[0]:
                fsize = os.path.getsize(fname[0])
                self.sckt.send(str(fsize).encode('utf-8'))

                with open(fname[0], 'rb') as f:
                    data_buffer = f.read(BUFFER_SIZE)
                    while data_buffer:
                        self.sckt.send(data_buffer)
                        data_buffer = f.read(BUFFER_SIZE)

                print('File opened and sent to server')
                self.statusBar().showMessage('File opened and sent to server')
                self.receive_files()
        else:
            self.statusBar().showMessage('First connect to server')
        
    def close_app(self):
        ''' docstring '''
        if self.conn_status:
            self.sckt.close()
        QApplication.instance().quit()

    def receive_files(self):
        ''' docstring'''
        #time.sleep(2)
        with open(ORIGINAL_DATASET_FILE, 'wb') as f:
            print('Receiving data ...')
            msg = self.sckt.recv(BUFFER_SIZE)
            fsize = int(msg.decode('utf-8'))
            rsize = 0
            while True:
                data = self.sckt.recv(BUFFER_SIZE)
                #print('Received data = %s', (data))
                rsize = rsize + len(data)
                f.write(data)
                #print(rsize)
                if  rsize >= fsize:
                    print('Breaking from file write')
                    break

        with open(REDUCED_DATASET_FILE, 'wb') as f:
            print('Receiving data ...')
            msg = self.sckt.recv(BUFFER_SIZE)
            fsize = int(msg.decode('utf-8'))
            rsize = 0
            while True:
                data = self.sckt.recv(BUFFER_SIZE)
                #print('Received data = %s', (data))
                rsize = rsize + len(data)
                f.write(data)
                #print(rsize)
                if  rsize >= fsize:
                    print('Breaking from file write')
                    break

        self.statusBar().showMessage('Files received from server')
        self.load_data()

    def load_data(self):
        ''' docstring'''
        lines_buffer = []
        original_dataset = []
        with open(ORIGINAL_DATASET_FILE, 'r') as f:
            lines_buffer = f.readlines()
            #print(lines_buffer)
        for line in lines_buffer:
            tmp = line.split(',')
            tmp[0] = float(tmp[0])
            tmp[1] = float(tmp[1])
            original_dataset.append(tmp)
        #print(original_dataset)

        lines_buffer = []
        reduced_dataset = []
        with open(REDUCED_DATASET_FILE, 'r') as f:
            lines_buffer = f.readlines()
            #print(lines_buffer)
        for line in lines_buffer:
            tmp = line.split(',')
            tmp[0] = float(tmp[0])
            tmp[1] = float(tmp[1])
            reduced_dataset.append(tmp)
        #print(reduced_dataset)

        yx = np.array(original_dataset)
        xy = np.fliplr(yx)
        print(yx)
        print(xy)
        # Plot the path as red dots connected by a blue line
        plt.hold(True)
        plt.plot(xy[:,0], xy[:,1], 'ro')
        plt.plot(xy[:,0], xy[:,1], 'b')

        root, ext = os.path.splitext(__file__)
        mapfile = root  + '.html'
        # Create the map. Save the file to basic_plot.html. _map.html is the default
        # if 'path' is not specified
        mplleaflet.save_html(path=mapfile)
        #self.custom_wid.map_wid.load(QUrl(mapfile))
        #mplleaflet.show(path=mapfile)


class MainWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.control_wid = ControlWidget(self)
        #self.map_wid = QWebEngineView(self)
        self.canvas_wid = CanvasWidget(self)

        grid = QGridLayout()
        grid.setSpacing(10)
        #grid.addWidget(self.control_wid, 1, 0)
        grid.addWidget(self.canvas_wid, 1, 1, 1, 7)
        grid.addWidget(self.map_wid, 1, 1, 1, 7)
        self.setLayout(grid)


class ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        #self.connect_host_label = QLab(self)
        #self.connect_host = QLineEdit(self)
        #self.connect_host.setMaximumWidth(200)
        #self.connect_host.setFixedWidth(100)
        self.connect_btn = QPushButton("Connect to Server")
        self.open_btn = QPushButton("Open File")
        self.plot_btn = QPushButton("Plot Trajectory")
        self.query_btn = QPushButton("Query")
        self.close_btn = QPushButton("Close")

        self.combo_box = QComboBox(self)
        self.combo_box.setToolTip(
            "Choose between full dataset/reduced dataset")
        self.combo_box.addItem("Full Dataset")
        self.combo_box.addItem("Reduced Dataset")

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(1)
        #self.vbox.addWidget(self.connect_host)
        self.vbox.addWidget(self.connect_btn)
        self.vbox.addWidget(self.open_btn)
        self.vbox.addWidget(self.combo_box)
        self.vbox.addWidget(self.plot_btn)
        self.vbox.addWidget(self.query_btn)
        self.vbox.addWidget(self.close_btn)
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

    def __init__(self, parent):
        # TODO
        pass


if __name__ == '__main__':

    APP = QApplication(sys.argv)
    ex = Window()
    sys.exit(APP.exec_())
