import pandas as pd
import cv2 as cv

frame = 0
df = pd.read_csv("boxes_data_1.csv")


cam = cv.VideoCapture("Set01_video01.h264")
out = cv.VideoWriter('box.avi', cv.VideoWriter_fourcc(*'mp4v'), 30.0, (1920,1080))
while True:
    _ret, img = cam.read()
    if(_ret == False):
        break
    temp_df = df[(df.frame == frame)]
    for index,row in temp_df.iterrows():
        x1 = int(row['x'])
        y1 = int(row['y'])
        x2 = x1 + int(row['w'])
        y2 = y1 + int(row['h'])
        speed = str(row['speed'])
        print(x1,y1,x2,y2)
        img = cv.rectangle(img, (x1, y1), (x2, y2), (36,255,12), 1)
        cv.putText(img, speed, (x1, y1-10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
    out.write(img)
    frame += 1
    if(frame%1000 ==0):
        print(frame)

    cv.imshow("frame",img)
    cv.waitKey(5)
out.release()
cv.destroyAllWindows()