#! /bin/bash

# Generate the requirements for the whole repo
ALLREQSFILE="requirements.txt"
cat ../deployments/requirements.txt > $ALLREQSFILE
echo "" >> $ALLREQSFILE
cat ../experiments/requirements.txt >> $ALLREQSFILE

# Copying pacsltk to this folder
cp -R ../pacsltk ./pacsltk

# Build the container
IMAGE_NAME=$(cat .dockername)
VERSION=$(python -u pacsltk/version.py)
echo "Image Name: $IMAGE_NAME"
docker build -t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:latest -f Dockerfile .

# remove pacsltk from this folder
rm -R pacsltk
