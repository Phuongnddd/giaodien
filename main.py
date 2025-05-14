from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox,QPushButton, QVBoxLayout, QWidget, QStackedWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QColor
import sys
import MySQLdb as mdb
import resources_rc 
import cv2
import numpy as np
import requests

from login_window import Login_w
from register_window import Register_w
from home_window import Home_w
from control_window import Control_w
from camera_window import Camerasetting_w
from warning_window import Warning_w
from add_window import Add_w

app = QApplication(sys.argv)
widget = QStackedWidget()

Login_f = Login_w(widget)
Register_f = Register_w(widget)
Home_f = Home_w(widget)
Control_f = Control_w(widget)
Camerasetting_f = Camerasetting_w(widget)
Warning_f = Warning_w(widget)
Add_f = Add_w()

widget.addWidget(Login_f)  # 0
widget.addWidget(Register_f)  # 1
widget.addWidget(Home_f)  # 2
widget.addWidget(Camerasetting_f)  # 3
widget.addWidget(Control_f)  # 4
widget.addWidget(Warning_f)  # 5
widget.addWidget(Add_f)  # 6

widget.setCurrentIndex(0)
widget.showMaximized()
widget.show()
app.exec_()