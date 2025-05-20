from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, 
                           QVBoxLayout, QStatusBar)
from .connection_tab import ConnectionTab
from .mapping_tab import MappingTab
from .logs_tab import LogsTab

class MainWindow(QMainWindow):
    def __init__(self, protocols, security_manager, parent=None):
        super().__init__(parent)
        self.protocols = protocols
        self.security_manager = security_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SCADA Data Gateway')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()
        
        # Add tabs
        self.connection_tab = ConnectionTab(self.protocols)
        self.mapping_tab = MappingTab(self.protocols)
        self.logs_tab = LogsTab()

        tabs.addTab(self.connection_tab, "Connections")
        tabs.addTab(self.mapping_tab, "Mappings")
        tabs.addTab(self.logs_tab, "Logs")

        layout.addWidget(tabs)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Set up menu bar
        self.setup_menu()

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        # Add menu actions here
        
        # Settings menu
        settings_menu = menubar.addMenu('&Settings')
        # Add settings actions here
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        # Add help actions here