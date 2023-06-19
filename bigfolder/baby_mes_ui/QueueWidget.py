import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, \
    QProgressBar


class PrinterQueueWidget(QWidget):
    send_queue_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.queue_list = QListWidget()

        # Create buttons for moving items
        self.up_button = QPushButton('Move Up')
        self.down_button = QPushButton('Move Down')

        self.submit_button = QPushButton('Submit')

        # Connect the buttons to the appropriate functions
        self.up_button.clicked.connect(self.move_item_up)
        self.down_button.clicked.connect(self.move_item_down)
        self.submit_button.clicked.connect(self.emit_send_queue_signal)

        # Add the widgets to the layout
        self.layout.addWidget(self.queue_list)
        self.layout.addWidget(self.up_button)
        self.layout.addWidget(self.down_button)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)
        self.setWindowTitle('Printer Queue')

    def move_item_up(self):
        current_row = self.queue_list.currentRow()
        if current_row > 0:
            item = self.queue_list.takeItem(current_row)
            self.queue_list.insertItem(current_row - 1, item)
            self.queue_list.setCurrentRow(current_row - 1)

    def move_item_down(self):
        current_row = self.queue_list.currentRow()
        if current_row < self.queue_list.count() - 1:
            item = self.queue_list.takeItem(current_row)
            self.queue_list.insertItem(current_row + 1, item)
            self.queue_list.setCurrentRow(current_row + 1)

    def emit_send_queue_signal(self):
        to_send = []
        for i in range(self.queue_list.count()):
            to_send.append(self.queue_list.item(i).text())
        self.send_queue_signal.emit(to_send)

    def display_queue_list(self, queue: list[str]):
        self.queue_list.clear()
        for job in queue:
            self.queue_list.addItem(job)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()

    queue_widget = PrinterQueueWidget()

    layout = QHBoxLayout()
    layout.addWidget(queue_widget)

    window.setLayout(layout)
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f2f2f2;
        }

        QLabel {
            align-items: center;
        }

        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 2px;
        }

        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
        }

        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 5px 10px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 3px;
        }
    """)

    window.show()
    sys.exit(app.exec_())
