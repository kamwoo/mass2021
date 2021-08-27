#! /usr/bin/python3.6
# -*- coding: utf-8 -*-

from math import *
import time

class massMathMotorCalculateAngle:

    compassAngle = 0.0 ## compass Angle계산되서 저장될것이다.
    gpsPoint = []
    objectAllLists = [] ## 전체 목표 값들이 들어오게 된다.
    objectLocalList = []  ## 지금 당장 가야할 목표를 저장한다.
    resultMotorValue = [0, 0]  ## 계산된 모터의 값을 저장하기 위한 변수이다.
    sequenceOfObjectList = 0 ## objectLocalList의 순서를 제어하기 위한 변수
    tollernce = 0.01 ## 오차제어
    angleOfBeforeStaright = 0.01 ## 직진하기 전에 회전을 얼마정도만 할건지 계산하기 위한 변수

    rotateOnOff = False

    ## 실험을 통해서 구한 상수들
    straight = [107, 107]
    right = [103, 78]
    left = [78, 103]
    turnDistance = 1.0  ## 1m

    def __init__(self, objectAllLists):
        ## Define Global Variable
        ## 전역변수를 정의한다.
        self.objectAllLists = objectAllLists  ## 전체 목표를 저장한다.

    def CalculateDistance(self, P1_latitude, P1_longitude, P2_latitude, P2_longitude):
        if (P1_latitude == P2_latitude) and (P1_longitude == P2_longitude):
            return 0

        PHI = pi;

        e10 = P1_latitude * PHI / 180
        e11 = P1_longitude * PHI / 180
        e12 = P2_latitude * PHI / 180
        e13 = P2_longitude * PHI / 180

        c16 = 6356752.314140910
        c15 = 6378137.000000000
        c17 = 0.0033528107
        f15 = c17 + c17 * c17
        f16 = f15 / 2
        f17 = c17 * c17 / 2
        f18 = c17 * c17 / 8
        f19 = c17 * c17 / 16
        c18 = e13 - e11
        c20 = (1 - c17) * tan(e10)
        c21 = atan(c20)
        c22 = sin(c21)
        c23 = cos(c21)
        c24 = (1 - c17) * tan(e12)
        c25 = atan(c24)
        c26 = sin(c25)
        c27 = cos(c25)
        c29 = c18
        c31 = (c27 * sin(c29) * c27 * sin(c29)) + (c23 * c26 - c22 * c27 * cos(c29)) * \
              (c23 * c26 - c22 * c27 * cos(c29))
        c33 = (c22 * c26) + (c23 * c27 * cos(c29))
        c35 = sqrt(c31) / c33
        c36 = atan(c35)
        c38 = 0

        if c31 == 0:
            c38 = 0
        else:
            c38 = c23 * c27 * sin(c29) / sqrt(c31)

        c40 = 0

        if (cos(asin(c38)) * cos(asin(c38))) == 0:
            c40 = 0
        else:
            c40 = c33 - 2 * c22 * c26 / (cos(asin(c38)) * cos(asin(c38)))

        c41 = cos(asin(c38)) * cos(asin(c38)) * (c15 * c15 - c16 * c16) / (c16 * c16)
        c43 = 1 + c41 / 16384 * (4096 + c41 * (-768 + c41 * (320 - 175 * c41)))
        c45 = c41 / 1024 * (256 + c41 * (-128 + c41 * (74 - 47 * c41)))
        c47 = c45 * sqrt(c31) * (c40 + c45 / 4 * (c33 * (-1 + 2 * c40 * c40) - \
                                                  c45 / 6 * c40 * (-3 + 4 * c31) * (-3 + 4 * c40 * c40)))
        c50 = c17 / 16 * cos(asin(c38)) * cos(asin(c38)) * \
              (4 + c17 * (4 - 3 * cos(asin(c38)) * cos(asin(c38))))
        c52 = c18 + (1 - c50) * c17 * c38 * (acos(c33) + c50 * sin(acos(c33)) * \
                                             (c40 + c50 * c33 * (-1 + 2 * c40 * c40)))
        c54 = c16 * c43 * (atan(c35) - c47)

        return c54

    ## 국토해양부에서 제공된 GPS 2개로 각도 계산하는것 -> 북쪽을 기준으로 계산된다고 한다.
    def CalculateBearingP1toP2(self, P1_latitude, P1_longitude, P2_latitude, P2_longitude):
        Cur_Lat_radian = P1_latitude * (3.141592 / 180)
        Cur_Lon_radian = P1_longitude * (3.141592 / 180)
        Dest_Lat_radian = P2_latitude * (3.141592 / 180)
        Dest_Lon_radian = P2_longitude * (3.141592 / 180)
        radian_distance = 0.0


        radian_distance = acos(sin(Cur_Lat_radian) * sin(Dest_Lat_radian) + cos(Cur_Lat_radian) * \
                               cos(Dest_Lat_radian) * cos(Cur_Lon_radian - Dest_Lon_radian))

        if(((sin(Dest_Lat_radian) - sin(Cur_Lat_radian) * cos(radian_distance)) / (cos(Cur_Lat_radian) * sin(radian_distance)))> 1.0):
            radian_bearing = acos(0.99999999999999999999999)
        elif(((sin(Dest_Lat_radian) - sin(Cur_Lat_radian) * cos(radian_distance)) / (cos(Cur_Lat_radian) * sin(radian_distance)))< -1.0):
            radian_bearing = acos(-0.99999999999999999999999)

        else:
            radian_bearing = acos(
            (sin(Dest_Lat_radian) - sin(Cur_Lat_radian) * cos(radian_distance)) / (cos(Cur_Lat_radian) * \
                                                                                   sin(radian_distance)))

        true_bearing = 0.0

        if sin(Dest_Lon_radian - Cur_Lon_radian) < 0.0:
            true_bearing = radian_bearing * (180 / 3.141592)
            true_bearing = 360 - true_bearing
        else:
            true_bearing = radian_bearing * (180 / 3.141592)

        true_bearing += 8
        if true_bearing >= 360:
            true_bearing -= 360

        return true_bearing

    ##Angle을 비교하는 함수 ->>>>>>>>>>>>>>>>>>> 시계방향 반시계방향 제어
    def CalculateDiffrenceAngle(self, tempCompass, tempBearing):
        tempResultAngle = tempBearing - tempCompass
        if tempResultAngle > 180.0:
            tempResultAngle -= 360.0
        elif tempResultAngle < -180.0:
            tempResultAngle += 360.0

        return tempResultAngle


    def CalculateAngleValueAfterRotate(self, tempDiffrenceAngleOfCompassWithBearing):
        ## 시계방향, 반시계방향 case 분류가 안되어 있음

        if(self.rotateOnOff == False):
            if (abs(tempDiffrenceAngleOfCompassWithBearing) < 10.0):
                self.rotateOnOff = False
                self.angleOfBeforeStaright = 0.0 * 1.5
            elif (abs(tempDiffrenceAngleOfCompassWithBearing) < 45.0):
                self.rotateOnOff = True
                self.angleOfBeforeStaright = 10.0 * 1.5
            elif (abs(tempDiffrenceAngleOfCompassWithBearing) < 90.0):
                self.rotateOnOff = True
                self.angleOfBeforeStaright = 20.0 * 1.5
            else:
                self.rotateOnOff = True
                self.angleOfBeforeStaright = 30.0 * 1.5

    def CalculateFinalMotorValue(self, tempDiffrenceAngle):
        motor = [90,90]
        motor[0] = self.straight[0]
        motor[1] = self.straight[1]

        self.CalculateAngleValueAfterRotate(tempDiffrenceAngle)

        if(self.rotateOnOff):
            if((abs(tempDiffrenceAngle) - self.angleOfBeforeStaright) < self.tollernce):
                self.rotateOnOff = False
            else:#######오른쪽인지 왼쪽인지 회전을 제어해야된다.
                if tempDiffrenceAngle >= 0:
                    motor[0] = self.right[0]
                    motor[1] = self.right[1]
                else:
                    motor[0] = self.left[0]
                    motor[1] = self.left[1]

        ## gps가 왼쪽에 있거나 오른쪽에 있으면 모터에 더 추가해주고 싶은데 상대좌표가 아니라서 어떻게 될지 모르겠음

        return motor

    ##while 문을 돌게될 함수 우리 class문에서의 main 함수라고 볼 수 있음
    def RealWhileAllMethod(self, tempGpsPoint, tempCompassAngle):
        self.gpsPoint = tempGpsPoint ##[위도, 경도]로 들어온다.
        self.compassAngle = tempCompassAngle ## 현재에서 얼마나 차이가 나는지 확인한다.

        self.objectLocalList = self.objectAllLists[self.sequenceOfObjectList]  ## 지금 갈곳이다.
        remainDistance = self.CalculateDistance(tempGpsPoint[0], tempGpsPoint[1],
                                                self.objectLocalList[0], self.objectLocalList[1])

        print("remainDistance : {}".format(remainDistance))
        if (abs(remainDistance) < self.turnDistance):
            if (len(self.objectAllLists) == (self.sequenceOfObjectList - 1)):
                return 0
            else:
                self.sequenceOfObjectList += 1

        bearingAngle = self.CalculateBearingP1toP2(self.gpsPoint[0], self.gpsPoint[1],
                                                       self.objectLocalList[0], self.objectLocalList[1])

        diffrenceAngle = self.CalculateDiffrenceAngle(self.compassAngle, bearingAngle)

        # motorValue = [0,0]

        motorValue = self.CalculateFinalMotorValue(diffrenceAngle)
        motorValue[0] = int(motorValue[0])
        motorValue[1] = int(motorValue[1])

        return motorValue
