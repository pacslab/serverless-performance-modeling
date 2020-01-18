#! /bin/bash

IMAGE_NAME=$(cat .dockername)
DOCKER_USER=${DOCKER_USER:-jovyan}
cd ..
docker run -it --rm \
    --name slsperftest \
    -v "$(pwd)":/home/jovyan \
    --user $DOCKER_USER \
    $IMAGE_NAME /bin/bash -c 'cd experiments && python 01-parse-plot.py && python 02-overall-plots.py && ls figs/'
