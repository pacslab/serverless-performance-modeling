#! /bin/bash

IMAGE_NAME=$(cat .dockername)
cd ..
chmod +w experiments/figs
docker run -it --rm \
    --name slsperftest \
    -v "$(pwd)":/home/jovyan \
    $IMAGE_NAME /bin/bash -c 'cd experiments && python 01-parse-plot.py && python 02-overall-plots.py && ls figs/'
