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

from facelib import FaceDetector, AgeGenderEstimator

face_detector = FaceDetector()
age_gender_detector = AgeGenderEstimator()


w = Watcher(0)
t = TimeLimit()

if __name__ == "__main__":
    #src = os.getenv('STREAM_SRC') #175.101.82.215:1024/Streaming/Channels/502

    video_stream_widget = VideoStreamWidget(0)
    time.sleep(1)

    while True:

        count = predict(video_stream_widget.frame)

        if count is None:
            print('None')
            time.sleep(10)
            continue

        watch = w.variable < count
        print(watch,w.variable,count)

        if count >= 1 and watch and t.check_value() > 40:
                TestThreading(os.getenv('SCREENLY_ASSET_COUNT'))
                time.sleep(duration(os.getenv('SCREENLY_ASSET_COUNT'))+3)


                try:
                    faces, boxes, scores, landmarks = face_detector.detect_align(video_stream_widget.frame)
                    # pin('on',[21,26])
                    
                    genders, ages = age_gender_detector.detect(faces)
                    z = tuple(zip(genders,ages))
                    g = genders.count('Male') > genders.count('Female')
                    if g:
                        TestThreading(os.getenv('SCREENLY_ASSET_M'))
                        time.sleep(duration(os.getenv('SCREENLY_ASSET_M'))+3)
                        ages_males = [ y for x, y in z if x  == 'Male' ]
                        classifications = [(i//10 + 1) for i in ages_males]
                        r = max(classifications,key=classifications.count)
                        try:
                            TestThreading(os.getenv('SCREENLY_ASSET_M'+str(r)))
                            time.sleep(duration(os.getenv('SCREENLY_ASSET_M'+str(r)))+3)
                        except:
                            TestThreading(os.getenv('SCREENLY_ASSET_AMLE'))
                            time.sleep(duration(os.getenv('SCREENLY_ASSET_AMLE'))+3)

                    else:
                        TestThreading(os.getenv('SCREENLY_ASSET_F'))
                        time.sleep(duration(os.getenv('SCREENLY_ASSET_COUNT'))+3)
                        ages_females = [ y for x, y in z if x  == 'Female' ]
                        classifications = [(i//10 + 1) for i in ages_females]
                        r = max(classifications,key=classifications.count)
                        try:
                            TestThreading(os.getenv('SCREENLY_ASSET_F'+str(r)))
                            time.sleep(duration(os.getenv('SCREENLY_ASSET_F'+str(r)))+3)
                        except:
                            TestThreading(os.getenv('SCREENLY_ASSET_AMLE'))
                            time.sleep(duration(os.getenv('SCREENLY_ASSET_AMLE'))+3)
                            
                    print(genders, ages)
                except:
                    TestThreading(os.getenv('SCREENLY_ASSET_AMLE'))
                    time.sleep(duration(os.getenv('SCREENLY_ASSET_AMLE'))+3)


                
                print('request sent')
                # pins on/off time gap
                # pin('off',[21,26])
                t = TimeLimit(int(time.time()))

        w.check_value(count)
        video_stream_widget.show_frame()
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break