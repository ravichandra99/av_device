# syntax=docker/dockerfile:1
FROM python:3.8-slim
ADD . /code
WORKDIR /code
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt
CMD ["python", "app6.py"]
