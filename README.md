# yoga-with-friends

A tool to get friends to attend yoga together. Exports yoga events to a hosted ICS calendar for your friends to subscribe to, a front end to show classes, and a PPM file to render the next class to an [LED grid](https://www.adafruit.com/product/420)
[Check it out!](https://yoga-with-friends.rcdis.co/)

![led_grid.png](images/led_grid.png)

![front_end.png](front_end.png)

## Develop
```bash
docker buildx build -f Dockerfile -t bdettmer/yoga-with-friends .
docker run -it yoga-with-friends /bin/sh
```
