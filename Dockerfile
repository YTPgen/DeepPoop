FROM python:3.7-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1. \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg 

ADD . /deep_poop
WORKDIR /deep_poop
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt 