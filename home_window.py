from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic, QtCore
from add_window import Add_w

class Home_w(QMainWindow):
    def __init__(self, widget):
        super(Home_w, self).__init__()
        uic.loadUi('home.ui', self)
        self.widget = widget
        self.user_window = None
        self.homebtn_h.clicked.connect(self.control_form)
        self.settingbtn_h.clicked.connect(self.setting_form)
        self.controlbtn_h.clicked.connect(self.home_form)
        self.gioithieubtn_h.clicked.connect(self.Warning_form)
        self.them_h.clicked.connect(self.show_user_window)

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
            pos = self.them_h.mapToGlobal(QtCore.QPoint(-150, self.them_h.height()))
            self.user_window.move(pos)
            self.user_window.show()