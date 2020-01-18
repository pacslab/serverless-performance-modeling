#! /bin/bash

# Generate the requirements for the whole repo
ALLREQSFILE="requirements.txt"
cat ../deployments/requirements.txt > $ALLREQSFILE
echo "" >> $ALLREQSFILE
cat ../experiments/requirements.txt >> $ALLREQSFILE

# Build the container
IMAGE_NAME=$(cat .dockername)
echo "Image Name: $IMAGE_NAME"
docker build -t $IMAGE_NAME -f jupyter_docker/Dockerfile ..