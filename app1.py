import numpy as np
import cv2
import time
import pymysql
import os
from flask import Flask,jsonify
from datetime import datetime
from multiprocessing import Process, Value
import multiprocessing
from itertools import cycle
import ast


from camera_thread import VideoStreamWidget # to access camera using threading for framerate
from switch import TestThreading  # to switch asset audio or video or image using API
from watch import Watcher,TimeLimit  # to watch the changes of person count variable 
from just import predict # to predict using object detection API from tensorflow serving
from pinreq import pin_control # API to on or off the gpio pins


time_limit = int(os.getenv('TIME_LIMIT'))
## AWS RDS CONFIG START

rds_host = os.getenv('RDS_URL')
rds_user = os.getenv('RDS_USER')
rds_pass = os.getenv('RDS_PASS')
rds_db = os.getenv('RDS_DB')

conn = pymysql.connect(host= rds_host,port = 3306,user = rds_user, password = rds_pass,db = rds_db)


def insert_details(id,count,time):
    cur=conn.cursor()
    cur.execute("INSERT INTO firstlast(id,just,fake) VALUES (%s,%s,%s)", (id,count,time))
    conn.commit()

def get_details():
    cur=conn.cursor()
    cur.execute("SELECT *  FROM firstlast")
    details = cur.fetchall()
    return details

## AWS RDS CONFIG END

app = Flask(__name__)


w = Watcher(0) #Initiate Watcher class

# BIND PINS TO REQUIRED ASSET
bind = ast.literal_eval(os.getenv('BIND'))
cycle_bind = cycle(bind)


def next_bind():
    return next(cycle_bind)


src = os.getenv('STREAM_SRC')
asset = os.getenv('SCREENLY_ASSET')


def record_loop(loop_on):
    t = TimeLimit()
    video_stream_widget = VideoStreamWidget(src) #Intiate VideoStreamWidget class
    time.sleep(1)
    number = 0

    while True:
        if loop_on.value == True:

            count = predict(video_stream_widget.frame) #access camera frame and pass it to predict function

            if count is None:
                time.sleep(10)
                continue

            watch = w.variable < count #access watch variable and compare with present person count
            print(watch,w.variable,count)

            if count >= 1 and watch and t.check_value() > time_limit:

                    # pin('on',[21,26])
                    p = next_bind()[1]
                    p1 = multiprocessing.Process(target=pin_control, args=(35,p))
                    p1.start()
                    TestThreading(asset)
                    print('request sent')
                    # time.sleep(35)
                    # pin('off',[21,26])
                    t = TimeLimit(int(time.time()))
                    number += 1
                    insert_details(number,count,datetime.now())

            w.check_value(count)
            video_stream_widget.show_frame()
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            



@app.route('/hello')
def hello():
    return 'hello world'



@app.route('/', methods=['GET'])
def get_tasks():
   data = get_details()
   return jsonify(data)



if __name__ == "__main__":
   # multai processing for camera stream and flask app
   recording_on = Value('b', True)
   p = Process(target=record_loop, args=(recording_on,))
   p.start()
   app.run(debug=True, use_reloader=False)
   p.join()
