#!/bin/bash

###########
# PURPOSE #
###########
# Convenient wrapper for running SportDP Helper

BASEDIR="$( dirname "$0")"
cd "$BASEDIR"

# enable display forwarding for selenium
# https://stackoverflow.com/questions/25281992/alternatives-to-ssh-x11-forwarding-for-docker-containers
xhost +si:localuser:$USER

sudo docker run \
    --rm \
    -it \
    --name sportdb-helper-container \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    sportdb-helper "$@"