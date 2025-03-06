#!/bin/bash

# crontab -e
# @reboot /home/pi/shader-leds/render.sh

MAX_LOG_FILE_SIZE=250000000
WORKING_DIR=/home/pi/shader-leds
LOG_FILE=/home/pi/shader-leds/log
BANNER_IMAGE_FILE="yoga.ppm"
POLLING_DELAY=2m


function log_to_file {
    echo "$(date) $1" >> log
}

function cleanup {
    log_to_file "Clearing LED display"
    sudo pkill demo
    exit
}

function rotate_logs_if_needed {
    log_file_size=$(du -b log | tr -s '\t' ' ' | cut -d' ' -f1)

    if [ $log_file_size -gt $MAX_LOG_FILE_SIZE ];then
        log_to_file "Rotating log file of size $log_file_size bytes"
        mv $LOG_FILE "$LOG_FILE.backup"
        touch $LOG_FILE
    fi
}

function main {
    pushd $WORKING_DIR

    while true; do
        wget -N https://s3.us-east-2.amazonaws.com/yoga-with-friends.com/$BANNER_IMAGE_FILE
        if [ $? -eq 0 ];
        then
            log_to_file "wget succeeded"
            sudo pkill demo
            sudo rpi-rgb-led-matrix/examples-api-use/demo -D 1 yoga.ppm --led-no-hardware-pulse --led-rows=16 --led-cols=32 -m 0 --led-daemon --led-brightness=50
        else
            log_to_file "wget failed - file was likely not modified"

            if [ ! -f $BANNER_IMAGE_FILE ]; then
                log_to_file "File not found!"
                exit 1
            fi
        fi

        rotate_logs_if_needed
        sleep $POLLING_DELAY
    done

    popd
}

trap cleanup EXIT
main
