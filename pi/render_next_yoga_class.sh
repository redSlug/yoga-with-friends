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
      echo "returning 0"
      return 0
  fi
  echo "returning 1"
  return 1
}


function main {
    pushd $WORKING_DIR
    IS_RENDERING=1
    while true; do
        SHOULD_RENDER=1
        echo "SHOULDRENDER$SHOULD_RENDER"

        SHOULD_RENDER=${should_render_ppm}
        echo "SHOULDRENDER$SHOULD_RENDER"

        ## if SHOULD_RENDER and NOT IS_RENDERING
        if [ "$SHOULD_RENDER" -eq 0 ] && [ "$IS_RENDERING" -eq 1 ]; then
          sudo rpi-rgb-led-matrix/examples-api-use/demo -D 1 yoga.ppm --led-no-hardware-pulse --led-rows=16 --led-cols=32 -m 0 --led-daemon --led-brightness=10
          IS_RENDERING=0
        fi

        ## if NOT SHOULD_RENDER and IS_RENDERING
        if [ "$SHOULD_RENDER" -eq 1 ] && [ "$IS_RENDERING" -eq 0 ]; then
          sudo pkill demo
          IS_RENDERING=1
        fi

        rotate_logs_if_needed
        sleep $POLLING_DELAY
    done
    popd
}

trap cleanup EXIT
main
