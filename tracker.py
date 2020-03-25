import cv2 as cv
import pandas as pd

df = pd.read_csv("Set03_video01.csv")
cam = cv.VideoCapture("Set03_video01.h264")
frame = 0
# initBB = (int(df.iloc[0]['x']),int(df.iloc[0]['y']),int(df.iloc[0]['w']),int(df.iloc[0]['h']))
# tracker = cv.TrackerCSRT_create()
# tracking = False
# while True:
#     _ret, img = cam.read()
#     if(_ret == False):
#         break
#     if(frame == df.iloc[0]['frame_start']):
#         tracker.init(img, initBB)
#         tracking = True    
#     if tracking:
#         (success, box) = tracker.update(img)
#         if success:
#             (x, y, w, h) = [int(v) for v in box]
#             img = cv.rectangle(img, (x, y), (x + w, y + h),(0, 255, 0), 2)
#     cv.imshow("f",img)
#     cv.waitKey(5)
#     frame+=1
#     if(frame>100):
#         break

trackers = []
to_delete = []
boxes = []
while True:
    _ret, img = cam.read()
    if(_ret == False):
        break
    temp_df = df[(df.frame_start == frame)]
    if(temp_df is not None):
        for index,row in temp_df.iterrows():
            x = int(row['x'])
            if(x > 200):
                x = int(row['x'])-200
            y = int(row['y'])-400
            w = 3*int(row['w'])
            h = 6*int(row['h'])
            print(x,y+400)
            bbox = cv.selectROI(img, False)
            print("selected")
            initBB = (x,y,w,h)
            speed = float(row['speed'])
            tracker = cv.TrackerCSRT_create()
            tracker.init(img, bbox)
            failure_rate = 0
            trackers.append([tracker,int(row['frame_end'])-10,speed,failure_rate])
    if(len(trackers) > 0):
        for idx, item in enumerate(trackers):
            if(frame > item[1] or item[3]>4):
                to_delete.append(idx)
    if(len(to_delete) > 0):
        for item in to_delete:
            trackers.pop(item)
        to_delete = []
    for tracker_ in trackers:
        (success, box) = tracker_[0].update(img)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            speed = tracker_[2]
            boxes.append([frame,x,y,w,h,speed])
            # img = cv.rectangle(img, (x, y), (x + w, y + h),(0, 255, 0), 2)
        else:
            tracker_[3] +=1
    # cv.imshow('f',img)
    # cv.waitKey(5)
    frame += 1 
    if(frame%200==0):
        print(frame)
        # print("kength of trackers" + str(len(trackers)))
        # print("kength of to_delete" + str(len(to_delete)))

df = pd.DataFrame(boxes)
df.to_csv("boxes_data_3.csv",index=False,header=['frame','x','y','w','h','speed'])