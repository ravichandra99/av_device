import numpy as np
import cv2
import time
from switch import TestThreading
import os
from watch import Watcher,TimeLimit
from camera_thread import VideoStreamWidget
from just import predict
from pinreq import pin
from duration import duration
import requests
from facelib import FaceDetector, AgeGenderEstimator
import pymysql
from datetime import datetime

face_detector = FaceDetector()
age_gender_detector = AgeGenderEstimator()


def sendtoserver(frame):
    imencoded = cv2.imencode(".jpg", frame)[1]
    file = {'image': ('image.jpg', imencoded.tobytes(), 'image/jpeg', {'Expires': '0'})}
    s = time.time()
    response = requests.post(os.getenv('MODEL_URL'), files=file, timeout=5) #3.110.0.141:5000
    e = time.time()
    j = response.json()
    result = [i for i in j if i['confidence'] > 0.6 and i['class'] == 0]
    return result,round(e-s,2)

w = Watcher(0)
# t = TimeLimit()

## AWS RDS CONFIG START

rds_host = os.getenv('RDS_URL')
rds_user = os.getenv('RDS_USER')
rds_pass = os.getenv('RDS_PASS')
rds_db = os.getenv('RDS_DB')
site = os.getenv('SITE_ID')
device = os.getenv('DEVICE_ID')
conn = pymysql.connect(host= rds_host,port = 3306,user = rds_user, password = rds_pass,db = rds_db)


def insert_details(genders,ages,id,count,time,device,site):
    cur=conn.cursor()
    #cur.executemany("INSERT INTO firstlast(mimetype,count,time) VALUES (%s,%s,%s)",[(str(id),str(count),str(time))])
    cur.executemany("INSERT INTO firstlast(genders,ages,mimetype,count,time,device_id,site_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",[(str(genders),str(ages),str(id),str(count),str(time),str(device),str(site))])
    conn.commit()

def get_details():
    cur=conn.cursor()
    cur.execute("SELECT *  FROM firstlast")
    details = cur.fetchall()
    return details

## AWS RDS CONFIG END

if __name__ == "__main__":
    src = os.getenv('STREAM_SRC') if os.getenv('STREAM_SRC') != "0" else 0  #175.101.82.215:1024/Streaming/Channels/502

    video_stream_widget = VideoStreamWidget(src)
    time.sleep(5)

    while True:
        #print(video_stream_widget.frame)
        result,it = sendtoserver(video_stream_widget.frame)
        count = len(result)

        if count is None:
            print('None')
            time.sleep(10)
            continue

        watch = w.variable < count
        print(it,count)

        if count >= 1 and watch: #and t.check_value() > 40:
                #TestThreading(os.getenv('SCREENLY_ASSET_COUNT'))
                #time.sleep(duration(os.getenv('SCREENLY_ASSET_COUNT'))+3)


                try:
                    faces, boxes, scores, landmarks = face_detector.detect_align(video_stream_widget.frame)
                    # pin('on',[21,26])
                    
                    genders, ages = age_gender_detector.detect(faces)
                    z = tuple(zip(genders,ages))
                    g = genders.count('Male') > genders.count('Female')
                    ages_males = [ y for x, y in z if x  == 'Male' ]
                    ages_females = [ j for i, j in z if i  == 'Female' ]
                    classifications_M = [(i//10 + 1) for i in ages_males]
                    classifications_F = [(i//10 + 1) for i in ages_females]
                    try:
                        m = max(classifications_M,key=classifications_M.count)
                        f= max(classifications_F,key=classifications_F.count)
                    except:
                        m = ''
                        f = ''
                    
                    if g:
                        print(genders, ages)
                        print('M_playing ad..')
                        TestThreading(os.getenv('SCREENLY_ASSET_M'+str(m)))
                        time.sleep(duration(os.getenv('SCREENLY_ASSET_M'+str(m)))+1)
                        
                    else:
                        print(genders, ages)
                        print('F_playing ad..')
                        TestThreading(os.getenv('SCREENLY_ASSET_F'+str(f)))
                        time.sleep(duration(os.getenv('SCREENLY_ASSET_F'+str(f)))+1)
                    insert_details(genders,ages,it,count,datetime.now(),device,site)

                            
                    
                except:
                    print(None)
                    print('N_playing ad..')
                    TestThreading(os.getenv('SCREENLY_ASSET_AMLE'))
                    time.sleep(duration(os.getenv('SCREENLY_ASSET_AMLE'))+1)
                    genders=None
                    ages=None
                    insert_details(genders,ages,it,count,datetime.now(),device,site)

            
                    


                
                # print('request sent')
                # pins on/off time gap
                # pin('off',[21,26])
                # t = TimeLimit(int(time.time()))

        # w.check_value(count)
        video_stream_widget.show_frame()
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
