import jetson.inference
import jetson.utils
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.gstCamera(1280, 720, "/dev/video0")
display = jetson.utils.glDisplay()

while display.IsOpen():
    frame, width, height = camera.CaptureRGBA(zeroCopy=1)
    detections = net.Detect(frame, width, height)
    display.RenderOnce(frame, width, height)
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

    frame = jetson.utils.cudaToNumpy(frame, width, height, 4)
    ret, frame = display.read()

    testmode = 1

    def make_chunks(EdgeArray, size_of_chunk):
        chunks = []
        for i in range(0, len(EdgeArray), size_of_chunk):  # 0 ~ EdgeArray size 만큼 size_of_chunk 만큼 커지면서
            chunks.append(EdgeArray[i:i + size_of_chunk])  # chunks 리스트에 EdgeArray 추가 [i ~ i + size_of_chunk]
        return chunks
    
   
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #lower_orange = np.array([1, 100, 100])
    #upper_orange = 

    lower_green = np.array([0, 255, 0])  # 초록색 (Yolo 검출)
    upper_green = np.array([0, 255, 0])

    mask_green = cv2.inRange(rgb, lower_green, upper_green)  # 초록색 범위 add

    mask = cv2.inRange(rgb, lower_green, upper_green)

    res = cv2.bitwise_and(frame, frame, mask=mask)  # 기존 이미지에 색깔 추출 이미지 덮어씌움
    red = red = cv2.cvtColor(red, cv2.COLOR_HSV2RGB)  # BGR 타입으로 변환

    ####################################################################################

    ret, thresh = cv2.threshold(mask, 40, 255, 0)  # 이미지 내에서 경계 찾기
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    lower_yellow = np.array([255, 255, 0])  # 노란색
    upper_yellow = np.array([255, 255, 0])

    mask_yellow = cv2.inRange(rgb, lower_yellow, upper_yellow)
    yellow = cv2.bitwise_and(frame, frame, mask=mask_yellow)  # 기존 이미지에 색깔 추출 이미지 덮어씌움
    res1 = yellow = cv2.cvtColor(yellow, cv2.COLOR_HSV2RGB)

    # 픽셀 돌면서 --> 그려진 contours 의 contour_area 구하기 --> if 면적 () 이상이면 --> 해당 contours 그리기
    for cont in contours:
        if cv2.contourArea(cont) > 500.0:  # 숫자 바꾸기
            cv2.drawContours(yellow, cont, -1, (0, 255, 255), 1)


    ####################################################################################

    original_frame = frame.copy()
    red_frame = frame.copy()
    img_edgerep = frame.copy()
    img_contour = frame.copy()
    img_navigation = frame.copy()

    blur = cv2.bilateralFilter(res1, 9, 40, 40)
    edges = cv2.Canny(blur, 50, 100)

    img_edgerep_h = img_edgerep.shape[0] - 1
    img_edgerep_w = img_edgerep.shape[1] - 1

    EdgeArray = []
    StepSize = 5

    # edge --> frame 에 초록선 그리기 (stepSize 간격으로)
    for j in range(0, img_edgerep_w, StepSize):  # FOR loop along the width of the image with given stepsize.
        pixel = (j, 0)  # If no edge found in column this value will be stored in edgearray.
        for i in range(img_edgerep_h - 5, 0, -1):  # FOR loop along the height of the image.
            if edges.item(i, j) == 255:  # Checking for edges.
                pixel = (j, i)
                break
        EdgeArray.append(pixel)  # EgdeArray 리스트에 stepSize 간격의 초록선 pixel 추가

    # img_edgerep
    # 초록 선 높이(y)
    for x in range(len(
            EdgeArray) - 1):
        cv2.line(img_edgerep, EdgeArray[x], EdgeArray[x + 1], (0, 255, 0), 1)  # EdgeArray

    for x in range(len(
            EdgeArray)):
        cv2.line(img_edgerep, (x * StepSize, img_edgerep_h), EdgeArray[x], (0, 255, 0), 1)

    # draw contours.

    blurred_frame = cv2.bilateralFilter(res1, 9, 75, 75)
    gray = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 106, 255, 1)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img_edgerep, contours, -1, (0, 0, 255), 3)

    # Code to decide direction of navigation

    number_of_chunks = 3
    size_of_chunk = int(len(EdgeArray) / number_of_chunks)
    chunks = make_chunks(EdgeArray, size_of_chunk)
    avg_of_chunk = []
    for i in range(len(chunks) - 1):
        x_vals = []
        y_vals = []
        for (x, y) in chunks[i]:  # x, y 평균
            x_vals.append(x)
            y_vals.append(y)
        avg_x = int(np.average(x_vals))
        avg_y = int(np.average(y_vals))
        avg_of_chunk.append([avg_y, avg_x])
        cv2.line(frame, (int(img_edgerep_w / 2), img_edgerep_h), (avg_x, avg_y), (255, 255, 0), 2)  # navigation 양옆선

    forwardEdge = avg_of_chunk[1]
    cv2.line(frame, (int(img_edgerep_w / 2), img_edgerep_h), (forwardEdge[1], forwardEdge[0]), (0, 255, 0),
             3)  # navigation 중앙선
    farthest_point = (min(avg_of_chunk))
    # print(farthest_point)

    if forwardEdge[0] > 20:  # 여기 바꿔
        if farthest_point[1] < 310:
            direction = "left"
            print(direction)
        else:
            direction = "right"
            print(direction)
    else:
        direction = "forward"
        print(direction)

    turn_message = direction
    rospy.loginfo(turn_message)
    pub.publish(turn_message)

        # Code to display the results

    if testmode == 1:
        font = cv2.FONT_HERSHEY_SIMPLEX
        navigation = cv2.putText(frame, direction, (275, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("T", res1)
        cv2.imshow("Navigation", navigation)



    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows
VideoSignal.release()
