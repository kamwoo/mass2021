#! /usr/bin/python3

import rospy
from std_msgs.msg import Float32
from serial import Serial

port = "/dev/ttyACM0"
serialFromArduino = Serial(port, 115200)
serialFromArduino.flushInput()


def talker():
    pub = rospy.Publisher('imu_list', Float32, queue_size = 10)
    rospy.init_node('imu', anonymous = True)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        input_s = serialFromArduino.readline()
        value = input_s.decode()
        try:
            value = float(value)
        except:
            pass
        print(value)
        pub.publish(value)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
