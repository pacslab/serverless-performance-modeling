#! /bin/bash

IMAGE_NAME=$(cat .dockername)
docker push $IMAGE_NAME
