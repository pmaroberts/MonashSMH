import math
import sys
import os
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, \
    QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout


class GCodeFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(self.file_path)
        self.quantity = 1
        self.time_original = 0
        self.material_original = 0
        self.calcTimeMaterial()
        self.time = self.time_original
        self.material = self.material_original

    def __str__(self):
        return f'{self.filename} x{self.quantity}'

    def calcTimeMaterial(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                if line.startswith(';TIME:'):
                    time_value = float(line.strip().split(':')[1])
                    # print(time_value)
                elif line.startswith(';Filament used:'):
                    material_value = float(line.strip().split(':')[1].strip("m"))
                    # print(material_value)
        self.time_original = time_value
        self.material_original = GCodeFile.jacobianConversion(material_value)

    def setQuantity(self, quantity):
        self.quantity = quantity
        self.time = self.time_original * quantity
        self.material = self.material_original * quantity

    def getTime(self):
        return self.time

    def getMaterial(self):
        return round(self.material, 3)

    @staticmethod
    def jacobianConversion(length, diameter=1.75, density=1.25):
        """
        Method for converting from length to mass for filament
        :param length: Length [m]
        :param diameter: [mm]
        :param density: [g/cm^3]
        :return: mass [g]
        """
        return (length * math.pi * ((diameter * 0.001) / 2) ** 2) * density * 1000000


class MainWindow(QMainWindow):

    order_now_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.files: List[GCodeFile] = []

        self.setWindowTitle('Order Management System')

        self.job_title_label = QLabel('Job Title:')
        self.job_title_input = QLineEdit()
        self.user_name_label = QLabel('User Name:')
        self.user_name_input = QLineEdit()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['File Name', 'Quantity', 'Time [s]', 'Material[g]'])

        self.add_file_button = QPushButton('Add File')
        self.add_file_button.clicked.connect(self.add_file)

        self.delete_file_button = QPushButton('Delete File')
        self.delete_file_button.clicked.connect(self.delete_file)

        self.total_print_time_label = QLabel('Total Print Time [seconds]:')
        self.total_print_time_input = QLineEdit()
        self.total_print_time_input.setReadOnly(True)

        self.total_material_label = QLabel('Total Material [g]:')
        self.total_material_input = QLineEdit()
        self.total_material_input.setReadOnly(True)

        self.estimated_pickup_time_label = QLabel('Estimated Pickup Time:')
        self.estimated_pickup_time_input = QLineEdit()
        self.estimated_pickup_time_input.setReadOnly(True)

        self.order_button = QPushButton('Order Now')
        self.order_button.clicked.connect(self.emit_order_now_signal)

        top_layout = QVBoxLayout()
        top_layout.addWidget(self.job_title_label)
        top_layout.addWidget(self.job_title_input)
        top_layout.addWidget(self.user_name_label)
        top_layout.addWidget(self.user_name_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_file_button)
        button_layout.addWidget(self.delete_file_button)
        button_layout.addStretch(1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.total_print_time_label)
        bottom_layout.addWidget(self.total_print_time_input)
        bottom_layout.addWidget(self.total_material_label)
        bottom_layout.addWidget(self.total_material_input)
        bottom_layout.addWidget(self.estimated_pickup_time_label)
        bottom_layout.addWidget(self.estimated_pickup_time_input)
        bottom_layout.addWidget(self.order_button)

        main_layout.addLayout(bottom_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        self.table.itemChanged.connect(self.update_quantity)

        self.setStyleSheet("""
    QMainWindow {
        background-color: #f2f2f2;
    }
    
    QLabel {
        font-weight: bold;
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

    def updateTable(self):
        self.table.itemChanged.disconnect(self.update_quantity)  # Disconnect the signal temporarily
        self.table.setRowCount(len(self.files))
        for row, file in enumerate(self.files):
            file_name_item = QTableWidgetItem(file.filename)
            quantity_item = QTableWidgetItem(str(file.quantity))
            time_item = QTableWidgetItem(str(file.time))
            material_item = QTableWidgetItem(str(file.getMaterial()))

            self.table.setItem(row, 0, file_name_item)
            self.table.setItem(row, 1, quantity_item)
            self.table.setItem(row, 2, time_item)
            self.table.setItem(row, 3, material_item)
        self.table.itemChanged.connect(self.update_quantity)  # Reconnect the signal
        self.update_totals()

    def add_file(self):
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(self, 'Select File(s)', filter="Gcode (*.gcode)")
        if files:
            for file in files:
                self.files.append(GCodeFile(file))
            self.updateTable()

    def delete_file(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        for row in reversed(sorted(selected_rows)):
            self.files.pop(row)
        self.updateTable()

    def update_quantity(self, item):
        if item.column() == 1:  # Check if the changed item is in the Quantity column
            row = item.row()
            quantity = int(item.text())
            self.files[row].setQuantity(quantity)
        self.updateTable()

    def update_totals(self):
        total_print_time = sum(file.time for file in self.files)
        total_material = sum(file.getMaterial() for file in self.files)

        self.total_print_time_input.setText(str(total_print_time))
        self.total_material_input.setText(str(total_material))

    def emit_order_now_signal(self):
        # Send the babyMES the data
        # list_to_emit = []
        # for file in self.files:
        #     list_to_emit.append((file.quantity, file.filename))
        self.order_now_signal.emit(self.files)

        # Clear the table
        self.files = []
        self.updateTable()


