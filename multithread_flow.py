#!/usr/bin/env python

'''
example to show optical flow

USAGE: opt_flow.py [<video_source>]

Keys:
 1 - toggle HSV flow visualization
 2 - toggle glitch

Keys:
    ESC    - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv
import queue
import video
import time
from threading import Thread, Event
from multiprocessing import Process, Queue
import os

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (_x2, _y2) in lines:
        cv.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis


def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    hsv[...,2] = np.minimum(v*4, 255)
    bgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    return bgr


def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv.remap(img, flow, None, cv.INTER_LINEAR)
    return res

def producer(pipeline,e):
    import sys
    try:
        fn = sys.argv[1]
    except IndexError:
        fn = 0

    cam = video.create_capture("brno/video.avi")
    frame = 102780
    cam.set(cv.CAP_PROP_POS_FRAMES, frame-1)
    previmg =  img = cam.read()[1]
    previmg = img = cv.resize(img, (1280,720), interpolation = cv.INTER_AREA)
    index = 0
    while True:
        if(pipeline.qsize() > 100):
            time.sleep(10)
            print("sleeping")
            continue
        _ret, img = cam.read()
        _ret, img = cam.read()
        if(not _ret):
            e.set()
            break
        img = cv.resize(img, (1280,720), interpolation = cv.INTER_AREA)
        index += 1
        pipeline.put((index,previmg,img))
        previmg = img
        
        # print("put message")
    return

def consumer(prod,cons,e):
    init = 0
    print("e set" + str(e.isSet()))
    while not e.isSet() or not prod.empty():
        # if(init == 0):
        #     prevgray =  gray = cv.cvtColor(prod.get(), cv.COLOR_BGR2GRAY)
        #     init = 1
        #     continue
        index, previmg, img = prod.get()
        # print("message received")
        prevgray = cv.cvtColor(previmg, cv.COLOR_BGR2GRAY)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        cons.put((index,flow))
    return

def saver(cons,e):
    out = cv.VideoWriter('output_brno_5_left.avi', cv.VideoWriter_fourcc(*'mp4v'), 50.0, (1280,720))
    ctr = 0
    index = 0
    list_flows = []
    while not e.isSet() or not cons.empty():
        if(not cons.empty()):
            list_flows.append(cons.get())
        for item in list_flows:
            if item[0] == (index + 1): 
                index += 1
                hsv = draw_hsv(item[1])
                out.write(hsv)
                # cv.imshow("sa",hsv)
                # cv.waitKey(5)
                if(ctr%20==0):
                    print(ctr)
                ctr += 1
                list_flows.remove(item)
                break
    out.release()
    return

def main():
    # import sys
    # try:
    #     fn = sys.argv[1]
    # except IndexError:
    #     fn = 0

    # cam = video.create_capture(fn)
    # _ret, prev = cam.read()
    cpu_count = os.cpu_count()
    
    producer_pipeline = Queue()
    consumer_pipeline = Queue()
    e = Event()
    prod_ = Process(target = producer, args = (producer_pipeline,e))
    consumers = []
    for i in range(cpu_count-2):
        consumers.append(Process(target = consumer, args = (producer_pipeline,consumer_pipeline,e)))
    # cons_ = Process(target = consumer, args = (producer_pipeline,consumer_pipeline,e))
    saver_ = Process(target = saver, args = (consumer_pipeline,e))
    prod_.start()
    for item in consumers:
        item.start()
    saver_.start()
    prod_.join()
    for item in consumers:
        item.join()
    saver_.join()
    # prevgray = cv.cvtColor(prev, cv.COLOR_BGR2GRAY)
    # show_hsv = False
    # show_glitch = False
    # cur_glitch = prev.copy()

    # while True:
    #     _ret, img = cam.read()
    #     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #     flow = cv.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    #     prevgray = gray

    #     cv.imshow('flow', draw_flow(gray, flow))
    #     if show_hsv:
    #         cv.imshow('flow HSV', draw_hsv(flow))
    #     if show_glitch:
    #         cur_glitch = warp_flow(cur_glitch, flow)
    #         cv.imshow('glitch', cur_glitch)

    #     ch = cv.waitKey(5)
    #     if ch == 27:
    #         break
    #     if ch == ord('1'):
    #         show_hsv = not show_hsv
    #         print('HSV flow visualization is', ['off', 'on'][show_hsv])
    #     if ch == ord('2'):
    #         show_glitch = not show_glitch
    #         if show_glitch:
    #             cur_glitch = img.copy()
    #         print('glitch is', ['off', 'on'][show_glitch])

    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()
