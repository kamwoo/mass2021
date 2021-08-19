#! /usr/bin/python3

import rospy
from std_msgs.msg import Float32MultiArray, MultiArrayDimension, Float32
from serial import Serial
from time import sleep

port = "/dev/ttyACM0"
serialFromArduino = Serial(port, 115200)
serialFromArduino.flushInput()

def gps_talker():
    pub = rospy.Publisher('gps_list', Float32MultiArray, queue_size = 1)
    rospy.init_node('gps', anonymous = True)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        input_s = serialFromArduino.readline()
        value = input_s.decode()
        try:
            value = list(map(float, value.split(" ")))
        except:
            pass
        msg  = Float32MultiArray()
        msg.data = value
        if type(msg.data) != str:
            pub.publish(msg)
            print(msg.data)


if __name__ == '__main__':
    try:
        gps_talker()
    except rospy.ROSInterruptException:
        pass
