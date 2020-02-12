#! /bin/bash

IMAGE_NAME=$(cat .dockername)
docker run -it --rm -p 5000:5000 --name slsperfapi $IMAGE_NAME
