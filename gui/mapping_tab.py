from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QTableWidget, QTableWidgetItem, QPushButton,
                           QComboBox, QDialog, QLabel, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt
from core.data_mapping import DataMapping, DataPoint

class MappingDialog(QDialog):
    def __init__(self, protocols, parent=None):
        super().__init__(parent)
        self.protocols = protocols
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Data Mapping")
        layout = QFormLayout(self)

        # Source protocol selection
        self.source_protocol = QComboBox()
        self.source_protocol.addItems(self.protocols.keys())
        layout.addRow("Source Protocol:", self.source_protocol)

        # Source tag configuration
        self.source_tag = QLineEdit()
        layout.addRow("Source Tag:", self.source_tag)

        # Destination protocol selection
        self.dest_protocol = QComboBox()
        self.dest_protocol.addItems(self.protocols.keys())
        layout.addRow("Destination Protocol:", self.dest_protocol)

        # Destination tag configuration
        self.dest_tag = QLineEdit()
        layout.addRow("Destination Tag:", self.dest_tag)

        # Buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

class MappingTab(QWidget):
    def __init__(self, protocols, parent=None):
        super().__init__(parent)
        self.protocols = protocols
        self.mapping_manager = DataMapping()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Mapping")
        edit_btn = QPushButton("Edit Mapping")
        delete_btn = QPushButton("Delete Mapping")
        enable_btn = QPushButton("Enable/Disable")

        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(enable_btn)
        button_layout.addStretch()

        # Mapping table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Source", "Destination", "Enabled", "Transformation", "Status"
        ])

        # Add layouts to main layout
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        # Connect signals
        add_btn.clicked.connect(self.add_mapping)
        edit_btn.clicked.connect(self.edit_mapping)
        delete_btn.clicked.connect(self.delete_mapping)
        enable_btn.clicked.connect(self.toggle_mapping)

        self.refresh_table()

    def add_mapping(self):
        dialog = MappingDialog(self.protocols, self)
        if dialog.exec_():
            source = DataPoint(
                dialog.source_protocol.currentText(),
                {"tag": dialog.source_tag.text()}
            )
            destination = DataPoint(
                dialog.dest_protocol.currentText(),
                {"tag": dialog.dest_tag.text()}
            )
            self.mapping_manager.add_mapping(source, destination)
            self.refresh_table()

    def edit_mapping(self):
        # TODO: Implement edit mapping functionality
        pass

    def delete_mapping(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.mapping_manager.remove_mapping(current_row)
            self.refresh_table()

    def toggle_mapping(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            mapping = self.mapping_manager.mappings[current_row]
            mapping["enabled"] = not mapping["enabled"]
            self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.mapping_manager.mappings))
        for i, mapping in enumerate(self.mapping_manager.mappings):
            self.table.setItem(i, 0, QTableWidgetItem(
                f"{mapping['source'].protocol}: {mapping['source'].tag['tag']}"
            ))
            self.table.setItem(i, 1, QTableWidgetItem(
                f"{mapping['destination'].protocol}: {mapping['destination'].tag['tag']}"
            ))
            self.table.setItem(i, 2, QTableWidgetItem(
                "Enabled" if mapping["enabled"] else "Disabled"
            ))
            self.table.setItem(i, 3, QTableWidgetItem(
                str(mapping["transformation"])
            ))
            self.table.setItem(i, 4, QTableWidgetItem("Active"))