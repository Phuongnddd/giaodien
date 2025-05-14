# warning_window.py
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic, QtCore
from add_window import Add_w

class Warning_w(QMainWindow):
    def __init__(self, widget):
        super(Warning_w, self).__init__()
        uic.loadUi('gioithieu.ui', self)
        self.widget = widget
        self.user_window = None
        self.homebtn_g.clicked.connect(self.home_form)
        self.settingbtn_g.clicked.connect(self.setting_form)
        self.controlbtn_g.clicked.connect(self.control_form)
        self.gioithieubtn_g.clicked.connect(self.Warning_form)
        self.them_w.clicked.connect(self.show_user_window)

    def home_form(self):
        self.widget.setCurrentIndex(2)

    def setting_form(self):
        self.widget.setCurrentIndex(3)

    def control_form(self):
        self.widget.setCurrentIndex(4)

    def Warning_form(self):
        self.widget.setCurrentIndex(5)

    def show_user_window(self):
        if self.user_window is None:
            self.user_window = Add_w(self)
        if self.user_window.isVisible():
            self.user_window.hide()
        else:
            pos = self.them_w.mapToGlobal(QtCore.QPoint(-150, self.them_w.height()))
            self.user_window.move(pos)
            self.user_window.show()