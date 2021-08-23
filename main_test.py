#! /usr/bin/python3

import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
import serial
import threading, time
from time import sleep
from math import *
from calculate import CalculateClass

class main():
    point_li = []
    gps_li = [0,0]
    imu_value = 0
    stop = False
    
    def __init__(self):
        rospy.init_node('main', anonymous = True)
        stackDataFileName = 'Alldata.txt'
        self.f = open(stackDataFileName, 'w')
        self.input_point()
        
    def input_point(self):
        point_cnt = int(input("point count : "))
        for i in range(point_cnt):
            cnt = i + 1
            input_point_li = list(map(float, input("{} point location : ".format(cnt)).split(" ")))
            self.point_li.append(input_point_li)
        self.motor_Calculator = CalculateClass(self.point_li)
        
        print("gps , imu thread start")
        while not rospy.is_shutdown():
              self.gps_listener()
              self.imu_listener()
              self.motor_calculate()
              sleep(1)
        
    
    def motor_calculate(self):
        if self.stop == False:
            motor_value = self.motor_Calculator.CalculateAllMethod(self.gps_li, self.imu_value)
            if motor_value == [0,0]:
                print("finish")
                self.stop = True
            else:
                pass
        
            
    def gps_callback(self, data):
        self.gps_li = [data.data[0]*0.0000001, data.data[1]*0.0000001]
        
    def gps_listener(self):
        rospy.Subscriber('gps_list', Float32MultiArray, self.gps_callback)
        
    def imu_callback(self,data):
        self.imu_value = data.data
        
    def imu_listener(self):
        rospy.Subscriber('imu_list', Float32, self.imu_callback)



if __name__ == '__main__':
    try:
        hopp = main()
    except rospy.ROSInterruptException:
        pass
