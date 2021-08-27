import cv2
import numpy as np
from urllib.request import urlopen
import imutils
import time
import os

##################################################################################################################

url = 2



# YOLO 가중치 파일과 CFG 파일 로드
YOLO_net = cv2.dnn.readNet("yolov3_final2.weights", "yolov3-tiny.cfg")

# YOLO NETWORK 재구성
classes = []

# 클래스의 갯수만큼 랜덤 RGB 배열을 생성

with open("obj.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in YOLO_net.getUnconnectedOutLayers()]
print(classes)


# 웹캠 프레임
VideoSignal = cv2.VideoCapture(url)

while (VideoSignal.isOpened()):
    #VideoSignal.open(url)  # 무선통신 시 필요
    ret, frame = VideoSignal.read()
    frame = imutils.resize(frame, width=800)
    h, w, c = frame.shape

    # YOLO 입력
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    YOLO_net.setInput(blob)
    outs = YOLO_net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:

            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.3:
                # Object detected
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                dw = int(detection[2] * w)
                dh = int(detection[3] * h)
                # Rectangle coordinate
                x = int(center_x - dw / 2)
                y = int(center_y - dh / 2)
                boxes.append([x, y, dw, dh])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.45, 0.4)

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            try:
                label = classes[i]
                # print('label', label)
                score = confidences[i]
            except:
                print('IndexError')

            # 경계상자와 클래스 정보 이미지에 입력
            if label == classes[0]:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
            elif label == classes[1]:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
            elif label == classes[2]:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)


    ##################################################################################################################

    testmode = 1


    def make_chunks(EdgeArray, size_of_chunk):
        chunks = []
        for i in range(0, len(EdgeArray), size_of_chunk):  # 0 ~ EdgeArray size 만큼 size_of_chunk 만큼 커지면서
            chunks.append(EdgeArray[i:i + size_of_chunk])  # chunks 리스트에 EdgeArray 추가 [i ~ i + size_of_chunk]
        return chunks

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    lower_green = np.array([0, 255, 0])  # 초록색 (Yolo 검출)
    upper_green = np.array([0, 255, 0])

    mask_green = cv2.inRange(rgb, lower_green, upper_green)  # 초록색 범위 add

    mask = cv2.inRange(rgb, lower_green, upper_green)

    red = cv2.bitwise_and(frame, frame, mask=mask)  # 기존 이미지에 색깔 추출 이미지 덮어씌움
    res = red = cv2.cvtColor(red, cv2.COLOR_HSV2BGR)  # BGR 타입으로 변환

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
        print(cv2.contourArea(cont))
        if cv2.contourArea(cont) > 50000.0:  # 숫자 바꾸기
            cv2.drawContours(yellow, cont, -1, (0, 255, 255), 1)

    cv2.imshow('mask_yellow', res1)

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

    if forwardEdge[0] > 10:  # 여기 바꿔
        if farthest_point[1] < 310:
            direction = "Move left"
            print(direction)
        else:
            direction = "Move right"
            print(direction)
    else:
        direction = "Move forward"
        print(direction)

        # Code to display the results

    if testmode == 1:
        cv2.imshow("Original_Frame", original_frame)
        cv2.imshow("color_Frame", res)
        cv2.imshow("Canny", edges)
        cv2.imshow("Threshold", thresh)
        cv2.imshow("Edge_separation", img_edgerep)
        font = cv2.FONT_HERSHEY_SIMPLEX
        navigation = cv2.putText(frame, direction, (275, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Navigation", navigation)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows
VideoSignal.release()



