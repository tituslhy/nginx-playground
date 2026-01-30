# nginx-playground

<p align="center">
    <img src="./images/nginx.png" height = 600px>
</p>

This repository is a companion resource to the Medium Article [Nginx: The Single-Server Swiss Army Knife](https://medium.com/@tituslhy/nginx-the-single-server-swiss-army-knife-3445197f8f86)

## Spinning everything up
### If you have `Make` installed
Simply run:
```
make build_scale
```
This builds the app's image and spins all the services up.

If you already have the app's image built:
```
make run
```

To tear everything down
```
make down
```

### If you don't have `Make` installed, 
Run:
```
docker-compose up -d --build --scale chainlit=3
```

If you already have the app's image built:
```
docker-compose up -d --scale chainlit=3
```

Tearing everything down:
```
docker-compose down -v --remove-orphans
```

### To build image
```
docker build -t <your_dockerhub_username>/search_agent:0.0.2 -f docker/Dockerfile .
```

## Using Helm
To pull subchart dependencies:
```
helm dependency update
```

To lint:
```
helm lint helm
```

To check templates:
```
helm template helm
```

## Creating secrets
Run:
```
kubectl create secret generic postgres-creds \
--from-literal=db-password='your_password'

kubectl create secret generic tavily-secret \
--from-literal=db-password='your_api_key'

kubectl create secret generic openai-secret \
--from-literal=OPENAI_API_KEY='your_api_key'
```

To check if the secrets were created:
```
kubectl get secrets
```