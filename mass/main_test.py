#! /usr/bin/python3

import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
import serial
import threading, time
from time import sleep
from math import *
from calculate import massMathMotorCalculateAngle

class main():
    point_li = []
    gps_li = [0,0]
    imu_value = 0
    stop = False

    rospy.init_node('main', anonymous = True)
    pub = rospy.Publisher('motor_list', Float32MultiArray, queue_size = 1)
    msg  = Float32MultiArray()

    
    def __init__(self):
        rospy.init_node('main', anonymous = True)
        stackDataFileName = 'Alldata.txt'
        self.f = open(stackDataFileName, 'w')
        self.input_point()
        
        
    def input_point(self):
        self.point_li = [[35.5448414,129.2519006],[35.5448691,129.2519430],[35.5448325,129.2518605]]
        self.motor_Calculator = massMathMotorCalculateAngle(self.point_li)
        
        print("gps , imu thread start")
        while not rospy.is_shutdown():
              self.gps_listener()
              self.imu_listener()
              self.motor_calculate()
              sleep(0.5)
        
    
    def motor_calculate(self):
        if self.stop == False:
            motor_value = self.motor_Calculator.RealWhileAllMethod(self.gps_li, self.imu_value)
            self.msg.data = motor_value
            self.pub.publish(self.msg)
            print(self.gps_li)
            print(self.imu_value)
            print("motorValue: {}".format(motor_value))

            if motor_value == [90,90]:
                print("finish")
                self.stop = True
            else:
                pass
                #print(motor_value)

        
            
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
