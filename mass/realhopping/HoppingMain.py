import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
from collections import deque

class imu_thread(QThread):
    new_signal = pyqtSignal(float)

    def run(self):
        while True:
            time.sleep(.1)
            self.new_signal.emit(1.0)


class gps_thread(QThread):
    new_signal = pyqtSignal(list)

    def run(self):
        while True:
            time.sleep(.1)
            self.new_signal.emit([1.0, 2.0])


class myclass2(QThread):
    new_signal = pyqtSignal()

    def run(self):
        while True:
            time.sleep(.1)
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
    motor_li = []

    def __init__(self):
        super().__init__()
        self.initUI()
        self.brush_size = 50
        self.brush_color = Qt.black

    def initUI(self):
        self.setWindowTitle('MASS 2021')
        self.move(300, 300)
        self.resize(1500, 900)
        self.setup()

        self.myclass2 = myclass2()
        self.myclass2.new_signal.connect(self.point_table_update)
        self.myclass2.new_signal.connect(self.gps_table_update)
        self.myclass2.new_signal.connect(self.imu_table_update)
        self.myclass2.start()

        self.gps_thread = gps_thread()
        self.gps_thread.new_signal.connect(self.Ros_gps_response)
        self.gps_thread.start()

        self.imu_thread = imu_thread()
        self.imu_thread.new_signal.connect(self.Ros_imu_response)
        self.imu_thread.start()

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


    def Ros_gps_response(self, li):
        if self.point_loc_earth[3]:
            x_ratio = abs(li[0] - self.point_loc_earth[0][0]) / abs(self.point_loc_earth[1][0] - self.point_loc_earth[0][0])
            y_ratio = abs(li[1] - self.point_loc_earth[0][1]) / abs(self.point_loc_earth[2][1] - self.point_loc_earth[0][1])
            # because pixel
            if self.stadium_type == "test":
                x = (self.stadium_width / 4) * x_ratio
                y = (self.stadium_height / 4) * y_ratio
            else:
                x = (self.stadium_width / 2) * x_ratio
                y = (self.stadium_height / 2) * y_ratio

            if len(self.gps_li) > 10:
                self.gps_li.popleft()
            if len(self.gps_li_earth) > 10:
                self.gps_li_earth.popleft()
            self.gps_li_earth.append(li)
            self.gps_li.append([x,y])
            gps_li_stadium = [x,y]

    
    def gps_table_update(self):
        if not self.point_loc_earth[3]:
            for i in range(20):
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
    
    def imu_table_update(self):
        if len(self.imu_li) == 0:
            for i in range(20):
                for j in range(1):
                    self.imu_table.setItem(i, j, QTableWidgetItem(str("")))

        else:
            for i in range(len(self.imu_li)):
                self.imu_table.setItem(i, 0, QTableWidgetItem(str(self.imu_li[i])))
            


    def motor_calculate_start_button(self):
        btn = QPushButton('Calculate Start', self)
        btn.move(880, 700)
        btn.resize(150,80)
        # self.point_loc 로스로 보내는 코드
        # 모터 테이블 쓰레드 start 코드
    
    def start_button(self):
        btn = QPushButton('Launch', self)
        btn.move(1070, 700)
        btn.resize(150,80)
        # 출발 불린 값 보내기 로스
    
    def stop_button(self):
        btn = QPushButton('Stop', self)
        btn.move(1260, 700)
        btn.resize(150,80)
        # 스탑 불린값 로스

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