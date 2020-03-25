import cv2 as cv
import pandas as pd
import numpy as np
import os
from multiprocessing import Process

def worker(frame_start,frame_end,proc_id):
    print("process : ", proc_id)
    df = pd.read_csv("boxes_data_2.csv")
    cam = cv.VideoCapture("output3.avi")
    frame = frame_start
    data = []
    while True:
        _ret, img = cam.read()
        # print(img.shape)
        if(_ret == False):
            break
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        # print(hsv.shape)
        temp_df = df[(df.frame == frame)]
        for index,row in temp_df.iterrows():
            x1 = int(row['x'])
            y1 = int(row['y'])
            x2 = x1 + int(row['w'])
            y2 = y1 + int(row['h'])
            if(x1 < 0):
                x1 = 0
            if(y1 < 0):
                y1 = 0
            if(x2 >= 1920):
                x2 = 1919
            if(y2 >= 1080):
                y2 = 1079
            for x in range(x1,x2,1):
                for y in range(y1,y2,1):
                    try:
                        r,g,b = img[y,x]
                        h,v = hsv[y,x,0], hsv[y,x,2]
                    except:
                        print("ERROR COORDINATES")
                        print(x,y)
                        print(row)
                        return
                    if(h == 0 and v == 0):
                        continue
                    data.append([x,y,r,g,b,h,v,row['speed']])
        frame +=1
        if(frame % 20 == 0):
            if(len(data) > 0):
                df_s = pd.DataFrame(data)
                df_s.to_csv("dataset3/dataset3_"+str(proc_id)+".csv",mode='a', index=False)
                data.clear()
                data = []
            print(frame)
        if(frame == frame_end):
            break
def main():

    cpu_count = os.cpu_count()
    frames = 6918
    frame_div = int(frames/cpu_count)
    workers = []
    frame_start = -frame_div
    frame_end = 0
    proc_id = 0
    for i in range(cpu_count):
        frame_start = frame_start + frame_div
        frame_end = frame_end + frame_div - 1
        if(frame_end > frames):
            frame_end = frames-1
        workers.append(Process(target = worker, args = (frame_start,frame_end, proc_id)))
        proc_id += 1
    for i in workers:
        i.start()
    for i in workers:
        i.join()

    return

if __name__ == '__main__':
    main()