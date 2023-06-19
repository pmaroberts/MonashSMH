import os
import sys


from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QSizePolicy, \
    QApplication

from PrinterStateMachine.PrinterData import PrinterData
from baby_mes_ui.QueueWidget import PrinterQueueWidget


class PrinterDataWidget(QWidget):
    def __init__(self, printer_number, printer_data: PrinterData):
        super().__init__()
        self.printer_number = printer_number
        self.p_data = printer_data
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)  # Set horizontal spacing
        layout.setVerticalSpacing(20)  # Set vertical spacing
        self.setLayout(layout)

        self.name_label = QLabel("Name:")
        self.name_value_label = QLabel(f"Printer {self.printer_number}")
        self.name_value_label.setAlignment(Qt.AlignRight)

        self.state_label = QLabel("State:")
        self.state_value_label = QLabel("PrinterState")
        self.state_value_label.setAlignment(Qt.AlignRight)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_value_label, 0, 1)
        layout.addWidget(self.state_label, 1, 0)
        layout.addWidget(self.state_value_label, 1, 1)
        layout.addWidget(self.progress_bar, 2, 0, 1, 2)

        layout.rowStretch(1)

        self.log_button = QPushButton("Log Pickup")
        self.log_button.clicked.connect(self.log_pickup)
        layout.addWidget(self.log_button, 3, 0, 1, 2)

        self.setStyleSheet("font-size: 20px")

    def get_data(self):
        printer_state = self.p_data.node_value_get("state_node")
        self.state_value_label.setText(printer_state)

        if printer_state == "heating":
            target = self.p_data.node_value_get("bed_temp_target") + self.p_data.node_value_get("noz_temp_target")
            current = self.p_data.node_value_get("bed_temp_node") + self.p_data.node_value_get("noz_temp_node")
            if target == 0:
                self.progress_bar.setValue(0)
            else:
                self.progress_bar.setValue(int(current / target * 100))
        elif printer_state == "printing":
            self.progress_bar.setValue(int(self.p_data.node_value_get("job_progress_node")))
        else:
            self.progress_bar.setValue(0)

    def log_pickup(self):
        self.p_data.node_value_change("part_removed_node", True)


class PrinterWidget(QWidget):
    def __init__(self, printer_number):
        super().__init__()
        self.printer_number = printer_number
        self.setWindowTitle(f"Printer {self.printer_number}")
        self.p_data = PrinterData(printer_number - 1)
        self.data_widget = PrinterDataWidget(self.printer_number, self.p_data)
        self.timer = QTimer(interval=500)
        self.init_ui()
        # self.update_data()
        self.timer.timeout.connect(self.update_data)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        video_stream_view = QWebEngineView()
        video_stream_url = QUrl(self.p_data.stream_url)
        video_stream_view.load(video_stream_url)

        video_stream_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy to expand

        layout.addWidget(video_stream_view)

        layout.addStretch(1)  # Add vertical stretch to separate video stream and printer info

        layout.addWidget(self.data_widget)

    def update_data(self):
        self.data_widget.get_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.timer.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Printer Monitoring")

    layout = QGridLayout()
    layout.addWidget(PrinterQueueWidget())
    layout.addWidget(PrinterWidget(1), 0, 1)
    layout.addWidget(PrinterWidget(2), 0, 2)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec_())
