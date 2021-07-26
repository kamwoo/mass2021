from math import *

## 35.545000, 129.1555

## point 3D이다. [x, y, z]
def CalculateInnerProduct(tempList, temptempList):
    result = tempList[0] * temptempList[0] + tempList[1] * temptempList[1] + tempList[2] * temptempList[2]
    return result

def CalculateOuterProduct(tempList, temptempList):
    result = [0.0, 0.0, 0.0]

    result[0] = tempList[1] * temptempList[2] - tempList[2] * temptempList[1]
    result[1] = -(tempList[0] * temptempList[2] - tempList[2] * temptempList[0])
    result[2] = tempList[0] * temptempList[1] - tempList[1] * temptempList[0]
    return result

## tempList = 시작 , temptempList = 끝
def CalculateVector(tempList, temptempList):
    result = [0.0, 0.0, 0.0]

    result[0] = temptempList[0] - tempList[0]
    result[1] = temptempList[1] - tempList[1]
    result[2] = temptempList[2] - tempList[2]

    return result

def CalculateDistance(tempPoint1, tempPoint2):
    return sqrt((tempPoint2[1] - tempPoint1[1]) ** 2.0 + (tempPoint2[0] - tempPoint1[0]) ** 2.0)

def CalculateRelativePoint(li):
    tempLi = [0.0, 0.0, 0.0]
    gps_li[0] = [35.54527, 129.2515, 0.0]
    gps_li[1] = [35.54526, 129.25144, 0.0]
    gps_li[2] = [35.54516, 129.25148, 0.0]
    gps_li[3] = [35.54518, 129.25154, 0.0]
    zVector = [0.0, 0.0 , 30.0]
    stadiumWidth = 5.0
    stadiumHeight = 15.0
    bottomMaxLi = gps_li[1]
    bottomMinLi = gps_li[0]

    xRelativeVector = CalculateVector(gps_li[0], gps_li[1])
    yRelativeVector = CalculateVector(gps_li[0], gps_li[3])
    objectVector = CalculateVector(gps_li[0], li)

    xOuter = CalculateOuterProduct(yRelativeVector, zVector)
    yOuter = CalculateOuterProduct(zVector, xRelativeVector)

    xRatio = (CalculateInnerProduct(xOuter, objectVector) / CalculateInnerProduct(xOuter, xRelativeVector))
    yRatio = (CalculateInnerProduct(yOuter, objectVector) / CalculateInnerProduct(yOuter, yRelativeVector))

    tempLi[0] = stadiumWidth * xRatio
    tempLi[1] = stadiumHeight * yRatio

    return tempLi

gps_li = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

##35.54523, 129.25149
##35.54522740504817, 129.25149201974645
##35.545205035467944, 129.25150878355274
##35.545191395476934, 129.25150543079147
##35.54518812187876, 129.25148598477622
##35.545186485079604, 129.25148062035822
##35.54517775548361, 129.25151683017975
Llll = [35.54517775548361, 129.25151683017975, 0.0]
temptemptemp = CalculateRelativePoint(Llll)
print(temptemptemp)
