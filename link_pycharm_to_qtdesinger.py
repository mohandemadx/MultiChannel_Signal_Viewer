import sys
from PyQt5 import QtWidgets, uic , QtGui, QtPrintSupport, QtSvg
import os

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Load the UI file created with Qt Designer
        uic.loadUi(r"C:\Users\hp\PycharmProjects\pythonProject\venv\Lib\site-packages\qt5_applications\Qt\bin\snapshot_ui.ui", self)
        self.setWindowTitle("Snapshot to PDF Example")

        # Create a central widget
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        # Add a layout to the central widget
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Add a label to the layout
        label = QtWidgets.QLabel("Hello, World!")
        layout.addWidget(label)

        # Add a button to take a snapshot
        button = QtWidgets.QPushButton("Take Snapshot")
        button.clicked.connect(self.take_snapshot)
        layout.addWidget(button)

    def take_snapshot(self):
        # Create a pixmap of the application's current screen
        pixmap = self.grab()

        # Create a QPainter to draw on the pixmap
        painter = QtGui.QPainter(pixmap)

        # Draw additional content on the pixmap (optional)
        painter.drawText(10, 10, "Snapshot Content")

        # End painting
        painter.end()

        # Create a QPrinter for PDF output
        printer = QtPrintSupport.QPrinter()
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setOutputFileName("snapshot.pdf")

        # Create a QPainter for the printer
        painter = QtGui.QPainter()
        painter.begin(printer)

        # Draw the pixmap on the PDF
        painter.drawPixmap(0, 0, pixmap)

        # End painting
        painter.end()
        self.grab().save("snapshot.pdf", "PDF")
        print("Snapshot saved as 'snapshot.pdf'")
        print("Current working directory:", os.getcwd())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())





