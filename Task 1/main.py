

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import pyqtgraph as pg
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import os
from os import path
import sys
import icons_rc

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "task1_design.ui"))


class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)

        self.setupUi(self)
        self.button = self.findChild(QPushButton, "pushButton")
        self.setWindowTitle("Multi-Channel Signal Viewer")

        # Initialize the graphs
        # self.graphicsView.setBackground('w')
        # self.graphicsView_2.setBackground('w')
        self.plotdata1 = []
        self.plotdata2 = []

        self.x1 = np.linspace(0, 10000, 10000)
        self.x2 = np.linspace(0, 10000, 10000)
        self.idx_1 = 0
        self.idx_2 = 0

        # To store file paths
        self.file_paths = {}
        self.keystoremove = []
        self.colors1 = []
        self.colors2 = []

        # Create a timer object
        self.timer1 = pg.QtCore.QTimer()
        self.timer2 = pg.QtCore.QTimer()

        # Pause & Play Buttons
        self.paused1 = False
        self.paused2 = False
        self.PlayButton1.clicked.connect(self.togglePause1)
        self.PlayButton2.clicked.connect(self.togglePause2)

        # Rewind Buttons
        self.rewindButton1.clicked.connect(self.rewind1)
        self.rewindButton2.clicked.connect(self.rewind2)

        # Speed Sliders
        self.speedUp1.clicked.connect(self.Up1)
        self.speedUp2.clicked.connect(self.Up2)
        self.speedDown1.clicked.connect(self.Down1)
        self.speedDown2.clicked.connect(self.Down2)

        self.current_speed1 = 100
        self.current_speed2 = 100
        self.int_speed2 = 100

        # set time intervals
        self.time_interval1 = 100
        self.time_interval2 = 100
        self.timer1.setInterval(self.time_interval1)  # set the timer to fire every "time_interval" ms
        self.timer2.setInterval(self.time_interval2)  # set the timer to fire every "time_interval" ms

        self.timer1.timeout.connect(self.update_data1)
        self.timer2.timeout.connect(self.update_data2)

        # Importing a File Button
        self.uploadButton.clicked.connect(self.uploadFun)

        # Plot-Signal Button
        self.plotsignalButton.clicked.connect(self.plotSignal)

        # Sync CheckBox
        self.syncCheckBox.stateChanged.connect(self.sync_fun)

        # signal checkboxes
        self.signal_checkboxes = []

        # Control
        self.horizontalScrollBar.setRange(0, len(self.x1))
        self.horizontalScrollBar.valueChanged.connect(self.scroll_graph)
        self.horizontalScrollBar_2.setRange(0, len(self.x2))
        self.horizontalScrollBar_2.valueChanged.connect(self.scroll_graph2)
        self.ZoomInButton1.clicked.connect(self.zoomIn)
        self.ZoomOutButton1.clicked.connect(self.zoomOut)
        self.ZoomInButton2.clicked.connect(self.zoomIn2)
        self.ZoomOutButton2.clicked.connect(self.zoomOut2)

        #Fixing windows


    # Class Functions
    def sync_fun(self):
        if self.syncCheckBox.isChecked():
            sync_value = self.current_speed1
            self.current_speed2 = sync_value

            self.time_interval1 = int(self.current_speed1)  # Update timer interval based on the slider
            if self.timer1.isActive():
                self.timer1.setInterval(self.time_interval1)

            self.time_interval2 = int(self.current_speed2)  # Update timer interval based on the slider
            if self.timer2.isActive():
                self.timer2.setInterval(self.time_interval2)
        else:
            self.current_speed2 = self.int_speed2

            self.time_interval2 = int(self.current_speed2)  # Update timer interval based on the slider
            if self.timer2.isActive():
                self.timer2.setInterval(self.time_interval2)

    def uploadFun(self):

        self.label_ImportedFileName.setText('')

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # Set a custom filter to show only .dat and .csv files
        filter = "CSV and DAT Files (*.csv *.dat)"
        files, _ = QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "", filter, options=options)

        if files:
            for file in files:
                # Store file path
                fileName = os.path.basename(file)
                self.file_paths[fileName] = file
                # Add file NAME as a clickable link in the QListWidget
                # Assume self.label_ImportedFileName is a QLabel
                self.label_ImportedFileName.setText(fileName)

    def Up1(self):
        if self.current_speed1 > 1:
            self.current_speed1 = self.current_speed1 / 10
            self.time_interval1 = int(self.current_speed1)  # Update timer interval based on the slider
            if self.timer1.isActive():
                self.timer1.setInterval(self.time_interval1)
        else:
            return

    def Up2(self):
        if self.current_speed2 > 1:
            self.current_speed2 /= 10
            self.time_interval2 = int(self.current_speed2)  # Update timer interval based on the slider
            self.int_speed2 = self.time_interval2
            if self.timer2.isActive():
                self.timer2.setInterval(self.time_interval2)
        else:
            return

    def Down1(self):
        if self.current_speed1 < 10000:
            self.current_speed1 *= 10
            self.time_interval1 = int(self.current_speed1)  # Update timer interval based on the slider
            if self.timer1.isActive():
                self.timer1.setInterval(self.time_interval1)
        else:
            return

    def Down2(self):
        if self.current_speed2 < 10000:
            self.current_speed2 *= 10
            self.time_interval2 = int(self.current_speed2)  # Update timer interval based on the slider
            self.int_speed2 = self.time_interval2
            if self.timer2.isActive():
                self.timer2.setInterval(self.time_interval2)
        else:
            return

    def getFilePath(self):
        selected_item = self.label_ImportedFileName

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

    def togglePause1(self):
        # Toggle the pause state
        self.paused1 = not self.paused1

        if self.paused1:
            # If paused, stop the timer
            self.timer1.stop()
        else:
            # If unpaused, start the timer
            self.timer1.start()
        if self.syncCheckBox.isChecked():
            self.paused2 = not self.paused2

            if self.paused2:
                # If paused, stop the timer
                self.timer2.stop()
            else:
                # If unpaused, start the timer
                self.timer2.start()


    def togglePause2(self):
        # Toggle the pause state
        self.paused2 = not self.paused2

        if self.paused2:
            # If paused, stop the timer
            self.timer2.stop()
        else:
            # If unpaused, start the timer
            self.timer2.start()
        if self.syncCheckBox.isChecked():
            self.paused1 = not self.paused1

            if self.paused1:
                # If paused, stop the timer
                self.timer1.stop()
            else:
                # If unpaused, start the timer
                self.timer1.start()

    def rewind1(self):
        self.graphicsView.clear()
        self.idx_1 = 0
        if self.syncCheckBox.isChecked():
            self.graphicsView_2.clear()
            self.idx_2=0

    def rewind2(self):
        self.graphicsView_2.clear()
        self.idx_2 = 0
        if self.syncCheckBox.isChecked():
            self.graphicsView.clear()
            self.idx_1 = 0


    def selected_color(self):
        selected_color = self.comboBox_color.currentText()

        # Map color names to QColor objects
        color_mapping = {
            "red": QColor("red"),
            "blue": QColor("blue"),
            "white": QColor("white"),
            "purple": QColor("purple"),
            "yellow": QColor("yellow"),
            "green": QColor("green")
        }

        plot_color = color_mapping[selected_color]
        return plot_color

    def retrievedata(self): #returns the dataset
        chosenpath = self.getFilePath()
        data = np.fromfile(chosenpath, dtype=np.int16)
        # standardization
        #data = (data - np.min(data)) / (np.max(data) - np.min(data))

        return data

    def update_data1(self):
        window_width=100
        self.window_position=self.idx_1
        self.x_min= self.window_position
        self.x_max = min(len(self.x1), self.window_position + window_width)
        self.graphicsView.setXRange(self.x_min, self.x_max)

        for i in range(len(self.plotdata1)):
            plot_item = self.graphicsView.plot(pen=self.colors1[i])
            plot_item.setData(self.x1[self.x_min:self.x_max], self.plotdata1[i][self.x_min:self.x_max])
        self.idx_1 += 1
        if self.idx_1 >= len(self.x1):
            self.idx_1 = 0
    def update_data2(self):
        window_width2 = 100
        self.window_position2 = self.idx_2
        self.x2_min = self.window_position2
        self.x2_max = min(len(self.x2), self.window_position2 + window_width2)
        self.graphicsView_2.setXRange(self.x2_min, self.x2_max)

        for i in range(len(self.plotdata2)):
            plot_item = self.graphicsView_2.plot(pen=self.colors2[i])
            plot_item.setData(self.x2[self.x2_min:self.x2_max], self.plotdata2[i][self.x2_min:self.x2_max])
        self.idx_2 += 1
        if self.idx_2 >= len(self.x2):
            self.idx_2 = 0

    def selectedGraph(self):
        if self.radioButton1.isChecked():
            graph = 1
        else:
            graph = 2
        return graph

    # def toggle_signal_visibility(self):
    #     #hide function
    def plotSignal(self):

        graph = self.selectedGraph()
        color = self.selected_color()
        data = self.retrievedata()

        if graph == 1:
            self.plotdata1.append(data)
            self.colors1.append(color)
            self.timer1.start(self.time_interval1)

            checkbox = QCheckBox(f'{self.label_ImportedFileName.text()}', self)

            checkbox.setChecked(True)
            # checkbox.stateChanged.connect(self.toggle_signal_visibility)
            self.layout1.addWidget(checkbox)
            self.signal_checkboxes.append(checkbox)

        elif graph == 2:
            self.plotdata2.append(data)
            self.colors2.append(color)
            self.timer2.start(self.time_interval2)

            checkbox = QCheckBox(f'{self.label_ImportedFileName.text()}', self)

            checkbox.setChecked(True)
            # checkbox.stateChanged.connect(self.toggle_signal_visibility)
            self.layout2.addWidget(checkbox)
            self.signal_checkboxes.append(checkbox)

    def scroll_graph(self, position):

        self.window_width=100
        self.window_position = position
        self.x_min = max(0, position - self.window_width // 2)
        self.x_max = min(len(self.x1), self.x_min + self.window_width)
        self.graphicsView.setXRange(self.x_min, self.x_max)

    def scroll_graph2(self, position):

        self.window_width2=100
        self.window_position2 = position
        self.x2_min = max(0, position - self.window_width2 // 2)
        self.x2_max = min(len(self.x2), self.x2_min + self.window_width2)
        self.graphicsView_2.setXRange(self.x_min, self.x_max)
    def zoomIn(self):
        zoom_factor = 0.8
        self.graphicsView.getViewBox().scaleBy((zoom_factor, zoom_factor))
        if self.syncCheckBox.isChecked():
            self.graphicsView_2.getViewBox().scaleBy((zoom_factor, zoom_factor))

    def zoomOut(self):
        zoom_factor = 1.2
        self.graphicsView.getViewBox().scaleBy((zoom_factor, zoom_factor))
        if self.syncCheckBox.isChecked():
            self.graphicsView_2.getViewBox().scaleBy((zoom_factor, zoom_factor))

    def zoomIn2(self):
        zoom_factor = 0.8
        self.graphicsView.getViewBox().scaleBy((zoom_factor, zoom_factor))
        if self.syncCheckBox.isChecked():
            self.graphicsView_2.getViewBox().scaleBy((zoom_factor, zoom_factor))

    def zoomOut2(self):
        zoom_factor = 1.2
        self.graphicsView.getViewBox().scaleBy((zoom_factor, zoom_factor))
        if self.syncCheckBox.isChecked():
            self.graphicsView_2.getViewBox().scaleBy((zoom_factor, zoom_factor))

#     def hideSignal(self):


#    def stats(self):

#    def addLabels(self):


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
