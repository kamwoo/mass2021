#! /usr/bin/python3.8
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
from collections import deque
from Calculate import CalculateClass
import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
from math import *

class motor_thread(QThread):
    new_signal = pyqtSignal()

    def run(self):
        while True:
            time.sleep(.01)
            self.new_signal.emit()


class imu_thread(QThread):
    new_signal = pyqtSignal(float)
    imu = 0

    def imu_callback(self, data):
        self.imu = data.data

    def run(self):
        while True:
            time.sleep(.01)
            rospy.Subscriber('imu_list', Float32, self.imu_callback)
            self.new_signal.emit(0.1)


class gps_thread(QThread):
    new_signal = pyqtSignal(list)
    gps = []

    def gps_callback(self, data):
        self.gps = [data.data[0]*0.0000001, data.data[1]*0.0000001]

    def run(self):
        while True:
            time.sleep(.01)
            rospy.Subscriber('gps_list', Float32MultiArray, self.gps_callback)
            self.new_signal.emit(self.gps)


class myclass2(QThread):
    new_signal = pyqtSignal()

    def run(self):
        while True:
            time.sleep(.01)
            self.new_signal.emit()


class MyApp(QWidget):
    stadium_type = "A"
    draw_point_loc = []
    point_loc = []
    point_loc_earth = [[],[],[],[]]
    draw_point_loc_earth = []
    left_bottom_ok_button_valid = False
    right_bottom_ok_button_valid = False
    left_top_ok_button_valid = False
    right_bottom_ok_button_valid = False

    gps_li = deque([])
    gps_li_earth = deque([])
    imu_li = deque([])
    motor_li = deque([])

    is_motor_start = False

    def __init__(self):
        super().__init__()
        self.initUI()
        self.brush_size = 50
        self.brush_color = Qt.black
        self.pub = rospy.Publisher('motor_list', Float32MultiArray, queue_size = 1)
        rospy.init_node('main', anonymous = True)
        stackDataFileName = 'Alldata.txt'
        self.f = open(stackDataFileName, 'w')

    def initUI(self):
        self.setWindowTitle('MASS 2021')
        self.move(300, 300)
        self.resize(1500, 900)
        self.setup()

        self.myclass2 = myclass2()
        self.myclass2.new_signal.connect(self.point_table_update)
        self.myclass2.new_signal.connect(self.gps_table_update)
        self.myclass2.new_signal.connect(self.imu_table_update)
        self.myclass2.new_signal.connect(self.motor_table_update)
        self.myclass2.start()

        self.gps_thread = gps_thread()
        self.gps_thread.new_signal.connect(self.Ros_gps_response)
        self.gps_thread.start()

        self.imu_thread = imu_thread()
        self.imu_thread.new_signal.connect(self.Ros_imu_response)
        self.imu_thread.start()

        self.motor_thread = motor_thread()
        self.motor_thread.new_signal.connect(self.Motor_calculate_start)

        self.show()


    def setup(self):
        self.exit_button()
        self.thread_stop()
        self.reset_button()
        self.center()
        self.Stadium_type()
        self.location_input()
        self.stadium_location_label_first()
        self.set_point_table()
        self.set_gps_table()
        self.set_imu_table()
        self.set_motor_table()
        self.motor_calculate_start_button()
        self.start_button()
        self.stop_button()
        self.left_bottom_ok_button()
        self.right_bottom_ok_button()
        self.left_top_ok_button()
        self.right_top_ok_button()
        

    def set_point_table(self):
        self.point_table = QTableWidget(self)
        self.point_table.setGeometry(QRect(40, 400, 381, 361))
        self.point_table.setRowCount(20)
        self.point_table.setColumnCount(3)
        self.point_table.setHorizontalHeaderLabels(["     경기장 좌표계     ", "지구 좌표계", "확인"])
        self.point_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.point_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.point_table.resizeColumnsToContents()
        self.point_table.setFixedSize(500, 420)
    
    def set_gps_table(self):
        self.gps_table = QTableWidget(self)
        self.gps_table.setGeometry(QRect(870, 70, 540, 200))
        self.gps_table.setRowCount(10)
        self.gps_table.setColumnCount(2)
        self.gps_table.setHorizontalHeaderLabels(["     경기장 좌표계     ", "gps   현재 위치  지구 좌표계"])
        self.gps_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.gps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.gps_table.resizeColumnsToContents()
    
    def set_imu_table(self):
        self.imu_table = QTableWidget(self)
        self.imu_table.setGeometry(QRect(870, 280, 540, 200))
        self.imu_table.setRowCount(10)
        self.imu_table.setColumnCount(1)
        self.imu_table.setHorizontalHeaderLabels(["imu  Heading  Angle"])
        self.imu_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.imu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.imu_table.resizeColumnsToContents()
    
    def set_motor_table(self):
        self.motor_table = QTableWidget(self)
        self.motor_table.setGeometry(QRect(870, 500, 540, 150))
        self.motor_table.setRowCount(10)
        self.motor_table.setColumnCount(2)
        self.motor_table.setHorizontalHeaderLabels(["Left Motor", "Right Motor"])
        self.motor_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.motor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.motor_table.resizeColumnsToContents()

    def Motor_calculate_start(self):
        # 모터 리턴 받는 함수에 인자로 self.point_loc, gps_li_stadium, self.imu_angle
        # 모터 값 [L, R]로 리턴 받아서 self.motor_li에 추가
        # 모터 calculate버튼 클릭되면 calculate 객체 생성
        motor_value = self.CalculateClass.CalculateAllMethod(self.gps_li_stadium, self.imu_angle)
        # print(self.point_loc)
        # print(self.gps_li_stadium)
        # print(self.imu_angle)
        motor_value = [motor_value[0] + 90, motor_value[1] + 90]
        if len(self.motor_li) > 10:
            self.motor_li.popleft()

        # 모터값에 90 더하기
        self.motor_li.append(motor_value)

        if self.is_motor_start:
            # Ros To_arduino로 보내는 코드
            msg  = Float32MultiArray()
            msg.data = motor_value
            self.pub.publish(msg)


    def point_table_update(self):
        if len(self.point_loc) == 0:
            for i in range(20):
                for j in range(3):
                    self.point_table.setItem(i, j, QTableWidgetItem(str("")))
        else:
            for i in range(len(self.point_loc)):
                self.point_table.setItem(i, 0, QTableWidgetItem(str(self.point_loc[i])))
            for j in range(len(self.draw_point_loc_earth)):
                self.point_table.setItem(j, 1, QTableWidgetItem(str(self.draw_point_loc_earth[j])))
                


    def CalculateDistance (self, tempPoint1, tempPoint2):
        P1_latitude, P1_longitude, P2_latitude, P2_longitude = tempPoint1[1], tempPoint1[0], tempPoint2[1], tempPoint2[0]
        if (P1_latitude == P2_latitude) and (P1_longitude == P2_longitude):
            return 0

        e10 = P1_latitude * pi / 180
        e11 = P1_longitude * pi / 180
        e12 = P2_latitude * pi / 180
        e13 = P2_longitude * pi /180

        c16 = 6356752.314140910
        c15 = 6378137.000000000
        c17 = 0.0033528107
        f15 = c17 + c17 * c17
        f16 = f15 / 2
        f17 = c17 * c17 /2
        f18 = c17 * c17 /8
        f19 = c17 * c17 /16
        c18 = e13 - e11
        c20 = (1-c17) * tan(e10)
        c21 = atan(c20)
        c22 = sin(c21)
        c23 = cos(c21)
        c24 = (1 - c17) * tan(e12)
        c25 = atan(c24)
        c26 = sin(c25)
        c27 = cos(c25)
        c29 = c18
        c31 = (c27 * sin(c29) * c27 * sin(c29)) + (c23 * c26 - c22 *c27 * cos(c29))*\
                (c23 * c26 - c22 * c27 * cos(c29))
        c33 = (c22 * c26) + (c23 * c27 * cos(c29))
        c35 = sqrt(c31) / c33
        c36 = atan(c35)
        c38 = 0

        if c31 == 0:
            c38 = 0
        else :
            c38 = c23 * c27 * sin(c29) / sqrt(c31)

        c40 = 0

        if (cos(asin(c38)) * cos(asin(c38))) == 0:
            c40 = 0
        else:
            c40 = c33 -2 * c22 * c26 / (cos(asin(c38)) * cos(asin(c38)))

        c41 = cos(asin(c38)) * cos(asin(c38)) * (c15 * c15 - c16 * c16) / (c16* c16)
        c43 = 1 + c41 / 16384 * (4096 + c41 * (-768 + c41 * (320 - 175 * c41)))
        c45 = c41 / 1024 * (256 + c41 *(-128 + c41 * (74-47 * c41)))
        c47 = c45 * sqrt(c31) * (c40 + c45 / 4 * (c33 * (-1 + 2*c40*c40)- \
                c45 / 6*c40*(-3 + 4*c31)*(-3 +4 * c40 *c40)))
        c50 = c17 / 16 * cos(asin(c38))* cos(asin(c38)) * \
                (4+c17*(4-3*cos(asin(c38))*cos(asin(c38))))
        c52 = c18 + (1-c50)*c17 * c38 * (acos(c33) + c50 * sin(acos(c33)) * \
                (c40 + c50 * c33 * (-1+ 2*c40*c40)))
        c54 = c16 * c43 * (atan(c35) - c47)

        return c54
    
    
    def linear_equation_coefficient(self):
        self.bottom_a = (self.point_loc_earth[1][1] - self.point_loc_earth[0][1]) / (self.point_loc_earth[1][0] - self.point_loc_earth[0][0])
        self.bottom_b = -1
        self.bottom_c = self.point_loc_earth[0][1] - self.bottom_a * self.point_loc_earth[0][0]
        
        self.side_a = (self.point_loc_earth[2][1] - self.point_loc_earth[0][1]) / (self.point_loc_earth[2][0] - self.point_loc_earth[0][0])
        self.side_b = -1
        self.side_c = self.point_loc_earth[0][1] - self.side_a * self.point_loc_earth[0][0]

    def Ros_gps_response(self,li):
        if self.point_loc_earth[3]:
            bottom_foot_x = (self.bottom_b*(self.bottom_b*li[0] - self.bottom_a*li[1]) - self.bottom_a*self.bottom_c) / (self.bottom_a**2 + self.bottom_b**2)
            bottom_foot_y = (self.bottom_a*(-1*self.bottom_b*li[0] + self.bottom_a*li[1]) - self.bottom_b*self.bottom_c) / (self.bottom_a**2 + self.bottom_b**2)
            
            side_foot_x =  (self.side_b*(self.side_b*li[0] - self.side_a*li[1]) - self.side_a*self.side_c) / (self.side_a**2 + self.side_b**2)
            side_foot_y = (self.side_a*(-1*self.side_b*li[0] + self.side_a*li[1]) - self.side_b*self.side_c) / (self.side_a**2 + self.side_b**2)
            
            bottom_foot_point = [bottom_foot_x, bottom_foot_y]
            side_foot_point = [side_foot_x, side_foot_y]
            
            distance_point_x = self.CalculateDistance(self.point_loc_earth[0], bottom_foot_point)
            distance_point_y = self.CalculateDistance(self.point_loc_earth[0], side_foot_point)
            earth_bottom_distance = self.CalculateDistance(self.point_loc_earth[0], self.point_loc_earth[1])
            earth_side_distance = self.CalculateDistance(self.point_loc_earth[0], self.point_loc_earth[2])
            
            xRatio = distance_point_x / earth_bottom_distance
            yRatio = distance_point_y / earth_side_distance
            
            # because pixel
            if self.stadium_type == "test":
                x = (self.stadium_width / 4) * xRatio
                y = (self.stadium_height / 4) * yRatio
            else:
                x = (self.stadium_width / 2) * xRatio
                y = (self.stadium_height / 2) * yRatio

            if len(self.gps_li) > 10:
                self.gps_li.popleft()
            if len(self.gps_li_earth) > 10:
                self.gps_li_earth.popleft()
            self.gps_li_earth.append(li)
            self.gps_li.append([x,y])
            self.gps_li_stadium = [x,y]
            print(self.gps_li_stadium)
            
    
    def gps_table_update(self):
        if not self.point_loc_earth[3]:
            for i in range(10):
                for j in range(2):
                    self.gps_table.setItem(i, j, QTableWidgetItem(str("")))
        else:
            for i in range(len(self.gps_li)):
                self.gps_table.setItem(i, 0, QTableWidgetItem(str(self.gps_li[i])))
            for j in range(len(self.gps_li_earth)):
                self.gps_table.setItem(j, 1, QTableWidgetItem(str(self.gps_li_earth[j])))


    def Ros_imu_response(self, angle):
        if len(self.imu_li) > 10:
            self.imu_li.popleft()
        self.imu_li.append(angle)
        self.imu_angle = angle
    
    def imu_table_update(self):
        if len(self.imu_li) == 0:
            for i in range(10):
                for j in range(1):
                    self.imu_table.setItem(i, j, QTableWidgetItem(str("")))

        else:
            for i in range(len(self.imu_li)):
                self.imu_table.setItem(i, 0, QTableWidgetItem(str(self.imu_li[i])))
    
    def motor_table_update(self):
        if not self.motor_li:
            for i in range(10):
                for j in range(2):
                    self.motor_table.setItem(i, j, QTableWidgetItem(str("")))
        else:
            for i in range(len(self.motor_li)):
                self.motor_table.setItem(i, 0, QTableWidgetItem(str(self.motor_li[i][0])))
                self.motor_table.setItem(i, 1, QTableWidgetItem(str(self.motor_li[i][1])))
            


    def motor_calculate_start_button(self):
        btn = QPushButton('Calculate Start', self)
        btn.move(880, 700)
        btn.resize(150,80)
        btn.clicked.connect(self.motor_thread_start)

    def motor_thread_start(self):
        self.CalculateClass = CalculateClass(1, self.point_loc, self.f)
        self.motor_thread.start()
    
    def start_button(self):
        btn = QPushButton('Launch', self)
        btn.move(1070, 700)
        btn.resize(150,80)
        btn.clicked.connect(self.start_button_click)
    
    def start_button_click(self):
        self.is_motor_start = True
    
    def stop_button(self):
        btn = QPushButton('Stop', self)
        btn.move(1260, 700)
        btn.resize(150,80)
        btn.clicked.connect(self.stop_button_click)
    
    def stop_button_click(self):
        self.is_motor_start = False
        msg  = Float32MultiArray()
        msg.data = [90,90]
        self.pub.publish(msg)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def exit_button(self):
        btn = QPushButton('Quit', self)
        btn.move(1350, 10)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)
    
    def thread_stop(self):
        btn = QPushButton("Thread Stop", self)
        btn.move(1220, 10)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.thread_stop_logic)
    
    def thread_stop_logic(self):
        self.myclass2.terminate()
        self.myclass2.quit()
        self.gps_thread.terminate()
        self.gps_thread.quit()
        self.imu_thread.terminate()
        self.imu_thread.quit()
        self.motor_thread.terminate()
        self.motor_thread.quit()
        self.f.close()

    def reset_button(self):
        btn = QPushButton('reset', self)
        btn.move(420, 370)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.reset)
        btn.clicked.connect(self.point_table_update)
    
    def reset(self):
        self.point_loc = []
        self.draw_point_loc = []
        self.draw_point_loc_earth = []
    
    def Stadium_type(self):
        self.rbtn1 = QRadioButton('A 경기장 (35m,  10m)', self)
        self.rbtn1.move(90, 50)
        self.rbtn1.setChecked(True)
        self.rbtn1.clicked.connect(self.radioButtonClicked)

        self.rbtn2 = QRadioButton(self)
        self.rbtn2.move(90, 70)
        self.rbtn2.setText('B 경기장 (40m,  5m)')
        self.rbtn2.clicked.connect(self.radioButtonClicked)

        self.rbtn3 = QRadioButton(self)
        self.rbtn3.move(90, 90)
        self.rbtn3.setText('테스트 용 (15m,  5.6m)')
        self.rbtn3.clicked.connect(self.radioButtonClicked)


    def radioButtonClicked(self):
        if self.rbtn1.isChecked():
            self.stadium_type = "A"
            self.stadium_location_label()
        elif self.rbtn2.isChecked():
            self.stadium_type = "B"
            self.stadium_location_label()
        elif self.rbtn3.isChecked():
            self.stadium_type = "test"
            self.stadium_location_label()
        else:
            pass

        self.draw_point_loc = []
        QTabWidget.update(self)


# 경기장 모서리 좌표 입력
    def left_bottom_ok_button(self):
        btn = QPushButton('확인하기', self)
        btn.move(310, 175)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.left_bottom_save)

    
    def right_bottom_ok_button(self):
        btn = QPushButton('확인하기', self)
        btn.move(310, 225)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.right_bottom_save)
    
    def left_top_ok_button(self):
        btn = QPushButton('확인하기', self)
        btn.move(310, 275)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.left_top_save)
    
    def right_top_ok_button(self):
        btn = QPushButton('확인하기', self)
        btn.move(310, 325)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.right_top_save)
    
    def left_bottom_save(self):
        loc_li = list(map(float, self.left_bottom_li.split(",")))
        print(loc_li)
        self.point_loc_earth[0] = loc_li
    
    def right_bottom_save(self):
        loc_li = list(map(float, self.right_bottom_li.split(",")))
        print(loc_li)
        self.point_loc_earth[1] = loc_li
    
    def left_top_save(self):
        loc_li = list(map(float, self.left_top_li.split(",")))
        print(loc_li)
        self.point_loc_earth[2] = loc_li
    
    def right_top_save(self):
        loc_li = list(map(float, self.right_top_li.split(",")))
        print(loc_li)
        self.point_loc_earth[3] = loc_li
        print(self.point_loc_earth)
        self.linear_equation_coefficient()
        

    def location_input(self):
        lbl1 = QLabel("left bottom (x, y)",self)
        lbl1.move(90, 150)
        self.qle1 = QLineEdit(self)
        self.qle1.move(90, 180)
        self.qle1.textChanged[str].connect(self.left_botton_location_onChanged)

        lbl2 = QLabel("right bottom (x, y)",self)
        lbl2.move(90, 205)
        qle2 = QLineEdit(self)
        qle2.move(90, 230)
        qle2.textChanged[str].connect(self.right_botton_location_onChanged)

        lbl3 = QLabel("left top (x, y)",self)
        lbl3.move(90, 255)
        qle3 = QLineEdit(self)
        qle3.move(90, 280)
        qle3.textChanged[str].connect(self.left_top_location_onChanged)

        lbl4 = QLabel("right top (x, y)",self)
        lbl4.move(90, 305)
        qle4 = QLineEdit(self)
        qle4.move(90, 330)
        qle4.textChanged[str].connect(self.right_top_location_onChanged)
    

    def left_botton_location_onChanged(self, text):
        self.left_bottom_li = "".join(list(text))
        

    def right_botton_location_onChanged(self, text):
        self.right_bottom_li = "".join(list(text))
        
    
    def left_top_location_onChanged(self, text):
        self.left_top_li = "".join(list(text))
        
    
    def right_top_location_onChanged(self, text):
        self.right_top_li = "".join(list(text))


    def stadium_location_label_first(self):
        stadium_lbl1 = QLabel("Stadium", self)
        stadium_lbl1.move(230, 150)

        self.stadium_loc1 = QLabel("(0,  0)", self)
        self.stadium_loc1.move(230, 180)
        self.stadium_loc2 = QLabel("(100,  0)", self)
        self.stadium_loc2.move(230, 230)
        self.stadium_loc3 = QLabel("(0,  350)", self)
        self.stadium_loc3.move(230, 280)
        self.stadium_loc_test = QLabel("(100,  350)", self)
        self.stadium_loc_test.move(230, 330)

    def stadium_location_label(self):
        if self.stadium_type == "A":
            self.stadium_loc_test.move(230, 330)
            self.stadium_loc1.setText("(0,  0)")
            self.stadium_loc2.setText("(100,  0)")
            self.stadium_loc3.setText("(0,  350)")
            self.stadium_loc_test.setText("(100,  350)")

        elif self.stadium_type == "B":
            self.stadium_loc1.setText("(0,  0)")
            self.stadium_loc2.setText("(50,  0)")
            self.stadium_loc3.setText("(0,  400)")
            self.stadium_loc_test.setText("(50,  400)")

        elif self.stadium_type == "test":
            self.stadium_loc1.setText("(0,  0)")
            self.stadium_loc2.setText("(56,  0)")
            self.stadium_loc3.setText("(0,  150)")
            self.stadium_loc_test.setText("(56,  150)")

        else: 
            pass
        

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        self.draw_rect(qp)
        self.drawPoints(e,qp)
        self.drawPointsInCircle(e,qp)
        qp.end()


    def drawPointsInCircle(self, event, qpsInCircle):
        pen = QPen(Qt.red, 3)
        qpsInCircle.setBrush(QColor(255,0,0))
        qpsInCircle.setPen(pen)
        
        for i in range(len(self.draw_point_loc)):
            x = self.draw_point_loc[i][0]
            y = self.draw_point_loc[i][1]
            qpsInCircle.drawEllipse(x-1, y-1, 2, 2) # 경기장 크기에 맞기 2m 계산
            self.update()

    def drawPoints(self, event, qp_point):
        pen = QPen(Qt.red, 3)
        qp_point.setBrush(QColor(255,255,255,0))
        qp_point.setPen(pen)
        
        for i in range(len(self.draw_point_loc)):
            x = self.draw_point_loc[i][0]
            y = self.draw_point_loc[i][1]
            qp_point.drawEllipse(x-20, y-20, 40, 40) # 경기장 크기에 맞기 2m 계산
            self.update()
    

    def draw_rect(self, qp):
        qp.setBrush(QColor(149,208,240))
        qp.setPen(QPen(QColor(0, 0, 0), 3))

        if self.stadium_type == "A":
            self.stadium_width = 100 * 2
            self.stadium_height = 350 * 2
            self.stadium_x = 500 + self.stadium_width/2
            self.stadium_y = 50
            qp.drawRect(self.stadium_x, self.stadium_y, self.stadium_width, self.stadium_height)

        elif self.stadium_type == "B":
            self.stadium_width = 50 * 2
            self.stadium_height = 400 * 2
            self.stadium_x = 500 + self.stadium_width * 3/2
            self.stadium_y = 50 - 30
            qp.drawRect(self.stadium_x, self.stadium_y, self.stadium_width, self.stadium_height)

        elif self.stadium_type == "test":
            self.stadium_width = 56 * 4
            self.stadium_height = 150 * 4
            self.stadium_x = 480 + self.stadium_width/2
            self.stadium_y = 100
            qp.drawRect(self.stadium_x, self.stadium_y, self.stadium_width, self.stadium_height)
        else:
            self.stadium_width = 100 * 2
            self.stadium_height = 350 * 2
            self.stadium_x = 500 + self.stadium_width/2
            self.stadium_y = 50
            qp.drawRect(self.stadium_x + self.stadium_width/2, self.stadium_y, self.stadium_width, self.stadium_height)


    def get_mouse_position(self):
        self.setMouseTracking(False)
    

    def mousePressEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            x = e.x()
            y = e.y()
            self.point_print(x,y)
            


    def point_print(self, x, y):
        if x > self.stadium_x and x < self.stadium_x + self.stadium_width:
            if y > self.stadium_y and y < self.stadium_y + self.stadium_height:
                self.draw_point_loc.append([x,y])
                
                if self.stadium_type == "A":
                    x = (x - self.stadium_x) / 2
                    y = abs((y - self.stadium_y) / 2 - 350)

                    if len(self.point_loc_earth[0]) > 0 and len(self.point_loc_earth[1]) > 0 and len(self.point_loc_earth[2]) > 0 and len(self.point_loc_earth[3]) > 0:
                        x_ratio = x / (self.stadium_width /2)
                        x_ti = abs(self.point_loc_earth[1][0] - self.point_loc_earth[0][0]) * x_ratio
                        x_fi = self.point_loc_earth[0][0] + x_ti

                        y_ratio = y / (self.stadium_height /2)
                        y_ti = abs(self.point_loc_earth[0][1] - self.point_loc_earth[2][1]) * y_ratio
                        y_fi = self.point_loc_earth[0][1] + y_ti

                        self.draw_point_loc_earth.append([x_fi, y_fi])

                elif self.stadium_type == "B":
                    x = (x - self.stadium_x) / 2
                    y = abs((y - self.stadium_y) / 2 - 400)

                    if len(self.point_loc_earth[0]) > 0 and len(self.point_loc_earth[1]) > 0 and len(self.point_loc_earth[2]) > 0 and len(self.point_loc_earth[3]) > 0:
                        x_ratio = x / (self.stadium_width /2)
                        x_ti = abs(self.point_loc_earth[1][0] - self.point_loc_earth[0][0]) * x_ratio
                        x_fi = self.point_loc_earth[0][0] + x_ti

                        y_ratio = y / (self.stadium_height /2)
                        y_ti = abs(self.point_loc_earth[0][1] - self.point_loc_earth[2][1]) * y_ratio
                        y_fi = self.point_loc_earth[0][1] + y_ti

                        self.draw_point_loc_earth.append([x_fi, y_fi])

                elif self.stadium_type == "test":
                    x = (x - self.stadium_x) / 4
                    y = abs((y - self.stadium_y) / 4 - 150)

                    if len(self.point_loc_earth[0]) > 0 and len(self.point_loc_earth[1]) > 0 and len(self.point_loc_earth[2]) > 0 and len(self.point_loc_earth[3]) > 0:
                        x_ratio = x / (self.stadium_width /4)
                        x_ti = abs(self.point_loc_earth[1][0] - self.point_loc_earth[0][0]) * x_ratio
                        x_fi = self.point_loc_earth[0][0] + x_ti

                        y_ratio = y / (self.stadium_height /4)
                        y_ti = abs(self.point_loc_earth[0][1] - self.point_loc_earth[2][1]) * y_ratio
                        y_fi = self.point_loc_earth[0][1] + y_ti

                        self.draw_point_loc_earth.append([x_fi, y_fi])

                else:
                    x = (x - self.stadium_x) / 2
                    y = abs((y - self.stadium_y) / 2 - 350)

                    if len(self.point_loc_earth[0]) > 0 and len(self.point_loc_earth[1]) > 0 and len(self.point_loc_earth[2]) > 0 and len(self.point_loc_earth[3]) > 0:
                        x_ratio = x / (self.stadium_width /2)
                        x_ti = abs(self.point_loc_earth[1][0] - self.point_loc_earth[0][0]) * x_ratio
                        x_fi = self.point_loc_earth[0][0] + x_ti

                        y_ratio = y / (self.stadium_height /2)
                        y_ti = abs(self.point_loc_earth[0][1] - self.point_loc_earth[2][1]) * y_ratio
                        y_fi = self.point_loc_earth[0][1] + y_ti

                        self.draw_point_loc_earth.append([x_fi, y_fi])

                self.point_loc.append([x,y])
                self.update()
                print(self.draw_point_loc)


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())
