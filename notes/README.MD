# Local Dev Setup for nginx-playground Helm Deployment

This guide explains how to get all services running locally on Minikube, including Chainlit, Phoenix, and Postgres.

---

## Prerequisites

- Minikube installed and running
- kubectl configured for Minikube
- Helm installed
- Docker installed (for building/pulling images)
- sudo privileges (for `minikube tunnel` if needed)

---

## 1. Start Minikube and enable ingress

```bash
minikube start
minikube addons enable ingress
```

To check if ingress is running:
```
minikube addons list | grep nginx
```

To check if nginx pod is running:
```
kubectl get pods -n ingress-nginx
```

Note: The ingress controller runs at 192.168.49.2 in this cluster.
Keep a terminal open for minikube tunnel if using LoadBalancer services in the future.

## 2. Helm install
From the repo root:
```
helm install search-agent helm
```
This deploys:
	•	chainlit-app (your main app)
	•	phoenix (UI and OTLP services)
	•	db (Postgres database)

Check status:
```
kubectl get pods
kubectl get svc
kubectl get ingress
```

## 3. Accessing services
Chainlit (via ingress)
	•	In your /etc/hosts file, add:
    ```
    192.168.49.2  chainlit.local
    ```
    •	Open in browser: http://chainlit.local

Note: In some Minikube setups, ingress may not work reliably yet. If the page times out, use the port-forward method below temporarily.

### Phoenix
Since ingress does not route Phoenix ports by default:
```
kubectl port-forward svc/phoenix 6006:6006
```

Open "http://localhost:6006" in the browser"

### Postgres
```
kubectl port-forward svc/db 5432:5432
```

Connect locally:
```
psql -h localhost -U postgres -d search-agent-db
```

Use password stored in Kubernetes secret:
```
kubectl get secret postgres-creds -o jsonpath="{.data.db-password}" | base64 --decode
```

## Quick troubleshooting
1. Pods not starting
```
kubectl logs <pod-name> -c <container-name>
kubectl describe pod <pod-name>
```

2. Secrets issues: check that secrets exist
```
kubectl get secret openai-secret
kubectl get secret tavily-secret
kubectl get secret postgres-creds
```

3. Ingress not reachable:
•	Verify /etc/hosts entry
•	Check kubectl get ingress → host/IP match
•	If still failing, use port-forward for local dev