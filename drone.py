import pygame
from random import randint as ri
import time
import matplotlib.pyplot as plt
import cv2
import numpy as np
import math
from scipy import ndimage
import os
import imagezmq
import imutils
from urllib.request import urlopen



################## 핸드폰 카메라 실시간 스트리밍 ##################
################## 키(q) 누르면 이미지 캡쳐&저장 ##################

url = 'http://172.20.10.3:8080/shot.jpg'

while True:

    imgResp = urlopen(url)
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgNp, -1)
    image = imutils.resize(img, width=800)  # frame 크기 조정

    cv2.imshow('IPWebcam', image)


    time.sleep(0.1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite('cap_start.jpg', image)
        break

pat = os.path.join('img', 'shape.png')
img = cv2.imread('cap_start.jpg')

################## raspberry pi 카메라 실시간 스트리밍 ##################
################## 키(q) 누르면 이미지 캡쳐&저장 ##################

# image_hub = imagezmq.ImageHub()
#
# while True:
#     rpi_name, image = image_hub.recv_image()
#     image = imutils.resize(image, width=800)   # 프레임 크기
#
#     cv2.imshow(rpi_name, image)
#     if cv2.waitKey(1) == ord('q'):
#         cv2.imwrite('start.jpg', image)
#         break
#
#     image_hub.send_reply(b'OK')
#
# pat = os.path.join('img', 'shape.png')
# img = cv2.imread('start.jpg')

################## 이미지 회전 #################

img_before = img

cv2.imshow("Before", img_before)
key = cv2.waitKey(0)

img_gray = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

angles = []

for x1, y1, x2, y2 in lines[0]:
    cv2.line(img_before, (x1, y1), (x2, y2), (0, 255, 255), 3)
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    angles.append(angle)

median_angle = np.median(angles)
img_rotated = ndimage.rotate(img_before, median_angle)

# print("Angle is {}".format(median_angle))
# cv2.imshow('img_rotated', img_rotated)

# cv2.waitKey()
# cv2.destroyWindow()

################## 물(파랑) 이외 색상 지우기 #################

img = img_rotated

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_blue = np.array([90, 100, 0])         # 실제 대회 경기장 사진 따라 수정 (파랑 범위)
upper_blue = np.array([150, 255, 255])

mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
result = cv2.bitwise_and(img, img, mask=mask_blue)
result[mask_blue == 0] = (0, 0, 0)

cv2.imshow('result', result)    # 결과 result

################## 경기장 네모 인식 #################

gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

ret, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

contour, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# con = cv2.drawContours(result, contour, 0, (0, 255, 0), 2)  # drawContours(그릴 이미지, , 선 색, 두께 )

# cv2.imshow('con', con)


# 네모
for cont in contour:
    # approxPolyDP(곡선 또는 다각형, 근사 정확도 위한 값( = 오차), True 이면 폐곡선, False 이면 양 끝 열린 곡선)
    approx = cv2.approxPolyDP(cont, cv2.arcLength(cont, True)*0.05, True)   # 소수 바꾸기
    # print(approx)
    vtc = len(approx)
    cv2.imshow('vtc', vtc)

    if vtc == 4 and cv2.contourArea(cont) > 15000:
        (x, y, w, h) = cv2.boundingRect(cont)
        pt1 = (x, y)
        pt2 = (x + w, y + h)
        co = cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)  #--> 이미지에 초록색 네모 그리는 코드
        # cv2.putText(img, 'Rec', (pt1[0], pt1[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))    # --> 그려진 네모 위에 글자 입력

        cv2.imshow('cv', co)
cv2.imshow('binary', thr)
cv2.imshow('result', result)

cv2.waitKey()
cv2.destroyAllWindows()


################## 경기장 자르기 ##################

x_min, x_max = pt1[0], pt2[0]
print(x_min)
print(x_max)

y_min, y_max = pt1[1], pt2[1]
print(y_min)
print(y_max)


# image trim 하기
x = x_min
y = y_min
w = x_max-x_min
h = y_max-y_min

img_trim = img[y:y+h, x:x+w]

cv2.imshow('img_trim', img_trim)

cv2.waitKey()
cv2.destroyAllWindows()


##################################### 장애물 검출 ############################################

image = img_trim

image_height, image_width, _ = image.shape

hsv_ori = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)    # 이미지 색상 hsv로 받아오기

lower_blue = np.array([90, 100, 0])
upper_blue = np.array([150, 255, 255])

mask_blue_ori = cv2.inRange(hsv_ori, lower_blue, upper_blue)    # blue 색상 받아오기 (hsv)

result_ori = cv2.bitwise_and(image, image, mask=mask_blue_ori)


kernel_ori = cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
blur_ori = cv2.GaussianBlur(mask_blue_ori, ksize=(5,5), sigmaX=0)
edged_ori = cv2.Canny(blur_ori, 100, 250)
closed_ori = cv2.morphologyEx(edged_ori, cv2.MORPH_CLOSE, kernel_ori)

contours_ori, _ = cv2.findContours(closed_ori.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours_image_ori = cv2.drawContours(image, contours_ori, -1, (0, 0, 255), 6)  # 끝에 숫자 바꾸면 영역 커짐

result_ori[mask_blue_ori == 0] = (0, 0, 0)

# cv2.imshow('closed_ori', closed_ori)
# cv2.imshow('mask_ori', mask_blue_ori)
# cv2.imshow('result_ori', result_ori)
cv2.imshow('contours_ori', contours_image_ori)

######################################################

hsv = cv2.cvtColor(contours_image_ori, cv2.COLOR_BGR2HSV)

mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

result = cv2.bitwise_and(contours_image_ori, contours_image_ori, mask=mask_blue)


kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
blur = cv2.GaussianBlur(mask_blue, ksize=(5,5), sigmaX=0)
edged = cv2.Canny(blur, 100, 250)
closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)


contours, _ = cv2.findContours(closed.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
contours_image = cv2.drawContours(contours_image_ori, contours, -1, (0, 255, 0), 2)

result[mask_blue == 0] = (0, 0, 0)

# cv2.imshow('closed', closed)
# cv2.imshow('mask', mask_blue)
# cv2.imshow('result', result)
cv2.imshow('contours', contours_image)

########################### 장애물 좌표 ###########################

k = cv2.waitKey(1) & 0xFF

cv2.waitKey(0)
cv2.destroyAllWindows()

contour_x_li = []
contour_y_li = []
contour_li = []
for i in range(len(contours)):
    for j in range(len(contours[i])):
        contour_x_li.append(contours[i][j][0][0])
        contour_y_li.append(contours[i][j][0][1])
        contour_li.append([contours[i][j][0][0], contours[i][j][0][1]])
print(contour_li)


cv2.waitKey(0)

plt.axis([0, image_width,3,image_height])
plt.scatter(contour_x_li, contour_y_li,c='r',s=1)
plt.show()



########################### 경로 탐색 ###########################

pygame.init()

#GAME Parameters
screen = pygame.display.set_mode([image_width+20, image_height+250]) # 이미지 자체 크기 +100
GAME_x = min(contour_x_li)
GAME_y = min(contour_y_li)
GAME_width = image_width  # 이미지 자체의 크기로 잡고, capture width, height
GAME_height = image_height
GAME_border = 3
WHITE=(255,255,255)
BLUE=(0,0,255)
BLACK=(0,0,0)
RED=(255,0,0)
GREEN=(0,255,0)
custom_color_1=(10,145,80)
screen.fill(WHITE)
INT_MAX = 100000000000000
#Class Definitions
class Button:
    def __init__ (self, colour, x, y, width, height):
        self.colour = colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    def create(self,screen):
        pygame.draw.rect(screen, self.colour, [self.x, self.y, self.width, self.height])


#Function Definition : Point inside Game ?
def point_inside_game(x,y):
    if x>GAME_x+GAME_border and x<GAME_x + GAME_width - GAME_border:
                if y>GAME_y+GAME_border and y < GAME_y + GAME_height - GAME_border:
                    return(True)
    return(False)


#Function Definition : Random Point Generator inside Game
def random_point():
    x_random = ri(GAME_x+GAME_border , GAME_x + GAME_width - GAME_border - 1)
    y_random = ri(GAME_y+GAME_border , GAME_y + GAME_height - GAME_border - 1)
    return((x_random, y_random))


#Function Definition : Point inside given Rectangle ?
def point_inside_rec(xr,yr,wr,hr,x,y):
    if x> xr and x < xr + wr:
                if y > yr and y < yr + hr:
                    return(True)
    return(False)


#Function Definition : Point to Point Distance
def p2p_dist(p1,p2):
    x1,y1=p1
    x2,y2=p2
    return ( ( (x1-x2)**2 + (y1-y2)**2 )**0.5 )


#Function Definition : Text on Button
def ClickText():
    font = pygame.font.Font('freesansbold.ttf', 12)
    text = font.render('CLICK HERE', True, WHITE)
    textRect = text.get_rect()
    textRect.center = (75, 380)
    screen.blit(text, textRect)


#Function Definition : Description Text
def DesText(s,x=315,y=485):
    pygame.draw.rect(screen,WHITE,(125,470,500,30))
    font = pygame.font.SysFont('segoeuisemilight', 15)
    text = font.render('%s'%(s), True, BLACK)
    textRect = text.get_rect()
    #textRect.center = (255, 460)
    textRect.center = (x, y)
    screen.blit(text, textRect)


#Function Definition :RRT Algorithm
def RRT(x,y,parent):
    if (x,y) not in parent and screen.get_at((x,y)) != (0,0,0,255):
        x_m,y_m = -1, -1
        cur_min=INT_MAX
        for v in parent:
            if p2p_dist(v,(x,y))<cur_min:
                x_m,y_m=v
                cur_min = p2p_dist(v,(x,y))

        good = True
        ans=[]
        if abs(x_m - x)<abs(y_m-y):
            if y_m<y:
                for u in range(y_m+1, y+1):
                    x_cur = int (((x_m - x)/(y_m - y))*( u - y) + x)
                    y_cur = u
                    if screen.get_at((x_cur,y_cur)) == (0,0,0,255):
                        good=False
                        break
                if good:
                    ans=[int (((x_m - x)/(y_m - y))*( y_m+Step - y) + x),y_m+Step]
            else:
                for u in range(y, y_m):
                    x_cur = int(((x_m - x)/(y_m - y))*( u - y) + x)
                    y_cur = u
                    if screen.get_at((x_cur,y_cur)) == (0,0,0,255):
                        good=False
                        break
                if good:
                    ans=[int (((x_m - x)/(y_m - y))*( y_m-Step - y) + x),y_m-Step]

        else:
            if x_m<x:
                for u in range(x_m + 1, x+1):
                    x_cur = u
                    y_cur = int( ((y_m-y)/(x_m-x))*(u-x) + y )
                    if screen.get_at((x_cur,y_cur)) == (0,0,0,255):
                        good=False
                        break
                if good:
                    ans=[x_m+Step,int( ((y_m-y)/(x_m-x))*(x_m+Step-x) + y ) ]
            else:
                for u in range(x , x_m):
                    x_cur = u
                    y_cur = int( ((y_m-y)/(x_m-x))*(u-x) + y )
                    if screen.get_at((x_cur,y_cur)) == (0,0,0,255):
                        good=False
                        break
                if good:
                    ans=[x_m-Step,int( ((y_m-y)/(x_m-x))*(x_m-Step-x) + y ) ]
        return(good,x_m,y_m,ans)
    return(False,-1,-1,[])

running = True
#Button for Game
pygame.draw.rect(screen,BLACK,(GAME_x,GAME_y,GAME_width,GAME_height),GAME_border)
B1 = Button(BLACK, 25, 500, 200, 50)
B1.create(screen)
OBS=dict()

#Number of forward Steps towards random sampled point
Step = 10
#Start stores a single point [Starting point- RED Point]
Start=[]

#End stores a set of destination point [Destination point- Green Point]
#Multiple points allowed to make the point appear bigger, and fast discovery,
#due to huge number of pixels in this game
End=set()


#parent stores the graph
parent=dict()

level=1
ClickText()
DesText("Instruction :", y = 400)
DesText("CLICK WHITE Part, then CLICK BLACK Button", y = 420)

obstacle_li =[]
xo_li = []
yo_li = []

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if running == False:
            break
        m = pygame.mouse.get_pressed()
        x,y = pygame.mouse.get_pos()

        if m[0] == 1:
            if point_inside_rec(B1.x,B1.y, B1.width, B1.height,x,y):
                    # print("BUTTON", level)
                    if level==1 and Start==[]:
                        level+=1
                        B1.colour=RED
                        DesText("Draw the Starting point, then CLICK RED Button")
                    elif level==2 and Start:
                        level+=1
                        B1.colour=GREEN
                        DesText("Draw the Destination point, then CLICK GREEN Button")
                    if level==3 and End!=set():
                        level+=1
                        B1.colour=BLUE
                        DesText("Path is being explored using RRT Algorithm")
                    B1.create(screen)
                    ClickText()
                    continue
            elif level==1:
                for each_contour_point in contour_li:
                    x, y = each_contour_point[0], each_contour_point[1]
                    if point_inside_game(x,y):
                        pygame.draw.circle(screen, BLACK, (x,y), 1)
            elif level == 2 and Start==[]:
                if point_inside_game(x,y):
                    #print("START ",x,y)
                    Start=(x,y)
                    pygame.draw.circle(screen, RED, (x, y), 5)
            elif level == 3:
                if point_inside_game(x,y):
                    #print("END ",x,y)
                    End.add((x,y))
                    pygame.draw.circle(screen, GREEN, (x, y), 10)

        if level>=4:
            running = False
            break
    pygame.display.update()




running = True
parent[Start]=(0,0)
Trace=[]
Timer = time.time()
while(running):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    x,y =random_point()
    if (time.time() - Timer) > 5:
        Step=5
    good,x_m,y_m,ans=RRT(x,y,parent)

    if good and ans:
        x_cur = ans[0]
        y_cur = ans[1]
        if screen.get_at((x_cur,y_cur)) != (0,0,0,255) and (x_cur,y_cur) not in parent:
            parent[(x_cur,y_cur)]=(x_m,y_m)
            if screen.get_at((x_cur,y_cur)) == (0, 255, 0, 255):
                Trace=(x_cur,y_cur)
                #print("End", x_cur, y_cur)
                running = False
            pygame.draw.line(screen, BLUE, (x_cur,y_cur), (x_m,y_m), 2)
    pygame.display.update()

running = True
#This loop gets the route back to Start point

x_li = []
y_li = []

while(Trace and running):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    while (Trace!=Start):
        l =[]
        x,y = parent[Trace]
        pygame.draw.line(screen, GREEN, (x,y), Trace, 2)
        Trace=(x,y)
        l.append(Trace)
        print(l)
        x_li.append(x)
        y_li.append(-y+GAME_height)


    DesText("Green Colored Path is the Required Path")
    pygame.display.update()

#Quit the Game

print(x_li)
print(y_li)
plt.axis([0, GAME_width,0,GAME_height])
plt.plot(x_li,y_li,'b')
plt.show()
pygame.quit()
