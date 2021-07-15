from math import *
import math

## 두 점 사이의 거리
def point_to_point_distance(p1, p2):
    return sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)


##3점을 통해서 각도를 구하는 코드 ->  #base start = p1, base end = p2, other = p3
def angle_base (p1, p2, p3):
    dis_a = point_to_point_distance(p2, p3)
    dis_b = point_to_point_distance(p1, p3)
    dis_c = point_to_point_distance(p1, p2)
    degree = abs(degrees(acos((dis_b**2 + dis_c**2 - dis_a**2)/(2 * dis_b * dis_c))))
    z_vector = vector_z_cor(p1,p2,p3)
    if (z_vector >0):
        degree = -degree
    return degree

##base의 점을 잡기 위해서 기울기를 집어넣고, x를 집어 넣어주어야 함 ## start = p1, end = p2
def extend_end_point (p1, p2):
    slope = slope_dot(p1, p2)
    base_end_x = 0
    base_end_y = 0
    if (p1[0] > p2[0]):
        base_end_x = p2[0] - 20
        base_end_y = slope * base_end_x + (p2[1]-(p2[0]*slope))
    elif (p1[0] < p2[0]):
        base_end_x = p2[0] + 20
        base_end_y = slope * base_end_x + (p2[1]-(p2[0])*slope)
    elif (p1[0] == p2[0]):
        if (p2[1] < p1[1]):
            base_end_x = p2[0]
            base_end_y = p2[1] - 10
        elif(p2[1] > p1[1]):
            base_end_x = p2[0]
            base_end_y = p2[1] + 10
    p_extend = [base_end_x, base_end_y]
    return p_extend

##base의 점을 잡기 위해서 기울기를 집어넣고, x를 집어 넣어주어야 함 ## start = p1, end = p2
def y_end_point (p1, p2):
    base_end_x = 0
    base_end_y = 0
    if (p1[0] > p2[0]):
        base_end_x = p2[0]
        base_end_y = p2[1] + 20
    elif (p1[0] < p2[0]):
        base_end_x = p2[0]
        base_end_y = p2[1] + 20
    elif (p1[0] == p2[0]):
        if (p2[1] < p1[1]):
            base_end_x = p2[0]
            base_end_y = p2[1] + 10
        elif(p2[1] > p1[1]):
            base_end_x = p2[0]
            base_end_y = p2[1] + 10
    p_extend = [base_end_x, base_end_y]
    return p_extend

#start = p1, end = p2
def slope_dot (p1, p2) :
    if ((p2[0] - p1[0]) != 0 ) :
        slope = (p2[1] - p1[1])/(p2[0] - p1[0])
    else :
        slope = 999999 ##  기울기를 구한때 (y2-y1) / (x2-x1) 인데 x2랑 x1이 같으면 기울기가 무한대라고 가정한다.
    return slope

def extend_li_change(): # 기준선을 연장해서 우리가 heading angle이 우리의 목표와 일직선이 된다고 가정했을때 다음목표까지의 원하는 각도
    j = extend_math_range.pop(0)
    extend_math_li_trash[0] = p_collection[j + 1]  # 문제 -> 2번째 경로부터는 괜찮은데 첫번째 경로는 기준선이 말썽임 #######해결~? 컨펌 받자
    extend_math_li_trash[1] = extend_end_point(p_collection[j], p_collection[j + 1])
    extend_math_li_trash[2] = p_collection[j + 2]  # 문제를 해결하기 위해서 첫 베이스를 임의로 지정해서 list에 지정해줌 그래서 이런식으로 됨 ######해결?~? 컨펌 받자

def y_li_change(): # 라이더의 각도가 y축 기준이므로 목표까지의 angle이 y축을 기반으로 했을 때 생기는 각도
    j = y_math_range.pop(0)
    y_math_li_trash[0] = p_collection[j + 1]  # 문제 -> 2번째 경로부터는 괜찮은데 첫번째 경로는 기준선이 말썽임 #######해결~? 컨펌 받자
    y_math_li_trash[1] = y_end_point(p_collection[j], p_collection[j + 1])
    y_math_li_trash[2] = p_collection[j + 2]  # 문제를 해결하기 위해서 첫 베이스를 임의로 지정해서 list에 지정해줌 그래서 이런식으로 됨 ######해결?~? 컨펌 받자

def vector_z_cor (p1, p2, p3): ####3점을 통해서 각도를 구하는 코드 ->  #base start = p1, base end = p2, other = p3
    a_vector = [(p2[0] - p1[0]), (p2[1] - p1[1]), 0]
    b_vector = [(p3[0] - p1[0]), (p3[1] - p1[1]), 0]
    z_vector = a_vector[0] * b_vector[1] - a_vector[1] * b_vector[0]
    return z_vector

def max_speed_select (p_real_time_li): ## 실시간 좌표를 대입시키면 각각 목표지점과의 거리의 차를 계산 후에 모터 최대값을 리턴RR
    distance_list = []
    for i in (p_collection):
        distance_list.append(point_to_point_distance(i, p_real_time_li))
    if (min(distance_list) < 500):
        print("모터 최댓값을 10으로 맞춥니다.")##############지울것
        return 5
    elif (min(distance_list)<1000):
        print("모터 최댓값을 20으로 맞춥니다.")##############지울것
        return 10
    else:
        print("모터 최댓값을 40으로 맞춥니다.")  ##############지울것
        return 20

def temporary_heading_angle(jjj):##그냥 임시로 확인하기 위한 함수이다. 라이더로 heading angle을 가져온다면 이 함수는 없애주자
    heading_angle = []
    angle_math_li_trash.append([400,400])
    for i in range(len(angle_math_li_trash)-1):
        partial_x = (angle_math_li_trash[i + 1][0] - angle_math_li_trash[i][0])
        heading_distance = point_to_point_distance(angle_math_li_trash[i], angle_math_li_trash[i + 1])
        if (heading_distance != 0):
            heading_angle.append((180/pi) * asin(partial_x/heading_distance))
        else: #############################################################################################################################이거 어떻게 할까?
            heading_angle.append((180 / pi) * asin(partial_x / 100))
    print("heading angle : ", heading_angle[jjj])##############지울것
    return heading_angle[jjj]

##RR은 모터 최대 출력, heading_angle은 라이더로 얻어낼 값(y축이 기준이다), y_base_angle은 y축 기준 다음목표까지의 변해야 할 각도이다. extend_base_angle은 우리가 원하는 angle
## return 값은 [왼쪽모터,오른쪽모터] 출력이다.
def return_motor_result(RR, extend_base_angle ,jjj, y_base_angle): ###jjj는 나중에 heading_angle 받아올때 바꿔보도록 하자
    motor=[0,0]
    heading_angle = temporary_heading_angle(jjj)
    heading_object_angle = y_base_angle - heading_angle
    if (y_base_angle != 0):
        if (extend_base_angle>=0):
            motor[0] = RR * (1 + 1 * (heading_object_angle / y_base_angle))
            motor[1] = RR * (1 - 1 * (heading_object_angle / y_base_angle))
        else:
            motor[0] = RR * (1 - 1 * (heading_object_angle / y_base_angle))
            motor[1] = RR * (1 + 1 * (heading_object_angle / y_base_angle))
    else:##각도가 0도 일때도 있다. ############################################################################################ 이거 어떻게 할까???????????????????????
        if (extend_base_angle>=0):
            motor[0] = RR * (1 + 1 * (heading_object_angle / 180))
            motor[1] = RR * (1 - 1 * (heading_object_angle / 180))
        else:
            motor[0] = RR * (1 - 1 * (heading_object_angle / 180))
            motor[1] = RR * (1 + 1 * (heading_object_angle / 180))
    return motor

##-> 이제 자동으로 base_end_point가 들어가도록 코딩해야된다.
#p_real_time이 실시간으로 들어갈 배가 가지는 실제 좌표, p_collection이 리스트 들의 리스트
def automatic_angle_distance (p_real_time):
    motor_power = []
    jjj=0
    for i in p_real_time:
        p_real_time_li = i
        extend_base_angle = angle_base(extend_math_li_trash[0], extend_math_li_trash[1], extend_math_li_trash[2])  #angle_base(p1,p2,p3) -> p1은 기준 출발점, p2는 기준 끝점, p3는 목표점
        y_base_angle = angle_base(y_math_li_trash[0], y_math_li_trash[1], y_math_li_trash[2])
        want_distance = point_to_point_distance(p_real_time_li, extend_math_li_trash[2])
        RR = max_speed_select(i)
        motor_power = return_motor_result(RR,extend_base_angle,jjj ,y_base_angle)
        jjj = jjj + 1
        result = [extend_base_angle, want_distance]
        print("기준 각도 : [" , result[0] , "] 목표까지 거리 : [" , result[1] , "]")
        print("좌측 모터 값 : [" , motor_power[0] , "] 우측 모터 값 : [" , motor_power[1] , "]")
        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        if (want_distance < 500):  # 1은 cm단위이다.
            extend_li_change()
            y_li_change()
            print("목표물이 바뀌었습니다.")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")


def mapToGrid(lat, lon):
    ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > PI :
        theta -= 2.0 * PI
    if theta < -PI :
        theta += 2.0 * PI
    theta *= sn
    x = (ra * math.sin(theta)) + xo
    y = (ro - ra * math.cos(theta)) + yo
    x = int(x + 1.5)
    y = int(y + 1.5)
    return [x, y]

def real_map_grid(lat, lon):
    base_math_li = []
    for i in base_coordinate:
        base_math_li.append(mapToGrid(i[0], i[1]))
    math_li = mapToGrid(lat, lon)
    angle = radians(angle_base(base_math_li[0],[base_math_li[0][0],base_math_li[0][1] + 100],base_math_li[1])) ##3점을 통해서 각도를 구하는 코드 ->  #base start = p1, base end = p2, other = p3
    x = cos(angle) * math_li[0] - sin(angle) * math_li[1]
    y = sin(angle) * math_li[0] + cos(angle) * math_li[1]
    return [x,y]

Re = 637100877.0     ##  지도반경
grid = 1.0          ##  격자간격 (cm)
slat1 = 30.0        ##  표준위도 1
slat2 = 60.0        ##  표준위도 2
olon = 129.257919       ##  기준점 경도
olat = 35.545082       ##  기준점 위도
xo = 0 / grid   ##  기준점 X좌표
yo = 0 / grid  ##  기준점 Y좌표
first = 0


if first == 0 :
    PI = math.asin(1.0) * 2.0
    DEGRAD = PI/ 180.0
    RADDEG = 180.0 / PI
    re = Re / grid
    slat1 = slat1 * DEGRAD
    slat2 = slat2 * DEGRAD
    olon = olon * DEGRAD
    olat = olat * DEGRAD
    sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(PI * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(PI * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    first = 1

p_collection = []
extend_math_range = []
y_math_range = []

location_list = [[35.545154,129.258177],[35.545387,129.257807],[35.545516,129.258320],[35.545708,129.257970],[35.545511, 129.258026],[35.545154,129.258177]] #1.목표물의 순서(경로)
## - > 목표물 경로 위도,경도를 입력해준다.
base_coordinate = [[35.545082,129.257919], [35.545651,129.257714]]
##수조의 벽면의 좌표를 입력하자 [0] -> base_strat, [1] -> base_end
for i in location_list:
    p_collection.append(real_map_grid(i[0], i[1]))

direction_list = [p_collection[0], [p_collection[0][0],1000], p_collection[1]]

print(p_collection)

#실시간으로 좌표 하나하나씩 받아오면 없어도 될 것들이다. 왜냐하면 pop함수를 썻기 때문에

extend_math_li_trash = direction_list
y_math_li_trash = direction_list
for i in range(len(p_collection)-2):
    extend_math_range.append(i)
for i in range(len(p_collection)-2):
    y_math_range.append(i)
################################
#while(True):
    ## p_real_time = [50, 50] -> 우리가 실시간으로 받아올 좌표임
    #    p_real_time = [[470, 20], [470, 260], [350, 500], [240, 640], [230, 910], [250, 1220], [130, 1380], [30, 1470],
    #                   [290, 1540], [420, 1460], [560, 1500], [760, 1460], [880, 1460], [960, 1460], [840, 1850], [740, 2050],
    #                  [710, 2340], [610, 2490], [540, 2780], [490, 3070], [490, 3300], [500, 3490], [450, 3140], [440, 2820],
    #                  [470, 2540], [470, 2180], [460, 1920], [490, 1630], [480, 1480], [470, 1180], [470, 960], [490, 740], [490, 500], [490, 330],
    #                  [490, 180], [490, 40], [410, 480], [330, 900], [210, 1180], [170, 1410], [100, 1640], [0, 1750]]
    #
    #    angle_math_li_trash = p_real_time
    #
    #   a = automatic_angle_distance(p_real_time)
    #
#  print(a)