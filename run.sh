#!/bin/bash

###########
# PURPOSE #
###########
# Convenient wrapper for running SportDP Helper
# For a list of possible arguments, run
# $ ./run.sh --help

# enable bash strict mode
set -eu

BASEDIR="$( dirname "$0")"

last="${@:$#}" # last parameter
other="${*%${!#}}" # all parameters except the last

if [ -e "$last" ]; then
    data="data/scratch/data.xls"
    cp "$last" "$BASEDIR/$data"
    last="./data/scratch/data.xls"
fi

cd "$BASEDIR"

# prepare graceful exit
function finish {
	sudo docker-compose down
}
trap finish EXIT


# build
sudo docker-compose build
# start selenium
sudo docker-compose up --detach selenium
sleep 3

# start vnc (ignore errors)
echo "Starting vnc client"
vinagre 127.0.0.1:5901 2>/dev/null || true &

# run sportdb-helper
sudo docker-compose run \
    --rm \
    --name sportdb-helper-container \
    -v $(pwd)/data:/sportdb-helper/data \
    sportdb-helper $last $other
