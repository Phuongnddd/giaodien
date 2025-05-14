from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
import MySQLdb as mdb

class Login_w(QMainWindow):
    def __init__(self, widget):
        super(Login_w, self).__init__()
        uic.loadUi('dangnhap.ui', self)
        self.widget = widget
        self.B1.clicked.connect(self.login)
        self.B2.clicked.connect(self.register_form)

    def register_form(self):
        self.widget.setCurrentIndex(1)

    def login(self):
        username = self.user.text()
        psw = self.pw.text()
        db = mdb.connect('localhost', 'root', '', 'user_list')
        query = db.cursor()
        query.execute("SELECT * FROM user_list WHERE user=%s AND pass=%s", (username, psw))
        result = query.fetchone()
        if result:
            QMessageBox.information(self, 'Login', 'Login success')
            self.widget.setCurrentIndex(2)
        else:
            QMessageBox.information(self, 'Login', 'Login failed')
        db.close()