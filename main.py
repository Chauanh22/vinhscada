import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.protocols import initialize_protocols
from core.security import SecurityManager

class ScadaGateway:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.security_manager = SecurityManager()
        self.protocols = initialize_protocols()
        self.main_window = MainWindow(self.protocols, self.security_manager)

    def run(self):
        self.main_window.show()
        return self.app.exec_()

if __name__ == "__main__":
    gateway = ScadaGateway()
    sys.exit(gateway.run())
