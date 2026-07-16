import sys
import os
from PySide6.QtWidgets import QApplication, QLabel

def main():
    app = QApplication(sys.argv)
    lbl = QLabel("Test GUI: If you see this window when launched from the agent, Qt is fine.")
    lbl.setWindowTitle("GUI Test")
    lbl.resize(480, 120)
    lbl.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())