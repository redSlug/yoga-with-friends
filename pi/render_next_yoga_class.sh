#!/bin/bash

MAX_LOG_FILE_SIZE=250000000
WORKING_DIR=/home/pi/yoga-with-friends/pi
LOG_FILE=/home/pi/yoga-with-friends/log
BANNER_IMAGE_FILE="yoga.ppm"
POLLING_DELAY=10
SHOULD_RENDER_FILE="render.txt"

function rotate_logs_if_needed {
    log_file_size=$(du -b log | tr -s '\t' ' ' | cut -d' ' -f1)

    if [ $log_file_size -gt $MAX_LOG_FILE_SIZE ];then
        log_to_file "Rotating log file of size $log_file_size bytes"
        mv $LOG_FILE "$LOG_FILE.backup"
        touch $LOG_FILE
    fi
}


function log_to_file {
    echo "$(date) $1" >> log
}

function cleanup {
    log_to_file "Clearing LED display"
    sudo pkill demo
    exit
}

function should_render_ppm {
  if grep -q "True" "$SHOULD_RENDER_FILE"; then
      should_render=0
  else
      should_render=1
  fi
  echo "should_render = $should_render"
  return $should_render
}


function main {
    pushd $WORKING_DIR
    while true; do
        sudo pkill demo
        if should_render_ppm;
        then
          sudo rpi-rgb-led-matrix/examples-api-use/demo -D 1 yoga.ppm --led-no-hardware-pulse --led-rows=16 --led-cols=32 -m 0 --led-daemon --led-brightness=20
        fi
        rotate_logs_if_needed
        sleep $POLLING_DELAY
    done
    popd
}

trap cleanup EXIT
main
