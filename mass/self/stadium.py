import pygame
from random import randint as ri
import time
import matplotlib.pyplot as plt
import cv2
import numpy as np

# cap = cv2.VideoCapture(0)
# capture = 0

# while True:
#     ret, frame = cap.read()

#     if ret:
#         cv2.imshow('frame', frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break
#     elif cv2.waitKey(33) & 0xFF == 26:
#         capture = frame
#         cv2.imshow('capture', capture)

# cap.release()
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# 경로 설정할 이미지 캡쳐

# ------------------------------------------------------------------------------------------------------

# 이미지 좌표화
# 이미지

image = cv2.imread("/Users/wooyeongkam/mass/self/stadium2.png")


image_height, image_width, _ = image.shape

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower_blue = np.array([0, 0, 0])
upper_blue = np.array([240, 240, 240])

mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

result = cv2.bitwise_and(image, image, mask=mask_blue)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
blur = cv2.GaussianBlur(mask_blue, ksize=(5,5), sigmaX=0)
edged = cv2.Canny(blur, 10, 250)
closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours_image = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

result[mask_blue == 0] = (0, 0, 0)

cv2.imshow('mask', mask_blue)
cv2.imshow('result', result)
cv2.imshow('contours', contours_image)

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

# cv2.waitKey(0)

plt.axis([0, image_width,0,image_height])
plt.plot(contour_x_li, contour_y_li,'r')
plt.show()

pygame.init()

#GAME Parameters
screen = pygame.display.set_mode([image_width+50, image_height+300]) # 이미지 자체 크기 +100
GAME_x = 20
GAME_y = 40
GAME_width = image_width # 이미지 자체의 크기로 잡고, capture width, height
GAME_height = image_height # 좌표 위아래, 옆 최대 좌표로 크기 맞추기 
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
    textRect.center = (75, 495)
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
B1 = Button(BLACK, 25, 470, 100, 50)
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
DesText("Instruction :",y=460)
DesText("CLICK WHITE Part, then CLICK BLACK Button")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if running==False:
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
                        #print("OBSTABLE ",x,y)
                        OBS[(x,y)]=1  # 아마도 장애물 리스트 넣는 곳인듯
                        pygame.draw.circle(screen, BLACK, (x, y),5)
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
        x,y = parent[Trace]
        pygame.draw.line(screen, GREEN, (x,y), Trace, 2)
        Trace=(x,y)
        x_li.append(x)
        y_li.append(-y+GAME_height)


    DesText("Green Colored Path is the Required Path")
    pygame.display.update()

#Quit the Game

path_li = []
for i in range(len(x_li)):
    path_li.append([x_li[i], y_li[i]])
path_li.reverse()
print('------------------------------------------------')
print(path_li)
plt.axis([0, GAME_width,0,GAME_height])
plt.plot(x_li,y_li,'r')
plt.show()
pygame.quit()