from math import *
import time

## -> 설명
#### -> 임시로 바꾸는 코드를 지우고 실제 구현 코드 넣을것
##### -> 예외처리
####### -> 최종 함수 설명

class CalculateClass :
    startButtonOnAndOff = 0
    objectAllLists = []
    objectLocalList = []  ## 지금 당장 가야할 목표를 저장한다.
    whileCount = 0  ## 처음 목표 기준을 정하기 힘들어 대입한 변수
    changeCount = 0  ## 목표가 바뀐 횟수를 저장하기 위한 변수
    numOfObject = 0  ## 목표가 몇개 있는지 확인하는 변수
    tempListForExtended = []  ## 목표를 받을 변수들
    tempListForY = []  ##목표를 받을 변수들 3개씩 대입된다.
    angleForCalculateDirection = 0.0  ## extended line으로 계산한 angle을 저장하기 위한 변수
    angleForCompareImu = 0.0  ## imu와 비교하기 위한 angle을 저장하기 위한 변수
    tempPointForCalculateExtend = 0.0  ## 각도를 계산 하기위한 기준선위의 점을 저장하기 위한 변수
    tempPointForCalculateY = 0.0  ## 각도를 계산 하기위한 기준선위의 점을 저장하기 위한 변수
    resultMotorValue = [0, 0]  ## 계산된 모터의 값을 저장하기 위한 변수이다.
    gpsPoint = []
    imuHeadingAngle = 0.0
    tempFile = ''
    tollernce = 0.01

    ## 실험을 통해서 구한 상수들
    straight = [104, 105]
    right = [105, 76]
    left = [76, 105]
    turnDistance = 1000 ## 1m
    ## 각도 범위는
    ## SelectTurnAngleRange 에서 정한다.
    stopConstant = False ## 90,90을 거쳐갔는지?
    initialTurnConstant = False ## 처음에 회전을 했는가?


    def __init__(self, objectAllLists):
        ## Define Global Variable
        ## 전역변수를 정의한다.
        self.objectAllLists = objectAllLists ## 전체 목표를 저장한다.

    ## require two point list[0,1]
    ## First point = Base start point , Second point = Base end point
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## 두점의 연장선을 그어 그 위의 점을 구하기 위한 함수/ 2개의 점 리스트가 필요하다. / 1번째 점은 기준시발점 , 2번째 점은 기준종착점
    def CalculatePointOnExtendedLine(self, tempPoint1, tempPoint2):
        slope = self.CalculateSlope(tempPoint1, tempPoint2)
        extendedX = 0.0
        extendedY = 0.0
        if (tempPoint1[0] > tempPoint2[0]):   ## 왼쪽으로 갈 때
            extendedX = tempPoint2[0] - 20.0
            extendedY = slope * extendedX + (tempPoint2[1] - (tempPoint2[0] * slope))
        elif (tempPoint1[0] < tempPoint2[0]): ## 오른쪽으로 갈 때
            extendedX = tempPoint2[0] + 20.0
            extendedY = slope * extendedX + (tempPoint2[1] - (tempPoint2[0]) * slope)
        elif (tempPoint1[0] == tempPoint2[0]): ##### y축 방향으로만 갈 때
            if (tempPoint2[1] < tempPoint1[1]): ## 아래로 갈 때
                extendedX = tempPoint2[0]
                extendedY = tempPoint2[1] - 10.0
            elif (tempPoint2[1] > tempPoint1[1]): ## 위로 갈 때
                extendedX = tempPoint2[0]
                extendedY = tempPoint2[1] + 10.0
        extendedPoint = [extendedX, extendedY]
        return extendedPoint

    ## Funtion for Calculate point on y cordinate/ require one point list[0,1]
    ## First point = Base start point , Second point = Base end point
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## y축 위의 점을 구하기 위한 함수/ 1개의 점 리스트가 필요하다. / 1번째 점은 기준시발점
    def CalculatePointOnYCordinate (self, tempPoint1):
        yExtendedX = tempPoint1[0]
        yExtendedY = tempPoint1[1] + 20.0
        yExtendedPoint = [yExtendedX, yExtendedY]
        return yExtendedPoint

    ## Funtion for Calculate range of turn angle/ requir will turn angle
    ## 각도 범위를 구한다. -> 실험을 통해서 각도의 범위를 구해야 한다.
    def SelectTurnAngleRange (self, extendBaseAngle):
        if (extendBaseAngle < 30.0):
            return 15.0
        elif (extendBaseAngle < 40.0):
            return 20.0
        elif (extendBaseAngle < 50.0):
            return 30.0
        elif (extendBaseAngle < 60.0):
            return 30.0
        elif (extendBaseAngle < 70.0):
            return 30.0
        elif (extendBaseAngle < 80.0):
            return 30.0
        elif (extendBaseAngle < 90.0):
            return 30.0
        elif (extendBaseAngle < 100.0):
            return 30.0
        elif (extendBaseAngle < 110.0):
            return 30.0
        elif (extendBaseAngle < 120.0):
            return 30.0
        elif (extendBaseAngle < 130.0):
            return 30.0
        elif (extendBaseAngle < 150.0):
            return 30.0
        elif (extendBaseAngle < 160.0):
            return 30.0
        elif (extendBaseAngle < 170.0):
            return 30.0
        else:
            return 30.0

    ## require two point list[0,1]
    ## 순서 필요 x
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## 점과 점사이의 거기를 계산한다. / 점이 x와 y점을 가지기 때문에 2개의 리스트가 필요하다.
    def CalculateDistance (self, tempPoint1, tempPoint2):
        P1_latitude, P1_longitude, P2_latitude, P2_longitude = tempPoint1[0], tempPoint1[1], tempPoint2[0], tempPoint2[1]
        if (P1_latitude == P2_latitude) and (P1_longitude == P2_longitude):
            return 0

        e10 = P1_latitude * pi / 180
        e11 = P1_longitude * pi / 180
        e12 = P2_latitude * pi / 180
        e13 = P2_longitude * pi /180

        c16 = 6356752.314140910
        c15 = 6378137.000000000
        c17 = 0.0033528107
        f15 = c17 + c17 * c17
        f16 = f15 / 2
        f17 = c17 * c17 /2
        f18 = c17 * c17 /8
        f19 = c17 * c17 /16
        c18 = e13 - e11
        c20 = (1-c17) * tan(e10)
        c21 = atan(c20)
        c22 = sin(c21)
        c23 = cos(c21)
        c24 = (1 - c17) * tan(e12)
        c25 = atan(c24)
        c26 = sin(c25)
        c27 = cos(c25)
        c29 = c18
        c31 = (c27 * sin(c29) * c27 * sin(c29)) + (c23 * c26 - c22 *c27 * cos(c29))*\
            (c23 * c26 - c22 * c27 * cos(c29))
        c33 = (c22 * c26) + (c23 * c27 * cos(c29))
        c35 = sqrt(c31) / c33
        c36 = atan(c35)
        c38 = 0

        if c31 == 0:
            c38 = 0
        else :
            c38 = c23 * c27 * sin(c29) / sqrt(c31)

        c40 = 0

        if (cos(asin(c38)) * cos(asin(c38))) == 0:
            c40 = 0
        else:
            c40 = c33 -2 * c22 * c26 / (cos(asin(c38)) * cos(asin(c38)))

        c41 = cos(asin(c38)) * cos(asin(c38)) * (c15 * c15 - c16 * c16) / (c16* c16)
        c43 = 1 + c41 / 16384 * (4096 + c41 * (-768 + c41 * (320 - 175 * c41)))
        c45 = c41 / 1024 * (256 + c41 *(-128 + c41 * (74-47 * c41)))
        c47 = c45 * sqrt(c31) * (c40 + c45 / 4 * (c33 * (-1 + 2*c40*c40)- \
            c45 / 6*c40*(-3 + 4*c31)*(-3 +4 * c40 *c40)))
        c50 = c17 / 16 * cos(asin(c38))* cos(asin(c38)) * \
            (4+c17*(4-3*cos(asin(c38))*cos(asin(c38))))
        c52 = c18 + (1-c50)*c17 * c38 * (acos(c33) + c50 * sin(acos(c33)) * \
            (c40 + c50 * c33 * (-1+ 2*c40*c40)))
        c54 = c16 * c43 * (atan(c35) - c47)

        return c54

    ## require three point list[0,1]
    ## First point = Base start point , Second point = Base end point , Third point = Object point
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## 세점에 대한 방향 값을 계산한다. / 3개의 점 리스트가 필요하다. / 1번째 점은 기준시발점 , 2번째 점은 기준종착점 , 3번째 점은 목표점
    def CalculateDirectionValue (self, tempPoint1, tempPoint2, tempPoint3):
        aVector = [(tempPoint2[0] - tempPoint1[0]), (tempPoint2[1] - tempPoint1[1]), 0.0]
        bVector = [(tempPoint3[0] - tempPoint1[0]), (tempPoint3[1] - tempPoint1[1]), 0.0]
        ZdirectionValue = aVector[0] * bVector[1] - aVector[1] * bVector[0]
        return ZdirectionValue


    ## require two point list [0,1]
    ## First point = Base start point , Second point = Base end point
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## 2 점의 기울기를 계산한다. / 2개의 점 리스트가 필요하다. / 1번째 점은 시발점 , 2번째 점은 종착점
    def CalculateSlope (self, tempPoint1, tempPoint2) :
        if ((tempPoint2[0] - tempPoint1[0]) != 0.0 ) :
            slope = (tempPoint2[1] - tempPoint1[1])/(tempPoint2[0] - tempPoint1[0])
        else :
            slope = 999999.0 ##### 기울기를 구할때 (y2-y1) / (x2-x1) 인데 x2랑 x1이 같으면 기울기가 무한대라고 가정한다.
        return slope

    ## require three point list [0,1]
    ## First point = Base start point , Second point = Base end point
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## 세점에 대한 방향 값을 계산한다. / 3개의 점 리스트가 필요하다. / 1번째 점은 기준시발점 , 2번째 점은 기준종착점 , 3번째 점은 목표점
    def CalculateDegreeOfPoint3 (self, tempPoint1, tempPoint2, tempPoint3):
        distanceA = self.CalculateDistance(tempPoint2, tempPoint3)
        distanceB = self.CalculateDistance(tempPoint1, tempPoint3)
        distanceC = self.CalculateDistance(tempPoint1, tempPoint2)
        degreeValue = abs(degrees(acos((distanceB**2.0 + distanceC**2.0 - distanceA**2.0)/(2.0 * distanceB * distanceC))))
        directionValue = self.CalculateDirectionValue(tempPoint1, tempPoint2, tempPoint3)
        if (directionValue > 0.0):
            degreeValue = -degreeValue
        return degreeValue

    ## require two point list [0,1]
    ## First point = Base start point , Second point = Base end point
    ## tempPoint[0] = xValue , tempPoint[1] = yValue
    ## Gps와 목표 지점의 각도를 계산한다. / 2개의 점 리스트가 필요하다. / tempObjectLocalList = 목표물 점 ,
    def CalculateDegreeOfGpsPoint(self, tempObjectLocalList, tempGpsPoint):

        tempPointForCalculateGps = self.CalculatePointOnYCordinate(tempGpsPoint)
        tempListForGps = [tempGpsPoint, tempPointForCalculateGps, tempObjectLocalList]
        tempDegree = self.CalculateDegreeOfPoint3(tempListForGps[0],
                                         tempListForGps[1],
                                         tempListForGps[2])

        return tempDegree

    ## motorSpeed = 거리당 계산된 모터의 속도
    ## imuHeadingAngle = imu에서 직접 받아올 Heading angle data
    ## angleOfBaseExtendeLine = 출발점과 끝점을 기준으로 연장선을 그었을 때 생기는 각도(방향을 지정하기 위한 각도이다./시계, 반시계)
    ## angelOfBaseYcordinate = 우리 imu 초기값이 y축에 지정되어있다고 가정하에 만든 각도 (imu의 heading angle과 비교한다.)
    ## return 값은 [왼쪽모터,오른쪽모터] 출력이다.
    def CalculateFinalMotorValue(self,remainDistance, angleOfBaseExtendeLine,
                             angleOfBaseYcordinate, tempCount):

        motor = [90,90]
        motor[0] = self.straight[0]
        motor[1] = self.straight[1]

        turnAngleRange = self.SelectTurnAngleRange(angleOfBaseExtendeLine)

        ##처음에 회전을 했는가?
        if(self.initialTurnConstant == False):
            tempAngleOfTrun = abs(abs(angleOfBaseExtendeLine) - abs(self.imuHeadingAngle))
            if (angleOfBaseExtendeLine <= 0.0):  ##LEFT

                ## 우리가 설정한 각도 범위내로 아직 안들어왔냐? -> 안들어왔으면 돌려라
                if ((tempAngleOfTrun - turnAngleRange) > self.tollernce):
                    motor[0] = self.left[0]
                    motor[1] = self.left[1]

                ## 우리가 설정한 각도 범위내로 들어오면 다음 목표로 바꾼다. -> 우리의 프로세스 끝 -> 이렇게 된다면 다음 목표로 설정되서
                ## remainDistance가 다음목표와의 거리로 설정되서 직진을 하게 된다.
                else:
                    self.initialTurnConstant = True
            else:  ## Right
                if ((tempAngleOfTrun - turnAngleRange) > self.tollernce):
                    motor[0] = self.right[0]
                    motor[1] = self.right[1]
                else:
                    self.initialTurnConstant = True

        ## 처음에 회전을 했다
        else:
            ## 남은 거리가 회전되어야 될 거리랑 차이가 작아서 회전을 해야되는가?
            if ((remainDistance - self.turnDistance) < self.tollernce):
                ## 회전 하기 전에 잠시 멈추냐>
                if (self.stopConstant == False):
                    self.stopConstant = True
                    motor = [90, 90]
                    time.sleep(1)

                ## 멈춘 뒤에 회전을 실시하냐?
                else:
                    tempAngleOfTrun = abs(abs(angleOfBaseExtendeLine) - abs(self.imuHeadingAngle))
                    if (angleOfBaseExtendeLine <= 0.0):  ##LEFT

                        ## 우리가 설정한 각도 범위내로 아직 안들어왔냐? -> 안들어왔으면 돌려라
                        if ((tempAngleOfTrun - turnAngleRange) > self.tollernce):
                            motor[0] = self.left[0]
                            motor[1] = self.left[1]

                        ## 우리가 설정한 각도 범위내로 들어오면 다음 목표로 바꾼다. -> 우리의 프로세스 끝 -> 이렇게 된다면 다음 목표로 설정되서
                        ## remainDistance가 다음목표와의 거리로 설정되서 직진을 하게 된다.
                        else:
                            self.stopConstant = False
                            if (len(self.objectAllLists) == (self.changeCount - 1)):
                                return [90, 90]
                            else:
                                self.changeCount += 1
                    else:  ## Right
                        if ((tempAngleOfTrun - turnAngleRange) > self.tollernce):
                            motor[0] = self.right[0]
                            motor[1] = self.right[1]
                        else:
                            self.stopConstant = False
                            if (len(self.objectAllLists) == (self.changeCount - 1)):
                                return 0
                            else:
                                self.changeCount += 1
            ##직진 보정 하기
            else:
                ## gps로 보정

                tempRelativeDirectionAboutGps = self.CalculateDirectionValue(self.objectAllLists[tempCount],
                                                                             self.gpsPoint,
                                                                             self.objectLocalList)
                if (tempRelativeDirectionAboutGps > 0.0):
                    motor[1] += 1
                elif (tempRelativeDirectionAboutGps < 0.0):
                    motor[0] += 1
                ## imu로 보정

                tempRelativeAngleAboutImu = abs(abs(angleOfBaseYcordinate) - abs(self.imuHeadingAngle))

                if (angleOfBaseYcordinate >0):
                    if(tempRelativeAngleAboutImu >0):  ##Left
                        motor[0] += 1
                    else:  ##Right
                        motor[1] += 1
                else:
                    if (tempRelativeAngleAboutImu > 0):  ##Right
                        motor[1] += 1
                    else:  ##Left
                        motor[0] += 1

        print(motor)
        return motor


    def CalculateAllMethod(self, tempGpsPoint, tempImuHeadingAngle):
        ## receive parameter that GPS and IMU from outer project
        ## 외부에서 GPS와 IMU 변수를 받아온다.
        self.imuHeadingAngle = tempImuHeadingAngle
        self.gpsPoint = tempGpsPoint
        self.objectLocalList = self.objectAllLists[self.changeCount + 1]
        remainingDistance = self.CalculateDistance(self.gpsPoint, self.objectLocalList)

        ## 처음에는 연장을 y축에 맞춰서 해주어야 하므로 if문을 만들어주었다.
        if (self.whileCount == 0):
            tempPointForCalculateExtend = self.CalculatePointOnYCordinate(self.objectAllLists[self.changeCount])
            tempPointForCalculateY = self.CalculatePointOnYCordinate(self.objectAllLists[self.changeCount])
        else:
            tempPointForCalculateExtend = self.CalculatePointOnExtendedLine(self.objectAllLists[self.changeCount],
                                                                       self.objectLocalList)
            tempPointForCalculateY = self.CalculatePointOnYCordinate(self.objectAllLists[self.changeCount])

        tempListForExtended = [self.objectAllLists[self.changeCount], tempPointForCalculateExtend, self.objectLocalList]
        tempListForY = [self.objectAllLists[self.changeCount], tempPointForCalculateY, self.objectLocalList]

        angleForCalculateDirection = self.CalculateDegreeOfPoint3(tempListForExtended[0],
                                                             tempListForExtended[1],
                                                             tempListForExtended[2])

        angleForCompareImu = self.CalculateDegreeOfPoint3(tempListForY[0],
                                                     tempListForY[1],
                                                     tempListForY[2])

        resultMotorValue = self.CalculateFinalMotorValue(remainingDistance,
                                                    angleForCalculateDirection,
                                                    angleForCompareImu, self.changeCount)

        self.whileCount = 1 ##처음 case 제어
        return resultMotorValue
