# Docker Container with Jupyter Notebook for The Serverless Performance Model

## Building

To build, simply run the build script:

```sh
chmod +x build.sh
./build.sh
```

## Running
In case you want to work with the files in this repository, you can just use the run script:

```sh
chmod +x ./run.sh
./run.sh
```

To run the docker container for another directory, change into the directory you want to use 
(e.g., `cd ..` in the following example) , then
use the following to run the Jupyter Lab:

```sh
IMAGE_NAME=$(cat .dockername)
TARGET_PORT=8890
# The folder you want to be mounted into the container:
cd ..
docker run -it --rm \
    -p $TARGET_PORT:8888 \
    -e JUPYTER_ENABLE_LAB=yes \
    --name slsperf \
    -v "$(pwd)":/home/jovyan \
    $IMAGE_NAME
```

Now you can use your browser to launch the jupyter lab associated with this repo. Copy the URL you see,
but replace the port `8888` with what you specified as the `TARGET_PORT`.

Now, you can launch a terminal and run any of the python files in the repo.
