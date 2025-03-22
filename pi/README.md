# yoga-with-friends raspberry pi 

Uses content persisted by [events.py](../backend/events.py) to render onto an LED grid

## Setup
### Install Submodule
```bash
ssh pi@yogapi.local
git submodule update --init
make -C rpi-rgb-led-matrix/examples-api-use
```

### Install Cron
[Setup backend](../backend/README.md) before running the `publish_yoga_events.sh ` cron
```bash
crontab -e
@reboot /home/pi/yoga-with-friends/pi/render_next_yoga_class.sh
* * * * * /home/pi/yoga-with-friends/backend/publish_yoga_events.sh
```

## BOM
- [Raspberry Pi w/ male headers (or similar)](https://www.adafruit.com/product/6008) and power 
  supply
- [MPC1073](http://www.electrodragon.com/product/rgb-matrix-panel-drive-board-raspberry-pi/) and CR1220 battery
- 16+ GB SD card, and card reader / writer
- [32x16 LED matrix](https://www.adafruit.com/product/420) with ribbon and 5 Volt 2 Amp power 
  supply (or solder to a 3 AMP raspberry pi power supply at your own risk)

## Debugging
Can turn rendering on the pi on and off using 
```bash
python events.py --force_render NO
python events.py --force_render YES
```
