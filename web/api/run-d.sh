#! /bin/bash

IMAGE_NAME=$(cat .dockername)
docker run -d -p 5000:5000 --name slsperfapi $IMAGE_NAME
