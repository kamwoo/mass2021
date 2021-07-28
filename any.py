from math import *

def bearingP1toP2(p1,p2):
    P1_latitude, P1_longitude, P2_latitude, P2_longitude = p1[0], p1[1], p2[0], p2[1]
    Cur_Lat_radian = P1_latitude * (3.141592 / 180)
    Cur_Lon_radian = P1_longitude * (3.141592 / 180)
    Dest_Lat_radian = P2_latitude * (3.141592 / 180)
    Dest_Lon_radian = P2_longitude * (3.141592 / 180)
    radian_distance = 0
    radian_distance = acos(sin(Cur_Lat_radian) * sin(Dest_Lat_radian) + cos(Cur_Lat_radian) * \
                           cos(Dest_Lat_radian) * cos(Cur_Lon_radian - Dest_Lon_radian))
    radian_bearing = acos((sin(Dest_Lat_radian) - sin(Cur_Lat_radian) * cos(radian_distance)) / (cos(Cur_Lat_radian) * \
                                                                                                 sin(radian_distance)))
    true_bearing = 0

    if sin(Dest_Lon_radian - Cur_Lon_radian) < 0:
        true_bearing = radian_bearing * (180 / 3.141592)
        true_bearing = 360 - true_bearing
    else:
        true_bearing = radian_bearing * (180 / 3.141592)

    return true_bearing

p0 = [35.54536462025495, 129.25149566155892]
p1 = [35.54532374971028, 129.2515043973441]
p2 = [35.54543747639157, 129.25178175852275]
p3 = [35.54538949796758, 129.25179923009307]

x1 = [35.54536462025495, 129.25159175519565]

print(bearingP1toP2(p0,p2))

