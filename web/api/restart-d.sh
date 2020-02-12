#! /bin/bash

./rm.sh

IMAGE_NAME=$(cat .dockername)
docker pull $IMAGE_NAME

./run-d.sh
