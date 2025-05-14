from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import requests
import cv2
import numpy as np
from add_window import Add_w

class Camerasetting_w(QMainWindow):
    def __init__(self, widget):
        super(Camerasetting_w, self).__init__()
        uic.loadUi('camerasetting.ui', self)
        self.widget = widget
        self.user_window = None
        self.homebtn_c.clicked.connect(self.home_form)
        self.settingbtn_c.clicked.connect(self.setting_form)
        self.controlbtn_c.clicked.connect(self.control_form)
        self.gioithieubtn_c.clicked.connect(self.Warning_form)
        self.them_s.clicked.connect(self.show_user_window)
        self.on.clicked.connect(self.start_camera)
        self.off.clicked.connect(self.stop_camera)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.stream_url = "http://192.168.0.101/cam-hi.jpg"
        self.running = False

    def home_form(self):
        self.widget.setCurrentIndex(2)

    def setting_form(self):
        self.widget.setCurrentIndex(3)

    def control_form(self):
        self.widget.setCurrentIndex(4)

    def Warning_form(self):
        self.widget.setCurrentIndex(5)

    def check_camera_connection(self):
        try:
            response = requests.get(self.stream_url, timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def start_camera(self):
        if not self.running:
            if not self.check_camera_connection():
                QMessageBox.critical(self, "Camera Error", "Không thể kết nối đến camera ESP32!")
                return
            self.running = True
            self.timer.start(100)

    def stop_camera(self):
        self.running = False
        self.timer.stop()
        self.khungcam.clear()

    def update_frame(self):
        if self.running:
            try:
                response = requests.get(self.stream_url, timeout=2)
                if response.status_code == 200:
                    img_array = np.frombuffer(response.content, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if frame is not None:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = frame.shape
                        bytes_per_line = ch * w
                        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        self.khungcam.setPixmap(QPixmap.fromImage(q_img))
            except Exception as e:
                print(f"Lỗi khi tải ảnh: {e}")

    def show_user_window(self):
        if self.user_window is None:
            self.user_window = Add_w(self)
        if self.user_window.isVisible():
            self.user_window.hide()
        else:
            pos = self.them_s.mapToGlobal(QtCore.QPoint(-150, self.them_s.height()))
            self.user_window.move(pos)
            self.user_window.show()