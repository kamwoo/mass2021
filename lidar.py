#!/usr/bin/env python

import sys
from rplidar import RPLidar
import rospy
from autopilot.msg import rplidar

PORT_NAME = '/dev/ttyUSB2'

rospy.init_node('lidar')
pub=rospy.Publisher('lidar_topic',rplidar, queue_size=10)
rate = rospy.Rate(1)
rate.sleep()

def run():
    lidar = RPLidar(PORT_NAME)
    try:
        for measurment in lidar.iter_measurments():
            new_scan,quality,angle,distance = measurment
            lidar_msg=rplidar()
            lidar_msg.angle=angle
            lidar_msg.distance=distance
            pub.publish(lidar_msg)
            if distance != 0:
            	print ("angle : %f  distance : %f"%(angle,distance))
            
    except KeyboardInterrupt:
        print('Stoping.')
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    
run()
