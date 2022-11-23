import sys
import console_log_analysis_gui as console
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = console.ConsoleLogMainWindow()
    window.show()
sys.exit(app.exec_())

