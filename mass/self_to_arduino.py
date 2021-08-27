#! /usr/bin/python3.6

import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
import serial
from threading import Timer
from time import sleep

ser = serial.Serial(port = '/dev/ttyACM0', baudrate = 9600,)


def motor_callback(data):
    try:
        pl = int(data.data[0])
        pr = int(data.data[1])
        to = str(pl)+" "+str(pr)
        print(to)
        ser.write(to.encode())
    except KeyboardInterrupt:
           print("key error")
           pl = 90
           pr = 90
           to = str(pl)+" "+str(pr)+"\n"
           ser.write(to.encode())


def motor_listener():
    rospy.init_node('motor', anonymous = True)
    #while not rospy.is_shutdown():
    rospy.Subscriber('motor_list', Float32MultiArray, motor_callback)
    rospy.spin()


if __name__ == '__main__':
    try:
        motor_listener()
    except rospy.ROSInterruptException:
        print("ros error")
        pass
