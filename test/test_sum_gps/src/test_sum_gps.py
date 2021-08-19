#! /usr/bin/python3

import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
import serial
import threading, time
from time import sleep

def gps_callback(self, data):
    self.gps_li = [data.data[0]*0.0000001, data.data[1]*0.0000001]

def gps_listener(self):
    rospy.Subscriber('gps_list', Float32MultiArray, self.gps_callback)

def motor_listener():
    rospy.init_node('motor', anonymous = True)
    rospy.Subscriber('motor_list', Float32MultiArray, motor_callback)
    rospy.spin()

if __name__ == '__main__':
    try:
        motor_listener()
    except rospy.ROSInterruptException:
        pass
