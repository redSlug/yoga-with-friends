# yoga-with-friends

A tool to get friends to attend yoga together. Exports yoga events to a calendar for your friends to subscribe to and a PPM file to render the next class to an https://www.adafruit.com/product/420. 

[Check it out!](https://yoga-with-friends.rcdis.co/)

![led_grid.png](images/led_grid.png)

## Develop
```bash
docker buildx build -f Dockerfile -t bdettmer/yoga-with-friends .
docker run -it yoga-with-friends /bin/sh
```
