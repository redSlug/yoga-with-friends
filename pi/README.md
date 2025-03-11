# yoga-with-friends raspberry pi 

```bash
# takes up to 20 seconds to copy
scp output.ppm pi@jampi.local:~/

ssh pi@jampi.local
sudo rpi-rgb-led-matrix/examples-api-use/demo -D 1 output.ppm --led-no-hardware-pulse --led-rows=16 --led-cols=32 -m 0 --led-brightness=50
```
