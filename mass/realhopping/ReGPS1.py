from math import *

## -> 설명
#### -> 임시로 바꾸는 코드를 지우고 실제 구현 코드 넣을것
##### -> 예외처리
####### -> 최종 함수 설명

## Define Global Variable
## 전역변수를 정의한다.
startButtonOnAndOff = 0 ## 1로 변환되면 while문이 돌게 된다.
objectAllLists = [] ## 전체 목표를 저장한다.
objectLocalList = [] ## 지금 당장 가야할 목표를 저장한다.
whileCount = 0 ## 처음 목표 기준을 정하기 힘들어 대입한 변수
changeCount = 0 ## 목표가 바뀐 횟수를 저장하기 위한 변수
numOfObject = 0 ## 목표가 몇개 있는지 확인하는 변수
tempListForExtended = [] ## 목표를 받을 변수들
tempListForY = [] ##목표를 받을 변수들 3개씩 대입된다.
angleForCalculateDirection = 0.0 ## extended line으로 계산한 angle을 저장하기 위한 변수
angleForCompareImu = 0.0 ## imu와 비교하기 위한 angle을 저장하기 위한 변수
tempPointForCalculateExtend = 0.0 ## 각도를 계산 하기위한 기준선위의 점을 저장하기 위한 변수
tempPointForCalculateY = 0.0 ## 각도를 계산 하기위한 기준선위의 점을 저장하기 위한 변수
resultMotorValue = [0,0] ## 계산된 모터의 값을 저장하기 위한 변수이다.

## Receive object list and starting parameter from outer project
## 외부에서 목표점 리스트와 시작을 의미하는 변수를 받아온다.
def PrepareFirst(tempStart, tempObjectList):
    global startButtonOnAndOff
    global objectAllLists

    startButtonOnAndOff = tempStart
    objectAllLists = tempObjectList

## require two point list[0,1]
## First point = Base start point , Second point = Base end point
## tempPoint[0] = xValue , tempPoint[1] = yValue
## 두점의 연장선을 그어 그 위의 점을 구하기 위한 함수/ 2개의 점 리스트가 필요하다. / 1번째 점은 기준시발점 , 2번째 점은 기준종착점
def CalculatePointOnExtendedLine(tempPoint1, tempPoint2):
    slope = CalculateSlope(tempPoint1, tempPoint2)
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
def CalculatePointOnYCordinate (tempPoint1):
    yExtendedX = tempPoint1[0]
    yExtendedY = tempPoint1[1] + 20.0
    yExtendedPoint = [yExtendedX, yExtendedY]
    return yExtendedPoint

## Funtion for Calculate max speed/ require remainDistance
## 최대 속력을 구하기 위한 함수 -> 실험을 통해 알맞은 모터값과 알맞은 거리값을 돌출해서 넣어주어야 하는 곳이다.
def SelectMaxSpeed (tempRemainingDitance):
    if (tempRemainingDitance < 500.0):
        return 5.0
    elif (tempRemainingDitance < 1000.0):
        return 10.0
    else:
        return 20.0

## require two point list[0,1]
## 순서 필요 x
## tempPoint[0] = xValue , tempPoint[1] = yValue
## 점과 점사이의 거기를 계산한다. / 점이 x와 y점을 가지기 때문에 2개의 리스트가 필요하다.
def CalculateDistance (tempPoint1, tempPoint2):
    return sqrt((tempPoint2[1] - tempPoint1[1]) ** 2.0 + (tempPoint2[0] - tempPoint1[0]) ** 2.0)

## require three point list[0,1]
## First point = Base start point , Second point = Base end point , Third point = Object point
## tempPoint[0] = xValue , tempPoint[1] = yValue
## 세점에 대한 방향 값을 계산한다. / 3개의 점 리스트가 필요하다. / 1번째 점은 기준시발점 , 2번째 점은 기준종착점 , 3번째 점은 목표점
def CalculateDirectionValue (tempPoint1, tempPoint2, tempPoint3):
    aVector = [(tempPoint2[0] - tempPoint1[0]), (tempPoint2[1] - tempPoint1[1]), 0.0]
    bVector = [(tempPoint3[0] - tempPoint1[0]), (tempPoint3[1] - tempPoint1[1]), 0.0]
    ZdirectionValue = aVector[0] * bVector[1] - aVector[1] * bVector[0]
    return ZdirectionValue


## require two point list [0,1]
## First point = Base start point , Second point = Base end point
## tempPoint[0] = xValue , tempPoint[1] = yValue
## 2 점의 기울기를 계산한다. / 2개의 점 리스트가 필요하다. / 1번째 점은 시발점 , 2번째 점은 종착점
def CalculateSlope (tempPoint1, tempPoint2) :
    if ((tempPoint2[0] - tempPoint1[0]) != 0.0 ) :
        slope = (tempPoint2[1] - tempPoint1[1])/(tempPoint2[0] - tempPoint1[0])
    else :
        slope = 999999.0 ##### 기울기를 구할때 (y2-y1) / (x2-x1) 인데 x2랑 x1이 같으면 기울기가 무한대라고 가정한다.
    return slope

## require three point list [0,1]
## First point = Base start point , Second point = Base end point
## tempPoint[0] = xValue , tempPoint[1] = yValue
## 세점에 대한 방향 값을 계산한다. / 3개의 점 리스트가 필요하다. / 1번째 점은 기준시발점 , 2번째 점은 기준종착점 , 3번째 점은 목표점
def CalculateDegreeOfPoint3 (tempPoint1, tempPoint2, tempPoint3):
    distanceA = CalculateDistance(tempPoint2, tempPoint3)
    distanceB = CalculateDistance(tempPoint1, tempPoint3)
    distanceC = CalculateDistance(tempPoint1, tempPoint2)
    degreeValue = abs(degrees(acos((distanceB**2.0 + distanceC**2.0 - distanceA**2.0)/(2.0 * distanceB * distanceC))))
    directionValue = CalculateDirectionValue(tempPoint1, tempPoint2, tempPoint3)
    if (directionValue > 0.0):
        degreeValue = -degreeValue
    return degreeValue

## require two point list [0,1]
## First point = Base start point , Second point = Base end point
## tempPoint[0] = xValue , tempPoint[1] = yValue
## Gps와 목표 지점의 각도를 계산한다. / 2개의 점 리스트가 필요하다. / tempObjectLocalList = 목표물 점 ,
def CalculateDegreeOfGpsPoint(tempObjectLocalList, tempGpsPoint):

    tempPointForCalculateGps = CalculatePointOnYCordinate(tempGpsPoint)
    tempListForGps = [tempGpsPoint, tempPointForCalculateGps, tempObjectLocalList]
    tempDegree = CalculateDegreeOfPoint3(tempListForGps[0],
                                         tempListForGps[1],
                                         tempListForGps[2])

    return tempDegree

## motorSpeed = 거리당 계산된 모터의 속도
## imuHeadingAngle = imu에서 직접 받아올 Heading angle data
## angleOfBaseExtendeLine = 출발점과 끝점을 기준으로 연장선을 그었을 때 생기는 각도(방향을 지정하기 위한 각도이다./시계, 반시계)
## angelOfBaseYcordinate = 우리 imu 초기값이 y축에 지정되어있다고 가정하에 만든 각도 (imu의 heading angle과 비교한다.)
## return 값은 [왼쪽모터,오른쪽모터] 출력이다.
def CalculateFinalMotorValue(motorSpeed, angleOfBaseExtendeLine,
                             angleOfBaseYcordinate, tempCount):
    global gpsPoint
    global imuHeadingAngle
    global objectAllLists

    ## imu angle이 같아도 시작점과 목표점을 이은 직선위가 아닌 평행한 직선을 그리며 이동할수도 있다
    ## 따라서 그러한 값을 Gps Point로 보정을 한다.

    ## 직선의 오른쪽에 있는지 왼쪽에 있는지에 따라 왼쪽 모터에 더해야될지 오른쪽 모터에 더해야될지를 판별한다.
    tempRelativeDirectionAboutGps = CalculateDirectionValue(objectAllLists[tempCount],gpsPoint,objectLocalList)

    ## 보정계수의 실질적인 값을 의미한다.
    tempCorrectionFactor = motorSpeed * 0.1

    motor=[0,0]
    angleOfFromNowPositionAndObject = angleOfBaseYcordinate - imuHeadingAngle[0]

    if (angleOfBaseYcordinate != 0.0):
        if (angleOfBaseExtendeLine>=0.0):
            motor[0] = motorSpeed * (1.0 + 1.0 * (angleOfFromNowPositionAndObject / angleOfBaseYcordinate))
            motor[1] = motorSpeed * (1.0 - 1.0 * (angleOfFromNowPositionAndObject / angleOfBaseYcordinate))
        else:
            motor[0] = motorSpeed * (1.0 - 1.0 * (angleOfFromNowPositionAndObject / angleOfBaseYcordinate))
            motor[1] = motorSpeed * (1.0 + 1.0 * (angleOfFromNowPositionAndObject / angleOfBaseYcordinate))
    else:##각도가 0도 일때도 있다. ##################### 이거 어떻게 할까???????????????????????
        if (angleOfBaseExtendeLine>=0.0):
            motor[0] = motorSpeed * (1.0 + 1.0 * (angleOfFromNowPositionAndObject / 180.0))
            motor[1] = motorSpeed * (1.0 - 1.0 * (angleOfFromNowPositionAndObject / 180.0))
        else:
            motor[0] = motorSpeed * (1.0 - 1.0 * (angleOfFromNowPositionAndObject / 180.0))
            motor[1] = motorSpeed * (1.0 + 1.0 * (angleOfFromNowPositionAndObject / 180.0))

    if (tempRelativeDirectionAboutGps > 0.0):
        motor[1] = motor[1] + tempCorrectionFactor
    elif (tempRelativeDirectionAboutGps < 0.0):
        motor[0] = motor[0] + tempCorrectionFactor

    return motor

## Starting Point (Temporary Main Funtion)
## 첫 시작되는 곳
#### 실제 구현 코드 PrepareFirst(tempStart, tempObjectAllLists)
objectAllLists = [[200.0,0.0],[0.0,300.0],[200.0,300.0],[400.0,300.0],[200.0,600.0],[200.0,300.0],[200.0, 0.0]]

## START While Loop funtion
## While Loop 함수가 실행되는 곳
while(objectAllLists):
    ## receive parameter that GPS and IMU from outer project
    ## 외부에서 GPS와 IMU 변수를 받아온다.
    gpsPoint = [100.0, 100.0]                      ## 외부의 GPS가 '1'개씩 여기로 들어와야 된다.
    imuHeadingAngle = [-30.0]               ## 외부의 IMU ANGLE 값이 '1'개씩 여기로 들어와야 된다.

    if((len(gpsPoint) >= 1) and (len(imuHeadingAngle) >= 1)):        ## 값이 들어오면 시작하기 위한 것
        while(True):

            objectLocalList = objectAllLists[changeCount + 1]
            remainingDistance = CalculateDistance(gpsPoint, objectLocalList)
            maxMotorSpeed = SelectMaxSpeed(remainingDistance)

            ## 처음에는 연장을 y축에 맞춰서 해주어야 하므로 if문을 만들어주었다.
            if(whileCount == 0):
                tempPointForCalculateExtend = CalculatePointOnYCordinate(objectAllLists[changeCount])
                tempPointForCalculateY = CalculatePointOnYCordinate(objectAllLists[changeCount])
            else :
                tempPointForCalculateExtend = CalculatePointOnExtendedLine(objectAllLists[changeCount], objectLocalList)
                tempPointForCalculateY = CalculatePointOnYCordinate(objectAllLists[changeCount])

            tempListForExtended = [objectAllLists[changeCount], tempPointForCalculateExtend, objectLocalList]
            tempListForY = [objectAllLists[changeCount], tempPointForCalculateY, objectLocalList]

            angleForCalculateDirection = CalculateDegreeOfPoint3(tempListForExtended[0],
                                                                 tempListForExtended[1],
                                                                 tempListForExtended[2])

            angleForCompareImu = CalculateDegreeOfPoint3(tempListForY[0],
                                                         tempListForY[1],
                                                         tempListForY[2])

            angleForCompareGps = CalculateDegreeOfGpsPoint(objectLocalList, gpsPoint)

            resultMotorValue = CalculateFinalMotorValue(maxMotorSpeed,
                                                        angleForCalculateDirection,
                                                        angleForCompareImu, changeCount)

            print(resultMotorValue)

            whileCount += 1

            if(remainingDistance < 500.0):
                if (len(objectAllLists) == (changeCount - 1)) :
                    break
                else :
                    changeCount += 1