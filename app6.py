import numpy as np
import cv2
import time
from switch import TestThreading
import os
from watch import Watcher,TimeLimit
from camera_thread import VideoStreamWidget
from just import predict
from pinreq import pin
import pymysql
import requests
from datetime import datetime
from asset import get_dict

w = Watcher(0)
t = TimeLimit()

def sendtoserver(frame):
    imencoded = cv2.imencode(".jpg", frame)[1]
    file = {'image': ('image.jpg', imencoded.tobytes(), 'image/jpeg', {'Expires': '0'})}
    s = time.time()
    response = requests.post(os.getenv('MODEL_URL'), files=file, timeout=5) #3.110.0.141:5000
    e = time.time()
    j = response.json()
    result = [i for i in j if i['confidence'] > 0.6 and i['class'] == 0]
    return result,round(e-s,2)

## AWS RDS CONFIG START

rds_host = os.getenv('RDS_URL')
rds_user = os.getenv('RDS_USER')
rds_pass = os.getenv('RDS_PASS')
rds_db = os.getenv('RDS_DB')

conn = pymysql.connect(host= rds_host,port = 3306,user = rds_user, password = rds_pass,db = rds_db)


def insert_details(mimetype,name,count,time):
    cur=conn.cursor()
    cur.execute("INSERT INTO firstlast(mimetype,name,count,time) VALUES (%s,%s,%s,%s)", (mimetype,name,count,time))
    conn.commit()

def get_details():
    cur=conn.cursor()
    cur.execute("SELECT *  FROM firstlast")
    details = cur.fetchall()
    return details

## AWS RDS CONFIG END


if __name__ == "__main__":
    src = os.getenv('STREAM_SRC') #175.101.82.215:1024/Streaming/Channels/502
    
    video_stream_widget = VideoStreamWidget(src)
    time.sleep(1)

    while True:

        #count = predict(video_stream_widget.frame)
        try:
            result,it = sendtoserver(video_stream_widget.frame)
        except:
            print('Video stream not detected')
            time.sleep(10)
            continue
        count = len(result)
        #print(it)


        if count is None:
            time.sleep(10)
            continue

        watch = w.variable < count
        print(watch,w.variable,count,it)


        # if count >= 1 and watch:
        #     time.sleep(duration(os.getenv('SCREENLY_ASSET'+3))
        #     TestThreading(os.getenv('SCREENLY_ASSET'))
        #     insert_details(os.getenv('SCREENLY_ASSET'),count,datetime.now())
        
                
        if count >= 1 and watch:
            #pin('on',[21,26])
            try:
                data_dict = get_dict(os.getenv('DEVICE_ID'),os.getenv('SCREENLY_ASSET'))
            except:
                print('Asset List is unavailable')
                time.sleep(10)
                continue
            mimetype = data_dict['mimetype']
            name = data_dict['name']
            duration = int(data_dict['duration'])
            if t.check_value() > duration:
                TestThreading(os.getenv('SCREENLY_ASSET'))
                print('request sent')
                insert_details(mimetype,name,count,datetime.now())
                #pin('off',[21,26])
                t = TimeLimit(int(time.time()))
            else:
                insert_details(None,None,count,datetime.now())


        w.check_value(count)
        #video_stream_widget.show_frame()
        #key = cv2.waitKey(1)
        #if key & 0xFF == ord('q'):
            #break#root@ip-172-31-42-87:/home/ubuntu/audio-test1#
