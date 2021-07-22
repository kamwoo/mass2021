#! /usr/bin/python3.6
import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
import serial
from threading import Timer
from time import sleep

ser = serial.Serial(port = '/dev/ttyACM2', baudrate = 9600,)

def motor_callback(data):
    rospy.loginfo(data.data)
    a = data.data
    try:
        pr = a[0]
        pl = a[1]
        sleep(0.5)
        to = str(pl)+","+str(pr)+"\n"
        print(to)
        ser.write(to.encode())
        rospy.loginfo(pl)
        rospy.loginfo(pr)
    except KeyboardInterrupt:
           pl = 0
           pr = 0
           to = str(pl)+","+str(pr)+"\n"
           print(to)
           ser.write(to.encode())


def motor_listener():
    rospy.init_node('motor', anonymous = True)
    rospy.Subscriber('motor_list', Float32MultiArray, motor_callback)
    rospy.spin()

if __name__ == '__main__':
    try:
        motor_listener()
    except rospy.ROSInterruptException:
        pass
