import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QSlider, QLabel, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLineEdit, QGroupBox, QSplitter, QFrame, QGridLayout,
                            QMessageBox, QSpinBox, QDoubleSpinBox, QComboBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import serial
import time
import serial.tools.list_ports
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic, QtCore
from add_window import Add_w
class ArduinoConnection:
    def __init__(self, parent=None):
        self.parent = parent
        self.serial_port = None
        self.connected = False
        
    def get_available_ports(self):
        """Lấy danh sách các cổng COM có sẵn"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports
        
    def connect(self, port, baud_rate=9600):
        """Kết nối với Arduino thông qua cổng COM đã chọn"""
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)  # Đợi Arduino khởi động lại
            self.connected = True
            return True
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Ngắt kết nối với Arduino"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.connected = False
            return True
        return False
        
    def send_command(self, command):
        """Gửi lệnh đến Arduino"""
        if not self.connected or not self.serial_port:
            return False, "Không có kết nối!"
            
        try:
            self.serial_port.write(f"{command}\n".encode())
            # Đợi và đọc phản hồi nếu có
            time.sleep(0.1)
            if self.serial_port.in_waiting:
                response = self.serial_port.readline().decode().strip()
                return True, response
            return True, "Đã gửi lệnh"
        except Exception as e:
            return False, f"Lỗi khi gửi lệnh: {e}"

#Thanh trượt hiện đại
# Thanh trượt hiện đại
class ModernSlider(QWidget):
    def __init__(self, title, min_val, max_val, initial_val=0, unit="", parent=None):
        super().__init__(parent)

        # Giới hạn chiều rộng tối đa
        self.setMaximumWidth(200)

        # Layout chính
        self.outer_layout = QHBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setAlignment(Qt.AlignCenter)  # Căn giữa slider trong widget

        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)

        # Header chứa tên + giá trị
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.value_label = QLabel(f"{initial_val} {unit}")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.value_label)
        self.inner_layout.addLayout(header_layout)

        # Thanh trượt
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(initial_val)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A86E8, stop:1 #5C9AFF);
                border: 1px solid #5c9aff;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        self.inner_layout.addWidget(self.slider)

        self.unit = unit
        self.slider.valueChanged.connect(self._update_value_label)

        # Thêm vào layout chính
        self.outer_layout.addWidget(self.inner_widget)

    def _update_value_label(self, value):
        self.value_label.setText(f"{value} {self.unit}")
    
    def value(self):
        return self.slider.value()
    
    def setValue(self, value):
        self.slider.setValue(value)

#Vùng vẽ robot
class SCARARobotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes.set_facecolor('#FFFFFF')
        self.axes.grid(True, linestyle='--', alpha=0.7)

    def draw_robot(self, joint_coords, z, reach_min, reach_max, in_range=True):
        self.axes.clear()
        x0, y0, z0 = 0, 0, z  # Gốc robot dịch theo Z
        x1, y1 = joint_coords[0]
        x2, y2 = joint_coords[1]

        # Trục Z cố định tại (0,0) từ 0 đến 60
        self.axes.plot([0, 0], [0, 0], [0, 4], 'k-', linewidth=4)

        # Tay đế (Base -> Elbow), di chuyển theo z
        self.axes.plot([x0, x1], [y0, y1], [z, z], 'r-', linewidth=4)

        # Tay nối (Elbow -> End-effector), di chuyển theo z
        self.axes.plot([x1, x2], [y1, y2], [z, z], 'g-', linewidth=4)

        # Các khớp robot
        self.axes.scatter([x0, x1, x2], [y0, y1, y2], [z, z, z], 
                        color=['blue', 'green', 'red' if not in_range else 'black'], s=60)

        self.axes.set_xlim(-40, 40)
        self.axes.set_ylim(-40, 40)
        self.axes.set_zlim(0, 40)
        self.axes.set_xlabel("X (cm)")
        self.axes.set_ylabel("Y (cm)")
        self.axes.set_zlabel("Z (cm)")
        self.axes.view_init(elev=30, azim=135)
        self.draw()

class ConnectionWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Kết nối Arduino", parent)
        self.arduino = ArduinoConnection(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Combo box để chọn cổng
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Cổng COM:"))
        self.port_combo = QComboBox()
        self.refresh_ports()
        port_layout.addWidget(self.port_combo)

        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_btn)
        layout.addLayout(port_layout)

        # Nút kết nối/ngắt kết nối
        self.connect_btn = QPushButton("Kết nối")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)

        # Trạng thái kết nối
        self.status_label = QLabel("Trạng thái: Chưa kết nối")
        layout.addWidget(self.status_label)

       
    def refresh_ports(self):
        """Làm mới danh sách cổng COM"""
        self.port_combo.clear()
        ports = self.arduino.get_available_ports()
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItem("Không tìm thấy cổng")

    def toggle_connection(self):
        """Kết nối hoặc ngắt kết nối Arduino"""
        if not self.arduino.connected:
            port = self.port_combo.currentText()
            if port and port != "Không tìm thấy cổng":
                if self.arduino.connect(port):
                    self.status_label.setText("Trạng thái: Đã kết nối")
                    self.connect_btn.setText("Ngắt kết nối")
                    QMessageBox.information(self, "Kết nối", f"Đã kết nối thành công với {port}")
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể kết nối với {port}")
            else:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn cổng COM hợp lệ")
        else:
            if self.arduino.disconnect():
                self.status_label.setText("Trạng thái: Đã ngắt kết nối")
                self.connect_btn.setText("Kết nối")

    def send_command(self, command):
        """Gửi lệnh đến Arduino và hiển thị kết quả"""
        if not self.arduino.connected:
            QMessageBox.warning(self, "Lỗi", "Chưa kết nối với Arduino")
            return False

        success, response = self.arduino.send_command(command)
        if not success:
            QMessageBox.warning(self, "Lỗi", response)
        return success
class Control_w(QMainWindow):
    def __init__(self, widget):
        super(Control_w, self).__init__()
        uic.loadUi('controll.ui', self)
        self.widget = widget
        self.user_window = None
        self.homebtn_co.clicked.connect(self.home_form)
        self.settingbtn_co.clicked.connect(self.setting_form)
        self.controlbtn_co.clicked.connect(self.control_form)
        self.gioithieubtn_co.clicked.connect(self.Warning_form)
        self.them_c.clicked.connect(self.show_user_window)
        self.widget_6 = self.findChild(QWidget, "widget_6")  # hoặc QFrame

        self.setup_robot_parameters()
        self.init_ui()

    def setup_robot_parameters(self):
        self.L1 = 17
        self.L2 = 13
        self.PPR1 = 64000
        self.PPR2 = 2400
        self.offset1 = 0
        self.offset2 = -122
        self.max2 = 156
        self.range2_deg = self.max2 - self.offset2
        self.max_p2 = self.range2_deg * (self.PPR2 / 360)
        self.reach_max = self.L1 + self.L2
        self.reach_min = abs(self.L1 - self.L2)
        self.Z_MAX_CM = 22
        self.Z_MAX_PULSE = 22000
        self.Z_PULSE_PER_CM = self.Z_MAX_PULSE / self.Z_MAX_CM  # = 1000

        self.robot_canvas = SCARARobotCanvas(self)
        self.widget_6 = self.findChild(QWidget, "widget_6") 

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.robot_canvas)
        self.widget_6.setLayout(layout)  # Cập nhật lại layout rõ ràng

         # Vẽ robot ban đầu để tránh vùng trắng


    def init_ui(self):
        self.widget_5 = self.findChild(QWidget, "widget_5")  # Chứa toàn bộ giao diện điều khiển

        # --- Layout chính chia trái (nút) / phải (robot canvas) ---
        main_layout = QHBoxLayout()
        self.widget_5.setLayout(main_layout)

        # === PANEL TRÁI ===
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel, 3)  # Tỉ lệ 3 phần
        

        # === SLIDER điều khiển các khớp ===
        self.slider1 = ModernSlider("Joint 1 (Base)", 0, int(self.PPR1 * 180 / 360), 0, "pulses")
        self.slider2 = ModernSlider("Joint 2 (Elbow)", 0, int(self.max_p2), 0, "pulses")
        self.slider_z = ModernSlider("Joint 3 (Z)", 0, int(self.Z_MAX_PULSE), 0, "pulses")
        self.slider1.slider.valueChanged.connect(self.update_plot)
        self.slider2.slider.valueChanged.connect(self.update_plot)
        self.slider_z.slider.valueChanged.connect(self.update_plot)

        left_layout.addWidget(self.slider1)
        left_layout.addWidget(self.slider2)
        left_layout.addWidget(self.slider_z)

        # === Hiển thị tọa độ và góc ===
        self.angle_display = QLabel("θ1 = 0.0°, θ2 = 0.0°")
        self.angle_display.setAlignment(Qt.AlignCenter)
        self.position_display = QLabel("X = 0.00 cm, Y = 0.00 cm, Z = 0.00 cm")
        self.position_display.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.angle_display)
        left_layout.addWidget(self.position_display)

        # === Nhập tọa độ X, Y và nút tính toán ===
        self.x_input = QDoubleSpinBox(); self.x_input.setRange(-40, 40); self.x_input.setDecimals(2)
        self.y_input = QDoubleSpinBox(); self.y_input.setRange(-40, 40); self.y_input.setDecimals(2)
        self.compute_button = QPushButton("Move to Position")
        self.compute_button.clicked.connect(self.inverse_kinematics)

        pos_group = QGroupBox("Position Control")
        pos_layout = QGridLayout()
        pos_layout.addWidget(QLabel("X:"), 0, 0)
        pos_layout.addWidget(self.x_input, 0, 1)
        pos_layout.addWidget(QLabel("Y:"), 0, 2)
        pos_layout.addWidget(self.y_input, 0, 3)
        pos_layout.addWidget(self.compute_button, 1, 0, 1, 4)
        pos_group.setLayout(pos_layout)
        left_layout.addWidget(pos_group)

        # === Nhập góc trực tiếp θ1, θ2 ===
        self.theta1_input = QDoubleSpinBox(); self.theta1_input.setRange(-180, 180)
        self.theta2_input = QDoubleSpinBox(); self.theta2_input.setRange(-180, 180)
        self.set_angle_button = QPushButton("Set Angles")
        self.set_angle_button.clicked.connect(self.set_joint_angles)

        angle_group = QGroupBox("Angle Input")
        angle_layout = QGridLayout()
        angle_layout.addWidget(QLabel("θ1 (°):"), 0, 0)
        angle_layout.addWidget(self.theta1_input, 0, 1)
        angle_layout.addWidget(QLabel("θ2 (°):"), 0, 2)
        angle_layout.addWidget(self.theta2_input, 0, 3)
        angle_layout.addWidget(self.set_angle_button, 1, 0, 1, 4)
        angle_group.setLayout(angle_layout)
        left_layout.addWidget(angle_group)

        # === Nhóm nút điều khiển Arduino ===
        arduino_group = QGroupBox("Arduino Control")
        arduino_layout = QGridLayout()

        self.send_pos_button = QPushButton("Gửi vị trí đến Arduino")
        self.send_pos_button.clicked.connect(self.send_position_to_arduino)
        arduino_layout.addWidget(self.send_pos_button, 0, 0, 1, 2)

        self.grab_button = QPushButton("Gắp vật (GRAB)")
        self.grab_button.clicked.connect(self.send_grab_command)
        arduino_layout.addWidget(self.grab_button, 1, 0)

        self.release_button = QPushButton("Nhả vật (RELEASE)")
        self.release_button.clicked.connect(self.send_release_command)
        arduino_layout.addWidget(self.release_button, 1, 1)

        self.home_button = QPushButton("Về vị trí gốc (HOME)")
        self.home_button.clicked.connect(self.send_home_command)
        arduino_layout.addWidget(self.home_button, 2, 0, 1, 2)

        arduino_group.setLayout(arduino_layout)
        left_layout.addWidget(arduino_group)

        # Nút reset
        self.reset_button = QPushButton("Reset Position")
        self.reset_button.clicked.connect(self.reset_position)
        left_layout.addWidget(self.reset_button)

        left_layout.addStretch()

        self.connection_widget = ConnectionWidget(self)
        left_layout.addWidget(self.connection_widget)

        # === PANEL PHẢI: Robot Canvas ===
        main_layout.addWidget(self.robot_canvas, 7)

        # Cập nhật lần đầu
        self.update_plot()


        

    def update_plot(self):
        p1 = self.slider1.value()
        p2 = self.slider2.value()
        z = (0.001*self.slider_z.value() / self.Z_MAX_CM) * 4
        z_real = self.slider_z.value()/self.Z_MAX_CM *0.001*22
        theta1 = np.deg2rad(self.offset1 + p1 * (360 / self.PPR1))
        theta2 = np.deg2rad(self.offset2 + p2 * (360 / self.PPR2))
        x1 = self.L1 * np.cos(theta1)
        y1 = self.L1 * np.sin(theta1)
        x2 = x1 + self.L2 * np.cos(theta1 + theta2)
        y2 = y1 + self.L2 * np.sin(theta1 + theta2)

        d = np.hypot(x2, y2)
        in_range = self.reach_min <= d <= self.reach_max
        self.robot_canvas.draw_robot([(x1, y1), (x2, y2)], z, self.reach_min, self.reach_max, in_range)

        self.angle_display.setText(f"θ1 = {np.rad2deg(theta1):.1f}°, θ2 = {np.rad2deg(theta2):.1f}°")
        self.position_display.setText(f"X = {x2:.2f} cm, Y = {y2:.2f} cm, Z = {z_real:.2f} cm")
        self.x_input.setValue(round(x2, 2))
        self.y_input.setValue(round(y2, 2))

    def inverse_kinematics(self):
        x = self.x_input.value()
        y = self.y_input.value()
        d = np.hypot(x, y)
        if d < self.reach_min or d > self.reach_max:
            QMessageBox.warning(self, "Out of Reach", "Target out of reach!")
            return
        cos_t2 = (x**2 + y**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        cos_t2 = np.clip(cos_t2, -1.0, 1.0)
        sin_t2 = np.sqrt(max(0, 1 - cos_t2**2))
        t2 = np.arctan2(sin_t2, cos_t2)
        k1 = self.L1 + self.L2 * cos_t2
        k2 = self.L2 * sin_t2
        t1 = np.arctan2(y, x) - np.arctan2(k2, k1)
        p1 = (np.rad2deg(t1) - self.offset1) * self.PPR1 / 360
        p2 = (np.rad2deg(t2) - self.offset2) * self.PPR2 / 360
        self.slider1.setValue(int(np.clip(p1, 0, self.PPR1 * 180 / 360)))
        self.slider2.setValue(int(np.clip(p2, 0, self.max_p2)))
        self.update_plot()
    def set_joint_angles(self):
        theta1_deg = self.theta1_input.value()
        theta2_deg = self.theta2_input.value()
        p1 = (theta1_deg - self.offset1) * self.PPR1 / 360
        p2 = (theta2_deg - self.offset2) * self.PPR2 / 360
        self.slider1.setValue(int(np.clip(p1, 0, self.PPR1 * 180 / 360)))
        self.slider2.setValue(int(np.clip(p2, 0, self.max_p2)))
        self.update_plot()

    def send_position_to_arduino(self):
        x_pos = int(self.x_input.value() * 1000)
        y_pos = int(self.y_input.value() * -100)
        z_cm = int(self.slider_z.value() * 0.001)
        z_pos = int(z_cm * self.Z_PULSE_PER_CM) 
        command = f"MOVE {x_pos} {y_pos} {z_pos}"
        if hasattr(self, 'connection_widget') and self.connection_widget.send_command(command):
            QMessageBox.information(self, "Thành công", f"Đã gửi lệnh: {command}")
    def reset_position(self):
        self.slider1.setValue(0)
        self.slider2.setValue(0)
        self.slider_z.setValue(0)
        self.update_plot()
    def send_grab_command(self):
        """Gửi lệnh gắp vật (bật nam châm)"""
        if self.connection_widget.send_command("GRAB"):
            QMessageBox.information(self, "Thành công", "Đã gửi lệnh GRAB")
        
    def send_release_command(self):
        """Gửi lệnh nhả vật (tắt nam châm)"""
        if self.connection_widget.send_command("RELEASE"):
            QMessageBox.information(self, "Thành công", "Đã gửi lệnh RELEASE")
            
    def send_home_command(self):
        """Gửi lệnh quay về vị trí gốc"""
        if self.connection_widget.send_command("HOME"):
            QMessageBox.information(self, "Thành công", "Đã gửi lệnh HOME")
        

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
            pos = self.them_c.mapToGlobal(QtCore.QPoint(-150, self.them_c.height()))
            self.user_window.move(pos)
            self.user_window.show()
