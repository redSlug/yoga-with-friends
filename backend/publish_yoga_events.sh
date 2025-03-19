#!/bin/bash

# crontab -e
# * * * * * /home/pi/yoga-with-friends/backend/publish_yoga_events.sh

pushd /home/pi/yoga-with-friends/backend
VENV_PATH="venv"
SCRIPT_PATH="events.py"
source "$VENV_PATH/bin/activate"
python "$SCRIPT_PATH"
deactivate
popd
