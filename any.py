from math import *

def CalculateRelativePoint(li):
    tempLi = [0.0 , 0.0]
    bottomMaxLi = [10.0, 0.0]
    bottomMinLi = [0.0, 0.0]

    def CalculateDistance(tempPoint1, tempPoint2):
        return sqrt((tempPoint2[1] - tempPoint1[1]) ** 2.0 + (tempPoint2[0] - tempPoint1[0]) ** 2.0)

    def CalculateDirectionValue(tempPoint1, tempPoint2, tempPoint3):
        aVector = [(tempPoint2[0] - tempPoint1[0]), (tempPoint2[1] - tempPoint1[1]), 0.0]
        bVector = [(tempPoint3[0] - tempPoint1[0]), (tempPoint3[1] - tempPoint1[1]), 0.0]
        ZdirectionValue = aVector[0] * bVector[1] - aVector[1] * bVector[0]
        return ZdirectionValue

    distanceA = CalculateDistance(bottomMaxLi, li)
    distanceB = CalculateDistance(bottomMinLi, li)
    distanceC = CalculateDistance(bottomMinLi, bottomMaxLi)

    degreeValue = abs(
        degrees(acos((distanceB ** 2.0 + distanceC ** 2.0 - distanceA ** 2.0) / (2.0 * distanceB * distanceC))))
    directionValue = CalculateDirectionValue(bottomMinLi, bottomMaxLi, li)

    if (directionValue <= 0.0):
        degreeValue = -degreeValue

    tempLi[0] = distanceB * cos(degreeValue * (pi /180.0))
    tempLi[1] = distanceB * sin(degreeValue * (pi /180.0))

    return tempLi

