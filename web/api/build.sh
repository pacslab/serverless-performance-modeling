#! /bin/bash

# Copying pacsltk to this folder
cp -R ../../pacsltk ./pacsltk
cp -R ../../docs ./src/static

# Build the container
IMAGE_NAME=$(cat .dockername)
VERSION=$(python -u pacsltk/version.py)
echo "Image Name: $IMAGE_NAME"
docker build -t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:latest -f Dockerfile .

# remove pacsltk from this folder
rm -R pacsltk
rm -R src/static
