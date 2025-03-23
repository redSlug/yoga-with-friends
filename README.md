# yoga-with-friends

Created in order facilitate friends attending yoga classes together, this repo shares up-to-date 
class information three ways:
1) [user facing website](https://redslug.github.io/yoga-with-friends/), 
2) calendar URL to subscribe to
3) [LED display that shows the time of the next class](images/led_grid.png) near bedtime within twelve hours of class, in a [3d printed case](https://www.tinkercad.com/things/8KHh1wXYdHa-16x32-rgb-led-matrix-panel-case)

Check out documentation for the [pi](pi/README.md), [backend](backend/README.md), [frontend](frontend/README.md) 
and [deploying](DEPLOY.md).

## Architecture Diagram
![architecture diagram](https://lucid.app/publicSegments/view/77710a04-6480-4144-8c24-c2ac63166583/image.png)

## Develop
Develop locally or using docker by [populating credentials](backend/README.md) and running:
```bash
docker buildx build -f Dockerfile -t bdettmer/yoga-with-friends .
docker run -it \
  -v $(pwd)/backend/token.json:/yoga-with-friends/backend/token.json \
  -v $(pwd)/backend/.env:/yoga-with-friends/backend/.env \
  bdettmer/yoga-with-friends /bin/sh
```
