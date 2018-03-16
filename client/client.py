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


#from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import *

#from PyQt5.QtWebKitWidgets import QWebPage as QWebEnginePage
#from PyQt5.QtWebKitWidgets import QWebView as QWebEngineView
#from PyQt5.QtWebKit import QWebSettings as QWebEngineSettings

#from PyQt5.QtWebKit import QWebSettings
#from PyQt5.QtWebKitWidgets import QWebPage, QWebView

#from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtCore import (QUrl, QFileInfo, QElapsedTimer)
from PyQt5.QtWebEngineWidgets import (QWebEnginePage, QWebEngineView, QWebEngineSettings)
#from PyQt5.QtWidgets import (QAction, QHBoxLayout, QTextEdit, QSizePolicy )
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QApplication, QLabel,
    QVBoxLayout, QWidget, QGridLayout, QComboBox, QDesktopWidget, QInputDialog, QLineEdit)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname()  # get local machine name
TCP_HOST_IP = socket.gethostbyname(TCP_HOST)
TCP_PORT = 9999  # set port
BUFFER_SIZE = 1024  # set 1024 bytes as buffer
ORIGINAL_DATASET_FILE = 'dataset_original.txt'
REDUCED_DATASET_FILE = 'dataset_reduced.txt'
QUERY_ORIGINAL_DATASET_FILE = 'dataset_original_query.txt'
QUERY_REDUCED_DATASET_FILE = 'dataset_reduced_query.txt'


class Window(QMainWindow):
    ''' docstring '''

    def __init__(self):
        super().__init__()
        self.conn_status = False
        self.query_status = False
        self.sckt = None
        self.new_tcp_host = TCP_HOST_IP
        self.init_ui()
        self.q_p1_x = 116.3
        self.q_p1_y = 39.9
        self.q_p2_x = 116.32
        self.q_p2_y = 40
        self.query_elapsed = None
        self.proc_elapsed = 0
        self.timer = QElapsedTimer()

    def init_ui(self):
        ''' docstring '''

        #self.com = Communicate()
        # self.com.close_app.connect(self.close)

        self.custom_wid = MainWidget(self)
        self.custom_wid.control_wid.connect_btn.clicked.connect(
            self.connect_server)
        self.custom_wid.control_wid.open_btn.clicked.connect(self.open_file)
        self.custom_wid.control_wid.close_btn.clicked.connect(self.close_app)
        self.custom_wid.control_wid.plot_btn.clicked.connect(self.load_data)
        self.custom_wid.control_wid.query_btn.clicked.connect(self.query_region)
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

        self.new_tcp_host, ok = QInputDialog.getText(self, 'Connect to Server', 
            'Enter server IP address:',QLineEdit.Normal,str(self.new_tcp_host))
        
        if ok:
            # create a socket object
            self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            print(self.new_tcp_host)
            self.sckt.connect((self.new_tcp_host, TCP_PORT))
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
        self.timer.restart()
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

        self.proc_elapsed = self.timer.nsecsElapsed()
        print(self.timer.clockType())
        print(self.proc_elapsed)
        self.custom_wid.control_wid.label_7.setText("Processing time: {}".format(self.proc_elapsed))

    def load_data(self):
        ''' docstring'''
        full_ds = 0
        reduced_ds = 0
        reduction_rate = 0
        query_full_ratio = 0
        query_reduced_ratio = 0

        lines_buffer = []
        original_dataset = []
        with open(ORIGINAL_DATASET_FILE, 'r') as f:
            lines_buffer = f.readlines()
            full_ds = len(lines_buffer)
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
            reduced_ds = len(lines_buffer)
            #print(lines_buffer)
        for line in lines_buffer:
            tmp = line.split(',')
            tmp[0] = float(tmp[0])
            tmp[1] = float(tmp[1])
            reduced_dataset.append(tmp)
        #print(reduced_dataset)

        reduction_rate = 100 * reduced_ds/full_ds
        self.custom_wid.control_wid.label_1.setText("Full dataset: {}".format(full_ds))
        self.custom_wid.control_wid.label_2.setText("Reduced dataset: {}".format(reduced_ds))
        self.custom_wid.control_wid.label_3.setText("Reduction rate: {} %".format(round(reduction_rate,2)))

        query_original_dataset = []
        query_reduced_dataset = []

        if self.query_status:
            lines_buffer = []
            with open(QUERY_ORIGINAL_DATASET_FILE, 'r') as f:
                lines_buffer = f.readlines()
                query_full_ratio = 100 * len(lines_buffer)/full_ds
                #print(lines_buffer)
            for line in lines_buffer:
                tmp = line.split(',')
                tmp[0] = float(tmp[0])
                tmp[1] = float(tmp[1])
                query_original_dataset.append(tmp)

            lines_buffer = []
            with open(QUERY_REDUCED_DATASET_FILE, 'r') as f:
                lines_buffer = f.readlines()
                query_reduced_ratio = 100 * len(lines_buffer)/reduced_ds
                #print(lines_buffer)
            for line in lines_buffer:
                tmp = line.split(',')
                tmp[0] = float(tmp[0])
                tmp[1] = float(tmp[1])
                query_reduced_dataset.append(tmp)

        self.custom_wid.control_wid.label_4.setText("Results ratio to full dataset: {} %".format(round(query_full_ratio)))
        self.custom_wid.control_wid.label_5.setText("Results ratio to reduced dataset: {} %".format(round(query_reduced_ratio)))
        
        xy = np.array(reduced_dataset)
        q_xy = np.array([])
        #print(self.custom_wid.control_wid.combo_box.currentIndex())
        #print(self.custom_wid.control_wid.combo_box.currentData())
        #print(self.custom_wid.control_wid.combo_box.currentText())
        tmp = self.custom_wid.control_wid.combo_box.currentText()
        if tmp == "Full Dataset":
            xy = np.array(original_dataset)
            q_xy = np.array(query_original_dataset)
        elif tmp == "Reduced Dataset":
            xy = np.array(reduced_dataset)
            q_xy = np.array(query_reduced_dataset)
        #xy = np.fliplr(yx)
        #print(yx)
        #print(xy)
        # Plot the path as red dots connected by a blue line
        plt.hold(True)
        if self.query_status:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            rect = mpatches.Rectangle([min(self.q_p1_x,self.q_p2_x),min(self.q_p1_y,self.q_p2_y)], abs(self.q_p1_x - self.q_p2_x), abs(self.q_p1_y - self.q_p2_y))
            ax.add_patch(rect)
            #plt.plot()
        plt.plot(xy[:,0], xy[:,1], 'ko')
        if self.query_status:
            plt.plot(q_xy[:,0], q_xy[:,1], 'rD')
        plt.plot(xy[:,0], xy[:,1], 'b')

        root, ext = os.path.splitext(__file__)
        mapfile = root  + '.html'
        print("mapfile: {}".format(mapfile))
        # Create the map. Save the file to basic_plot.html. _map.html is the default
        # if 'path' is not specified
        mplleaflet.show(inbrowser=False,path=mapfile)
        #mplleaflet.save_html(mapfile)
        #self.custom_wid.map_wid.load(QUrl(mapfile))
        #self.custom_wid.map_wid.setUrl(QUrl("http://www.google.com/"))
        #print(QUrl(mapfile))
        #self.custom_wid.map_wid.setUrl(QUrl(mapfile))
        self.custom_wid.map_wid.setUrl(QUrl.fromLocalFile(QFileInfo(mapfile).absoluteFilePath()))
        #mplleaflet.show(path=mapfile)
    def query_region(self):
        ''' docstring '''
        self.timer.restart()
        print('Sending query ...')
        msg_to_send = '{},{},{},{}'.format(self.q_p1_x,self.q_p1_y,self.q_p2_x,self.q_p2_y)
        self.sckt.send(msg_to_send.encode('utf-8'))
        print('Query sent ...')

        with open(QUERY_ORIGINAL_DATASET_FILE, 'wb') as f:
            print('Receiving query data ...')
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
                    print('Breaking from query file write')
                    break

        with open(QUERY_REDUCED_DATASET_FILE, 'wb') as f:
            print('Receiving query data ...')
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
                    print('Breaking from query file write')
                    break

        self.query_status = True
        self.query_elapsed = self.timer.nsecsElapsed()
        print(self.timer.clockType())
        print(self.query_elapsed)
        self.custom_wid.control_wid.label_6.setText("Query time: {}".format(self.query_elapsed))



class MainWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.control_wid = ControlWidget(self)
        self.map_wid = QWebEngineView(self)        
        #self.canvas_wid = CanvasWidget(self)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.control_wid, 1, 0)
        #grid.addWidget(self.canvas_wid, 1, 1, 1, 7)
        grid.addWidget(self.map_wid, 1, 1, 1, 7)
        self.setLayout(grid)


class ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.connect_btn = QPushButton("Connect to Server")
        self.open_btn = QPushButton("Open File")
        self.plot_btn = QPushButton("Plot Trajectory")
        self.select_btn = QPushButton("Select Region")
        self.query_btn = QPushButton("Query")
        self.close_btn = QPushButton("Close")

        self.combo_box = QComboBox(self)
        self.combo_box.setToolTip(
            "Choose between Full or Reduced dataset")
        self.combo_box.addItem("Full Dataset")
        self.combo_box.addItem("Reduced Dataset")

        self.label_1 = QLabel(self)
        self.label_2 = QLabel(self)
        self.label_3 = QLabel(self)
        self.label_4 = QLabel(self)
        self.label_5 = QLabel(self)
        self.label_6 = QLabel(self)
        self.label_7 = QLabel(self)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.connect_btn)
        self.vbox.addWidget(self.open_btn)
        self.vbox.addWidget(self.combo_box)
        self.vbox.addWidget(self.plot_btn)
        self.vbox.addWidget(self.select_btn)
        self.vbox.addWidget(self.query_btn)
        self.vbox.addWidget(self.close_btn)
        self.vbox.addWidget(self.label_1)
        self.vbox.addWidget(self.label_2)
        self.vbox.addWidget(self.label_3)
        self.vbox.addWidget(self.label_7)
        self.vbox.addWidget(self.label_4)
        self.vbox.addWidget(self.label_5)
        self.vbox.addWidget(self.label_6)
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
