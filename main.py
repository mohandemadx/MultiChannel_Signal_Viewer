
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import pyqtgraph as pg
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QMainWindow
import os
from os import path
import sys
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "task1_design.ui"))


class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)

        self.setupUi(self)
        self.button = self.findChild(QPushButton, "pushButton")
        self.setWindowTitle("Multi-Channel Signal Viewer")

        # Initialize the graphs
        self.plotdata1 = []
        self.plotdata2 = []
        self.x1 = np.linspace(0, 10000, 10000)
        self.x2 = np.linspace(0, 10000, 10000)
        self.idx_1 = 0
        self.idx_2 = 0

        # To store file paths
        self.file_paths = {}
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
        self.signal_checkboxes2= []

        # Control
        self.horizontalScrollBar.setRange(0, len(self.x1))
        self.horizontalScrollBar.valueChanged.connect(self.scroll_graph)
        self.horizontalScrollBar_2.setRange(0, len(self.x2))
        self.horizontalScrollBar_2.valueChanged.connect(self.scroll_graph2)
        self.ZoomInButton1.clicked.connect(self.zoomIn)
        self.ZoomOutButton1.clicked.connect(self.zoomOut)
        self.ZoomInButton2.clicked.connect(self.zoomIn2)
        self.ZoomOutButton2.clicked.connect(self.zoomOut2)
        self.exportButton1.clicked.connect(self.export_to_pdf)
        self.exportButton2.clicked.connect(self.export_to_pdf2)

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

        self.paused1 = not self.paused1

        if self.paused1:
            # If paused, stop the timer
            self.timer1.stop()
        else:
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

        self.paused2 = not self.paused2

        if self.paused2:

            self.timer2.stop()
        else:

            self.timer2.start()
        if self.syncCheckBox.isChecked():
            self.paused1 = not self.paused1

            if self.paused1:

                self.timer1.stop()
            else:

                self.timer1.start()

    def rewind1(self):
        self.graphicsView.clear()
        self.idx_1 = 0
        if self.syncCheckBox.isChecked():
            self.graphicsView_2.clear()
            self.idx_2 = 0

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

    def retrievedata(self):

        chosenpath = self.getFilePath()
        data = np.fromfile(chosenpath, dtype=np.int16)
        return data

    def update_data1(self):
        window_width = 250
        window_position = self.idx_1
        x_min = window_position
        x_max = min(len(self.x1), window_position + window_width)
        self.graphicsView.setXRange(x_min, x_max)

        for i in range(len(self.plotdata1)):
            plot_item = self.graphicsView.plot(pen=self.colors1[i])
            if self.signal_checkboxes[i].isChecked():  # Check the visibility state
                plot_item.setData(self.x1[x_min:x_max], self.plotdata1[i][x_min:x_max])
            else:
                plot_item = self.graphicsView.plot(pen=None)
        self.idx_1 += 1
        if self.idx_1 >= len(self.x1):
            self.idx_1 = 0

    def update_data2(self):
        window_width2 = 250
        window_position2 = self.idx_2
        x2_min =  window_position2
        x2_max = min(len(self.x2), window_position2 + window_width2)
        self.graphicsView_2.setXRange(x2_min, x2_max)

        for i in range(len(self.plotdata2)):
            plot_item = self.graphicsView_2.plot(pen=self.colors2[i])
            if self.signal_checkboxes2[i].isChecked():
                plot_item.setData(self.x2[x2_min:x2_max], self.plotdata2[i][x2_min:x2_max])
            else:
                plot_item = self.graphicsView.plot(pen=None)
        self.idx_2 += 1
        if self.idx_2 >= len(self.x2):
            self.idx_2 = 0

    def selectedGraph(self):
        if self.radioButton1.isChecked():
            graph = 1
        else:
            graph = 2
        return graph

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
            self.layout1.addWidget(checkbox)
            self.signal_checkboxes.append(checkbox)

        elif graph == 2:
            self.plotdata2.append(data)
            self.colors2.append(color)
            self.timer2.start(self.time_interval2)
            checkbox = QCheckBox(f'{self.label_ImportedFileName.text()}', self)
            checkbox.setChecked(True)
            self.layout2.addWidget(checkbox)
            self.signal_checkboxes2.append(checkbox)

    def scroll_graph(self, position):
        window_width = 250
        window_position = position
        x_min = max(0, position - window_width // 2)
        x_max = min(len(self.x1), x_min + window_width)
        self.graphicsView.setXRange(x_min, x_max)

    def scroll_graph2(self, position):
        window_width2 = 250
        window_position2 = position
        x2_min = max(0, position - window_width2 // 2)
        x2_max = min(len(self.x2), x2_min + window_width2)
        self.graphicsView_2.setXRange(x2_min, x2_max)

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

    def calculate_statistics(self):
        statistics = []
        mean = []
        std_dev = []
        minimum = []
        maximum = []
        statistics.append(["Signal Number:", "Mean", "Std_dev", "Minimum", "Maximum"])
        for i in range(len(self.plotdata1)):
            mean.append(np.mean(self.plotdata1[i]))
            std_dev.append(np.std(self.plotdata1[i]))
            minimum.append(np.min(self.plotdata1[i]))
            maximum.append(np.max(self.plotdata1[i]))
        for j in range(len(self.plotdata1)):
            statistics.append([j+1, round(mean[j]), round(std_dev[j]), round(minimum[j]), round(maximum[j])])
        stats = Table(statistics)

        return stats

    def calculate_statistics2(self):
        statistics2 = []
        mean2 = []
        std_dev2 = []
        minimum2 = []
        maximum2 = []
        statistics2.append(["Signal Number:", "Mean", "Std_dev", "Minimum", "Maximum"])
        for i in range(len(self.plotdata2)):
            mean2.append(np.mean(self.plotdata2[i]))
            std_dev2.append(np.std(self.plotdata2[i]))
            minimum2.append(np.min(self.plotdata2[i]))
            maximum2.append(np.max(self.plotdata2[i]))
        for j in range(len(self.plotdata2)):
            statistics2.append([j + 1, round(mean2[j]), round(std_dev2[j]), round(minimum2[j]), round(maximum2[j])])
        stats2 = Table(statistics2)

        return stats2

    def export_to_pdf(self):
        frame_to_capture = self.graphicsView
        pixmap = frame_to_capture.grab()
        file_path1 = "screenshot1.png"
        pixmap.save(file_path1, "PNG")
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")

        if file_path:
            # Create a PDF file (output.pdf) with letter-sized pages
            Report = canvas.Canvas(file_path, pagesize=letter)
            Report.setFont("Helvetica", 12)

            # Draw some text on the PDF
            Report.drawString(100, 750, "Graph 1")
            aspectRatio = 3
            Report.drawImage(file_path1, 100, 600, 400, 133)
            table = self.calculate_statistics()
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header row background color
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header bottom padding
                ('BACKGROUND', (0, 1), (-1, -1), colors.ghostwhite),  # Data row background color
                ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Table grid color and width
            ])
            table.setStyle(style)
            table.wrapOn(Report, 0, 0)
            table.drawOn(Report, 150, 525)
            Report.save()

    def export_to_pdf2(self):
        frame_to_capture2 = self.graphicsView_2
        pixmap2 = frame_to_capture2.grab()
        file_path2 = "screenshot.png"
        pixmap2.save(file_path2, "PNG")
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")

        if file_path:
            # Create a PDF file (output.pdf) with letter-sized pages
            Report2 = canvas.Canvas(file_path, pagesize=letter)
            Report2.setFont("Helvetica", 12)

            # Draw some text on the PDF
            Report2.drawString(100, 750, "Graph 2")
            aspectRatio2 = 3
            Report2.drawImage(file_path2, 100, 600, 400, 133)

            table2 = self.calculate_statistics2()
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header row background color
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header bottom padding
                    ('BACKGROUND', (0, 1), (-1, -1), colors.ghostwhite),  # Data row background color
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Table grid color and width
                ])
            table2.setStyle(style)
            table2.wrapOn(Report2, 0, 0)
            table2.drawOn(Report2, 150, 525)
            Report2.save()


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
