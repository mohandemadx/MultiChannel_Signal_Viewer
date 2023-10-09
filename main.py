

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import os
from os import path
import sys

FORM_CLASS,_=loadUiType(path.join(path.dirname(__file__),"task1_design.ui"))

class MainApp(QMainWindow , FORM_CLASS):
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.data = np.fromfile("emg_healthy.dat", dtype=np.int16)
        self.data = (self.data - np.min(self.data)) / (np.max(self.data) - np.min(self.data))
    # Create a counter to keep track of the current sample
        self.current_sample = 0

    # Create a timer object
        self.timer1 = pg.QtCore.QTimer()
        self.timer2 = pg.QtCore.QTimer()
        self.timer1.setInterval(500)  # set the timer to fire every 50 ms
        self.timer1.timeout.connect(self.update)
        self.timer1.start()
        self.timer2.setInterval(500)  # set the timer to fire every 50 ms
        self.timer2.timeout.connect(self.update2)
        self.timer2.start()
        self.paused1 = False
        self.paused2 = False
        self.PlayButton1.clicked.connect(self.togglePause1)
        self.PlayButton2.clicked.connect(self.togglePause2)
        self.rewindButton1.clicked.connect(self.rewind)
        self.rewindButton2.clicked.connect(self.rewind)
    def togglePause1(self):
        # Toggle the pause state
        self.paused1 = not self.paused1

        if self.paused1:
            # If paused, stop the timer
            self.timer1.stop()
        else:
            # If unpaused, start the timer
            self.timer1.start()
    def togglePause2(self):
        # Toggle the pause state
        self.paused2 = not self.paused2

        if self.paused2:
            # If paused, stop the timer
            self.timer2.stop()
        else:
            # If unpaused, start the timer
            self.timer2.start()
    def rewind(self):
        self.current_sample = 0
    def update(self):
    # Clear the current plot
       self.graphicsView.clear()

       end_index = min(self.current_sample + 25, len(self.data))
    # Update the plot with the current sample
       x = np.arange(self.current_sample, end_index)
       y = self.data[self.current_sample:end_index]
       self.graphicsView.plot(x, y, pen='red')

    # Set the x-axis range based on the current sample and the length of the data
       #self.graphicsView.setXRange(self.current_sample, len(self.data))

    # Add a grid
       self.graphicsView.showGrid(x=True, y=True)

    # Update the current sample
       self.current_sample += 25

    # If we've reached the end of the data, loop back to the start
       if self.current_sample >= len(self.data):
         self.current_sample = 0
    def update2(self):
    # Clear the current plot
       self.graphicsView_2.clear()

       #end_index = min(self.current_sample + 1000, len(self.data))
    # Update the plot with the current sample
       self.graphicsView_2.plot(self.data[self.current_sample:self.current_sample + 1000])

    # Add a grid
       self.graphicsView_2.showGrid(x=True, y=True)

    # Update the current sample
       self.current_sample += 1000

    # If we've reached the end of the data, loop back to the start
       if self.current_sample >= len(self.data):
         self.current_sample = 0


"""
    
    
    ```
    def plott(self, graph_widget, file_path):
            data = pd.read_csv(file_path).values
            y = np.squeeze(data)
            x = np.arange(0, np.prod(y.shape))
            graph_widget.plot(x, y)

    def reset(self):
        self.graphicsView.clear()

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open DAT File", "", "DAT Files (*.dat);;All Files (*)",
                                                   options=options)
        if file_path:
            self.plot(ui.graphicsView, file_path)
    """

def main():
    app = QApplication(sys.argv)
    window= MainApp()
    window.show()
    app.exec_()

if __name__ =='__main__':
    main()











