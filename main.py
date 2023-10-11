

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

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "task1_design.ui"))


class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.button = self.findChild(QPushButton, "pushButton")
        #self.data = np.fromfile("emg_healthy.dat", dtype=np.int16)
        #self.data = (self.data - np.min(self.data)) / (np.max(self.data) - np.min(self.data))
        #self.ComboBox.setCurrentIndex(-1)
    # Create a counter to keep track of the current sample
        self.current_sample = 0
        self.file_paths = {}  # List to store file paths
        self.keystoremove=[]
        # Open the file if the item in the List doubleClicked
        self.listWidget.itemDoubleClicked.connect(self.open_file)

    # Create a timer object
        self.timer1 = pg.QtCore.QTimer()
        self.timer2 = pg.QtCore.QTimer()
       # self.timer1.setInterval(1000)  # set the timer to fire every 50 ms
       # self.timer1.timeout.connect(self.update)
        # self.timer1.start()
       # self.timer2.setInterval(1000)  # set the timer to fire every 50 ms
       # self.timer2.timeout.connect(self.update2)
        #self.timer2.start()
        self.paused1 = False
        self.paused2 = False
        self.PlayButton1.clicked.connect(self.togglePause1)
        self.PlayButton2.clicked.connect(self.togglePause2)
        self.rewindButton1.clicked.connect(self.rewind)
        self.rewindButton2.clicked.connect(self.rewind)
        self.uploadButton.clicked.connect(self.uploadFun)
        self.deleteButton.clicked.connect(self.deleteFun)
        self.plotsignalButton.clicked.connect(self.plotSignal)
        self.comboBox.currentIndexChanged.connect(self.change_plot_color)
        self.sampling_frequency = 1000 # number of samples/ total time
    def uploadFun(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        files, _ = QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Text Files (*.txt)", options=options)

        if files:
            for file in files:
                # Store file path
                fileName = os.path.basename(file)
                self.file_paths[fileName] = file
                # Add file NAME as a clickable link in the QListWidget
                item = QListWidgetItem(fileName)
                item.setToolTip(file)  # Set the full path as the tooltip for reference
                item.setFlags(item.flags() | pg.QtCore.Qt.ItemIsSelectable)
                self.listWidget.addItem(item)

    def retrievedata(self):
        chosenpath=self.getFilePath()
        self.data = np.fromfile(chosenpath, dtype=np.int16)
        self.data = (self.data - np.min(self.data)) / (np.max(self.data) - np.min(self.data)) #standardization
    def getFilePath(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            selected_text = selected_item.text()
            for filename, file_path in self.file_paths.items():
                if selected_text == filename:
                    # Return the file path when a match is found
                    return file_path
            # Return None if no match is found
            return None
        else:
            # Return None if no item is selected
            return None
    def deleteFun(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            file_path = selected_item.toolTip()
            self.file_paths.remove(file_path)  # Remove the file path from the array
            self.listWidget.takeItem(
                self.listWidget.row(selected_item))  # Remove the item from the QList



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
         #self.graphicsView.clear()

         end_index = min(self.current_sample + 2000, len(self.data))
    # Update the plot with the current sample
       #x = np.arange(0, end_index)
         x= np.arange(self.current_sample,end_index )/ self.sampling_frequency
         y = self.data[self.current_sample: end_index]

         window_size = 5  # Set the desired window size in seconds
         x_min = max(0, x[-1] - window_size)  # Adjust the minimum x based on window size
         x_max = x[-1]  # Maximum x based on the latest data

    # Update the x-axis range
         self.graphicsView.setXRange(x_min, x_max)
         self.graphicsView.plot(x, y, pen=self.change_plot_color() )

    # Set the x-axis range based on the current sample and the length of the data
       #self.graphicsView.setXRange(self.current_sample, len(self.data))

    # Add a grid
         self.graphicsView.showGrid(x=True, y=True)

    # Update the current sample
         self.current_sample += 2000

    # If we've reached the end of the data, loop back to the start
         if self.current_sample >= len(self.data):
           self.current_sample = 0
           self.graphicsView.clear()
    def update2(self):
        end_index = min(self.current_sample + 2000, len(self.data))

    # Update the plot with the current sample
    # x = np.arange(0, end_index)
        x = np.arange(self.current_sample, end_index) / self.sampling_frequency
        y = self.data[self.current_sample: end_index]

        window_size = 5  # Set the desired window size in seconds
        x_min = max(0, x[-1] - window_size)  # Adjust the minimum x based on window size
        x_max = x[-1]  # Maximum x based on the latest data

    # Update the x-axis range
        self.graphicsView_2.setXRange(x_min, x_max)
        self.graphicsView_2.plot(x, y, pen=self.plot_color )

    # Set the x-axis range based on the current sample and the length of the data
    # self.graphicsView.setXRange(self.current_sample, len(self.data))

    # Add a grid
        self.graphicsView_2.showGrid(x=True, y=True)

    # Update the current sample
        self.current_sample += 2000

    # If we've reached the end of the data, loop back to the start
        if self.current_sample >= len(self.data):
           self.current_sample = 0
           self.graphicsView_2.clear()


    def open_file(self, item):
        file_path = item.text()
        if os.path.isfile(file_path):
            os.startfile(file_path)
    def change_plot_color(self):
        selected_color = self.comboBox.currentText()

        # Map color names to QColor objects
        color_mapping = {
            "red": QColor("red"),
            "blue": QColor("blue"),
            "white": QColor("white"),
            "purple": QColor("purple"),
            "yellow":  QColor("yellow"),
            "green": QColor("green")
        }

        self.plot_color = color_mapping[selected_color]
        return self.plot_color


    def plotSignal(self):

        if self.radioButton1.isChecked():
            data = self.retrievedata()
            self.timer1 = pg.QtCore.QTimer()
            self.timer1.setInterval(500)  # set the timer to fire every 50 ms
            self.timer1.timeout.connect(self.update)
            self.timer1.start()
        else:
            data = self.retrievedata()
            self.timer2 = pg.QtCore.QTimer()
            self.timer2.setInterval(1000)  # set the timer to fire every 50 ms
            self.timer2.timeout.connect(self.update2)
            self.timer2.start()




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











