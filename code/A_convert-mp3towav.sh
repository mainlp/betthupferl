#!/bin/bash
# __author__ bplank
# __date__ 29.10.2024
# __descr__ Convert mp3 to wav
mkdir -p audio
file=$1 
ffmpeg -i $1 ../audio/`basename $1 | sed s'/.mp3//'`.wav


