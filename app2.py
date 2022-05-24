import numpy as np
import cv2
import time
from switch import TestThreading
import os
from watch import Watcher,TimeLimit
from camera_thread import VideoStreamWidget
from just import predict
from pinreq import pin_control
import ast
import multiprocessing
from itertools import cycle


w = Watcher(0)
t = TimeLimit()
bind = ast.literal_eval(os.getenv('BIND'))
cycle_bind = cycle(bind)


def next_bind():
    return next(cycle_bind)


if __name__ == "__main__":
    src = os.getenv('STREAM_SRC') #175.101.82.215:1024/Streaming/Channels/502

    video_stream_widget = VideoStreamWidget(src)
    time.sleep(1)
    number = 0

    while True:

        count = predict(video_stream_widget.frame)

        if count is None:
            time.sleep(10)
            continue

        watch = w.variable < count
        print(watch,w.variable,count)

        if count >= 1 and watch and t.check_value() > 40:
                asset = os.getenv('SCREENLY_ASSET')
                p = next_bind()[1]
                print(p)
                p1 = multiprocessing.Process(target=pin_control, args=(35,p))
                p1.start()
                TestThreading(asset)
                print('request sent')
                t = TimeLimit(int(time.time()))
                number += 1
                print(number)


        w.check_value(count)

        video_stream_widget.show_frame()
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break