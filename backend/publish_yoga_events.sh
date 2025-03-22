#!/bin/bash

pushd /home/pi/yoga-with-friends/backend
VENV_PATH="venv"
SCRIPT_PATH="events.py"
source "$VENV_PATH/bin/activate"
python "$SCRIPT_PATH"
deactivate
popd
