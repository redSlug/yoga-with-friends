# yoga-with-no-fees

A tool for preventing yoga class fees. Exports yoga events and sends them to your calendar so 
you know about them.

[Check it out!](https://yoga-with-friends.rcdis.co/)

![led_grid.png](images/led_grid.png)

## Develop locally
```bash
docker buildx build -f Dockerfile -t bdettmer/yoga-with-friends .
docker run -it yoga-with-friends /bin/sh
```

## Deploy

```bash
docker login
ssh bdettmer@broome.cluster.recurse.com -N -L 6443:localhost:6443 # create tunnel
docker buildx build --platform linux/amd64 -f Dockerfile -t bdettmer/yoga-with-friends . && docker push bdettmer/yoga-with-friends && kubectl rollout restart -n yoga-with-friends deployment/yoga-with-friends
````

### Helpful commands

```bash
kubectl get nodes -n yoga-with-friends
kubectl get pods -n yoga-with-friends
kubectl get deployments -n yoga-with-friends
kubectl logs deployment/yoga-with-friends -n yoga-with-friends
kubectl get ingress -n yoga-with-friends
kubectl get services -n yoga-with-friends
kubectl get pods -n yoga-with-friends 
kubectl describe pod yoga-with-friends-POD_ID -n yoga-with-friends
kubectl logs yoga-with-friends-POD_ID -n yoga-with-friends
kubectl delete pod yoga-with-friends-POD_ID -n yoga-with-friends
docker buildx build --no-cache -f Dockerfile -t bdettmer/yoga-with-friends .
```
