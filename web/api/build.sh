#! /bin/bash

# Copying pacsltk to this folder
cp -R ../../pacsltk ./pacsltk
cp -R ../../docs ./src/static

# Build the container
IMAGE_NAME=$(cat .dockername)
echo "Image Name: $IMAGE_NAME"
docker build -t $IMAGE_NAME -f Dockerfile .

# remove pacsltk from this folder
rm -R pacsltk
rm -R src/static
