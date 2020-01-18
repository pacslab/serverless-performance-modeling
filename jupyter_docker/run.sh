#! /bin/bash

IMAGE_NAME=$(cat .dockername)
TARGET_PORT=8888
cd ..
docker run -it --rm \
    -p $TARGET_PORT:8888 \
    -e JUPYTER_ENABLE_LAB=yes \
    --name slsperf \
    -v "$(pwd)":/home/jovyan \
    $IMAGE_NAME
