import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, \
    QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout


def analyze_text_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(';TIME:'):
                time_value = float(line.strip().split(':')[1])
                print(time_value)
            elif line.startswith(';Filament used:'):
                material_value = float(line.strip().split(':')[1].strip("m"))
                print(material_value)

    return time_value, material_value


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Order Management System')

        self.job_title_label = QLabel('Job Title:')
        self.job_title_input = QLineEdit()
        self.user_name_label = QLabel('User Name:')
        self.user_name_input = QLineEdit()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['File Name', 'Quantity', 'Time', 'Material'])

        self.add_file_button = QPushButton('Add File')
        self.add_file_button.clicked.connect(self.add_file)

        self.delete_file_button = QPushButton('Delete File')
        self.delete_file_button.clicked.connect(self.delete_file)

        self.analyse_button = QPushButton('Analyse Now')
        # self.analyse_button.clicked.connect()

        self.total_print_time_label = QLabel('Total Print Time:')
        self.total_print_time_input = QLineEdit()
        self.total_print_time_input.setReadOnly(True)

        self.total_material_label = QLabel('Total Material:')
        self.total_material_input = QLineEdit()
        self.total_material_input.setReadOnly(True)

        self.estimated_pickup_time_label = QLabel('Estimated Pickup Time:')
        self.estimated_pickup_time_input = QLineEdit()
        self.estimated_pickup_time_input.setReadOnly(True)

        self.order_button = QPushButton('Order Now')

        top_layout = QVBoxLayout()
        top_layout.addWidget(self.job_title_label)
        top_layout.addWidget(self.job_title_input)
        top_layout.addWidget(self.user_name_label)
        top_layout.addWidget(self.user_name_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_file_button)
        button_layout.addWidget(self.delete_file_button)
        button_layout.addWidget(self.analyse_button)
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

        self.table.itemChanged.connect(self.update_time_material)

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

    def add_file(self):
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(self, 'Select File(s)', filter="Gcode (*.gcode)")
        if files:
            row_count = self.table.rowCount()
            self.table.setRowCount(row_count + len(files))

            for row, file_path in enumerate(files):
                file_name = os.path.basename(file_path)
                quantity_item = QTableWidgetItem('1')
                file_name_item = QTableWidgetItem(file_name)

                self.table.setItem(row_count + row, 0, file_name_item)
                self.table.setItem(row_count + row, 1, quantity_item)

                # Analyze file and update time and material columns
                # Analyze file and update time and material columns
                time_value, material_value = analyze_text_file(file_path)
                if time_value:
                    time_item = QTableWidgetItem(str(time_value))
                    self.table.setItem(row_count + row, 2, time_item)
                if material_value:
                    material_item = QTableWidgetItem(str(material_value))
                    self.table.setItem(row_count + row, 3, material_item)

    def delete_file(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        for row in reversed(sorted(selected_rows)):
            self.table.removeRow(row)

    def update_time_material(self, item):
        if item.column() == 1:  # Check if the changed item is in the Quantity column
            row = item.row()
            quantity = int(item.text())

            # Get the time and material values from the table
            time_item = self.table.item(row, 2)
            material_item = self.table.item(row, 3)

            if time_item and material_item:
                # Multiply time and material values by the quantity
                time_value = float(time_item.text()) * quantity
                material_value = float(material_item.text()) * quantity

                # Update the time and material values in the table
                time_item.setText(str(time_value))
                material_item.setText(f'{material_value:.2f}')


app = QApplication([])
window = MainWindow()

window.show()
sys.exit(app.exec_())
