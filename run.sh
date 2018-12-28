#!/bin/bash

###########
# PURPOSE #
###########
# Convenient wrapper for running SportDP Helper

BASEDIR="$( dirname "$0")"
cd "$BASEDIR"

# sudo docker run --expose=4444  sportdb-helper "$@"


sudo docker run \
    -rm \
    -p 5901:5900 \
    -v /dev/shm:/dev/shm \
    -e VNC_NO_PASSWORD=1 \
    --name $(CONTAINER) \
    sportdb-helper "$@"