from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                           QHBoxLayout, QPushButton, QComboBox,
                           QLabel, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
import logging
import datetime

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class LogsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_logger()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        # Log level filter
        self.level_combo = QComboBox()
        self.level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.level_combo.setCurrentText('INFO')
        self.level_combo.currentTextChanged.connect(self.change_log_level)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)

        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_logs)

        # Add controls to layout
        controls_layout.addWidget(QLabel("Log Level:"))
        controls_layout.addWidget(self.level_combo)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()

        # Log display
        self.log_widget = QTextEditLogger(self)
        self.log_widget.widget.setLineWrapMode(QTextEdit.NoWrap)

        # Add all to main layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.log_widget.widget)

    def setup_logger(self):
        self.logger = logging.getLogger('SCADA_Gateway')
        self.logger.setLevel(logging.INFO)
        
        # Add our custom handler
        self.log_widget.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(self.log_widget)

        # Start periodic logging of statistics
        self.start_stats_logging()

    def start_stats_logging(self):
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.log_statistics)
        self.stats_timer.start(5000)  # Log every 5 seconds

    def log_statistics(self):
        # TODO: Implement actual statistics gathering
        self.logger.info("Active connections: 5, Data points: 1250, Transfer rate: 100 pts/sec")

    def change_log_level(self, level):
        self.logger.setLevel(getattr(logging, level))

    def clear_logs(self):
        self.log_widget.widget.clear()

    def export_logs(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"scada_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_widget.widget.toPlainText())