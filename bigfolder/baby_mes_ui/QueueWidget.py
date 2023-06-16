import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, \
    QProgressBar


class PrinterQueueWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.queue_list = QListWidget()

        # Add some sample jobs to the queue
        for job in ['Job 1', 'Job 2', 'Job 3', 'Job 4']:
            self.queue_list.addItem(job)

        # Create buttons for moving items
        self.up_button = QPushButton('Move Up')
        self.down_button = QPushButton('Move Down')
        self.submit_button = QPushButton('Submit')

        # Connect the buttons to the appropriate functions
        self.up_button.clicked.connect(self.move_item_up)
        self.down_button.clicked.connect(self.move_item_down)

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
