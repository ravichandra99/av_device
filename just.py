from PIL import Image
import numpy
import json
import requests
import os
import dot


def predict(img):
    np_img = numpy.array(img)
    payload = {"instances": [np_img.tolist()]}


    url = os.getenv("MODEL_URL")

    r = requests.post(url,json = payload)

    r1 = json.loads(r.text)

    try:

        r2 = dict(zip(r1['predictions'][0]['detection_scores'],r1['predictions'][0]['detection_classes']))

    except:

        print(r1)

        return None

    r3 = [i for i in r2 if i > 0.8 and r2[i] == 1.0]

    return len(r3)

if __name__ == '__main__':
    import cv2

    test = cv2.imread('test.jpg')
    img = Image.open('test.jpg')
    res = predict(img)
    print(res)
