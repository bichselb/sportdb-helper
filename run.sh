#!/bin/bash

###########
# PURPOSE #
###########
# Convenient wrapper for running SportDP Helper

BASEDIR="$( dirname "$0")"

last="${@:$#}" # last parameter
other="${*%${!#}}" # all parameters except the last

if [ -e "$last" ]; then
    data="data/scratch/data.xls"
    cp "$last" "$BASEDIR/$data"
    last="./data/scratch/data.xls"
fi

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
    -v $(pwd)/data:/sportdb-helper/data \
    sportdb-helper $last $other