#!/bin/bash

# prerequisites:
# sudo apt install -y ffmpeg

# source: https://unix.stackexchange.com/questions/35282/convert-ogv-video-to-gif-animation

INPUT=in-action.ogv
OUTPUT=in-action.gif
TMP=output_tmp

BASEDIR="$( dirname "$0")"

cd "$BASEDIR"

mkdir -p $TMP

# ffmpeg -i $INPUT $OUTPUT

# exit

FPS=15
WIDTH=1000
ffmpeg -i $INPUT -vf fps=$FPS,scale=$WIDTH:-1:flags=lanczos,palettegen $TMP/tmp_palette.png
ffmpeg -y -i $INPUT -i $TMP/tmp_palette.png -loop 0 -filter_complex "fps=$FPS,scale=$WIDTH:-1:flags=lanczos[x];[x][1:v]paletteuse" $OUTPUT

# cleanup
rm -r $TMP
