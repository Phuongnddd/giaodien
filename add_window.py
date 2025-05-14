from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

class Add_w(QWidget):
    def __init__(self, parent=None):
        super(Add_w, self).__init__(parent)
        uic.loadUi('them.ui', self)
        self.back_h.clicked.connect(self.close_window)

    def close_window(self):
        self.hide()
