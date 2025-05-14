from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
import MySQLdb as mdb

class Register_w(QMainWindow):
    def __init__(self, widget):
        super(Register_w, self).__init__()
        uic.loadUi('dangky.ui', self)
        self.widget = widget
        self.B3.clicked.connect(self.register)

    def register(self):
        full_name = self.Name_r.text()
        username = self.Username_r.text()
        psw = self.Password_r1.text()
        confirm_psw = self.Password_r2.text()

        if psw != confirm_psw:
            QMessageBox.information(self, 'Register', 'Mật khẩu không trùng khớp')
            return

        db = mdb.connect('localhost', 'root', '', 'user_list')
        query = db.cursor()
        query.execute("SELECT * FROM user_list WHERE user=%s", (username,))
        if query.fetchone():
            QMessageBox.information(self, 'Register', 'Tài khoản đã tồn tại')
        else:
            query.execute("INSERT INTO user_list(full_name, user, pass) VALUES(%s, %s, %s)", (full_name, username, psw))
            db.commit()
            QMessageBox.information(self, 'Register', 'Đăng ký thành công')
            self.widget.setCurrentIndex(0)
        db.close()
