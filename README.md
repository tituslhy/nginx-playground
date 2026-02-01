# nginx-playground

<table border="0">
  <tr>
    <td><img src="./images/nginx.png" height="600px"></td>
    <td><img src="./images/helm_chart_banner.png" height="600px"></td>
  </tr>
</table>

This repository demonstrates NGINX reverse proxy patterns and Kubernetes ingress configuration. It's a companion resource to the Medium articles:
1. [Nginx: The Single-Server Swiss Army Knife](https://medium.com/@tituslhy/nginx-the-single-server-swiss-army-knife-3445197f8f86).

The project includes:
- **Chainlit**: GenAI chat interface with WebSocket streaming
- **Phoenix**: Observability and LLM tracing
- **PostgreSQL**: Persistent storage for traces and chat history

---

## Table of Contents
- [Docker Compose Setup](#docker-compose-setup)
- [Kubernetes (Minikube) Setup](#kubernetes-minikube-setup)
- [Troubleshooting](#troubleshooting)

---

## Docker Compose Setup

### Quick Start

**With Make installed:**
```bash
# Build and scale Chainlit to 3 replicas
make build_scale

# Run (if images already built)
make run

# Tear down
make down
```

**Without Make:**
```bash
# Build and scale
docker-compose up -d --build --scale chainlit=3

# Run (if images already built)
docker-compose up -d --scale chainlit=3

# Tear down
docker-compose down -v --remove-orphans
```

### Building Custom Image
```bash
docker build -t <your_dockerhub_username>/search_agent:0.0.2 -f docker/Dockerfile .
```

### Verifying NGINX Load Balancing (Docker)
```bash
# Access NGINX container
docker exec -it <nginx_container_id> /bin/bash

# Install DNS tools
apt-get update && apt-get install -y dnsutils

# Verify NGINX can resolve Chainlit service to multiple IPs
nslookup chainlit
```

You should see multiple IP addresses (one per Chainlit replica).

---

## Kubernetes (Minikube) Setup

### Prerequisites

- Minikube installed and running
- kubectl configured for Minikube
- Helm installed
- Docker (for building/pulling images)
- sudo privileges (for `minikube tunnel` if needed)

---

### 1. Start Minikube and Enable Ingress
```bash
# Start cluster
minikube start

# Enable ingress addon
minikube addons enable ingress
```

**Verify ingress is running:**
```bash
# Check addon status
minikube addons list | grep ingress

# Check NGINX ingress controller pod
kubectl get pods -n ingress-nginx
```

You should see `ingress-nginx-controller-xxx` in `Running` state.

---

### 2. Create Kubernetes Secrets

The application requires three secrets for API keys and database credentials:
```bash
# PostgreSQL password
kubectl create secret generic postgres-creds \
  --from-literal=postgres-password='your_password'

# Tavily API key (for web search)
kubectl create secret generic tavily-secret \
  --from-literal=api-key='your_tavily_api_key'

# OpenAI API key (for LLM)
kubectl create secret generic openai-secret \
  --from-literal=api-key='your_openai_api_key'
```

**Verify secrets were created:**
```bash
kubectl get secrets
```

---

### 3. Install with Helm

**Pull dependencies (PostgreSQL subchart):**
```bash
cd helm
helm dependency update
```

**Lint and validate:**
```bash
# Check YAML syntax and templating
helm lint .

# Render templates (check for errors)
helm template .
```

**Install the chart:**
```bash
# From repo root
helm install search-agent helm
```

**Verify deployment:**
```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get svc

# Check ingress
kubectl get ingress
```

Expected output:
```
NAME           CLASS   HOSTS                      ADDRESS        PORTS
chainlit-app   nginx   chainlit.local,localhost   192.168.49.2   80
```

---

### 4. Accessing Services

#### Option 1: Via Ingress (Recommended for testing ingress config)

**a) Add DNS entry to `/etc/hosts`:**
```bash
sudo nano /etc/hosts
```

Add this line:
```
192.168.49.2  chainlit.local
```

**b) Port-forward NGINX ingress controller:**
```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```

**c) Access in browser:**

- **Using localhost:** http://localhost:8080
- **Using custom domain:** http://chainlit.local (requires `minikube tunnel` - see below)

---

#### Option 2: Via Minikube Tunnel (For real ingress testing)

**Start tunnel (requires sudo):**
```bash
sudo minikube tunnel
```

**Keep this terminal open.** Verify route exists:
```bash
netstat -rn | grep 192.168.49
```

**Access in browser:**
```
http://chainlit.local
```

**Note:** If tunnel doesn't create routes on macOS, use Option 1 (port-forward) instead.

---

#### Option 3: Direct Service Access (For debugging)

**Chainlit (main app):**
```bash
kubectl port-forward service/chainlit-app 8080:80
```
Open: http://localhost:8080

**Phoenix (observability UI):**
```bash
kubectl port-forward service/phoenix 6006:6006
```
Open: http://localhost:6006

**PostgreSQL (database):**
```bash
kubectl port-forward service/db 5432:5432
```

Connect with psql:
```bash
# Get password from secret
kubectl get secret postgres-creds -o jsonpath="{.data.postgres-password}" | base64 --decode

# Connect
psql -h localhost -U postgres -d search-agent-db
```

---

### 5. Verifying NGINX Ingress Load Balancing

**Check NGINX can see multiple Chainlit replicas:**
```bash
# Get NGINX ingress controller pod name
kubectl get pods -n ingress-nginx

# Access NGINX container
kubectl exec -it -n ingress-nginx ingress-nginx-controller-<pod-id> -- /bin/bash

# Install DNS tools (if not already present)
apt-get update && apt-get install -y dnsutils

# Verify NGINX can resolve Chainlit service
nslookup chainlit-app.default.svc.cluster.local
```

Expected output: Multiple IP addresses (one per Chainlit replica pod).

**Check NGINX upstream configuration:**
```bash
# Inside NGINX container
cat /etc/nginx/nginx.conf | grep -A 20 "upstream default-chainlit-app"
```

You should see multiple `server <pod-ip>:8000;` entries.

**Verify session affinity is working:**
```bash
# Terminal 1: Tail logs from all Chainlit pods
kubectl logs -f -l app.kubernetes.io/name=chainlit-app

# Terminal 2: Open app in browser, send multiple messages
# All logs should come from ONE pod (sticky session)
```

---

### 6. Updating the Deployment

**After changing values.yaml or templates:**
```bash
# Upgrade release
helm upgrade search-agent helm

# Or uninstall and reinstall
helm uninstall search-agent
helm install search-agent helm
```

**Check rollout status:**
```bash
kubectl rollout status deployment/chainlit-app
```

---

## Troubleshooting

### Pods Not Starting

**Check pod status:**
```bash
kubectl get pods
kubectl describe pod <pod-name>
```

**Check logs:**
```bash
kubectl logs <pod-name>

# For multi-container pods
kubectl logs <pod-name> -c <container-name>
```

**Common issues:**
- Missing secrets → Create secrets (see step 2)
- Image pull failures → Check image name/tag in `values.yaml`
- Resource limits → Check `kubectl describe node`

---

### Ingress Not Reachable

**Verify ingress configuration:**
```bash
kubectl get ingress
kubectl describe ingress chainlit-app
```

**Check NGINX ingress logs:**
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

**Common issues:**
- `/etc/hosts` not configured → Add `192.168.49.2 chainlit.local`
- Tunnel not running → Start `sudo minikube tunnel`
- No network route → Use port-forward instead (Option 1 above)

---

### Session Affinity Not Working

**Symptoms:** WebSocket disconnects, messages route to different pods

**Verify service configuration:**
```bash
kubectl get service chainlit-app -o yaml | grep -A 3 sessionAffinity
```

Should show:
```yaml
sessionAffinity: ClientIP
sessionAffinityConfig:
  clientIP:
    timeoutSeconds: 3600
```

**Check ingress annotations:**
```bash
kubectl get ingress chainlit-app -o yaml | grep affinity
```

Should include:
```yaml
nginx.ingress.kubernetes.io/affinity: "cookie"
nginx.ingress.kubernetes.io/session-cookie-name: "route"
```

---

### Database Connection Issues

**Check PostgreSQL pod is running:**
```bash
kubectl get pods | grep db
```

**Verify secret exists:**
```bash
kubectl get secret postgres-creds
```

**Test connection from Chainlit pod:**
```bash
kubectl exec -it <chainlit-pod> -- /bin/bash
apt-get update && apt-get install -y postgresql-client
psql -h db -U postgres -d search-agent-db
```

---

### Phoenix Not Showing Traces

**Check environment variables are set:**
```bash
kubectl exec -it <chainlit-pod> -- env | grep PHOENIX
```

Should show:
```
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
```

**Check Phoenix pod logs:**
```bash
kubectl logs -l app.kubernetes.io/name=phoenix
```

**Verify OTLP port is accessible:**
```bash
kubectl get service phoenix
# Should show port 4317 (OTLP) and 6006 (UI)
```

---

## Architecture

### Services

| Service | Type | Ports | Purpose |
|---------|------|-------|---------|
| chainlit-app | ClusterIP | 80 → 8000 | Main GenAI chat interface |
| phoenix | ClusterIP | 6006 (UI), 4317 (OTLP) | Observability and tracing |
| db | ClusterIP | 5432 | PostgreSQL database |

### Session Affinity

Configured for WebSocket sticky sessions across multiple Chainlit replicas:

- **Service level:** `sessionAffinity: ClientIP` (routes same IP to same pod)
- **Ingress level:** NGINX cookie-based affinity (more reliable across proxies)

### Autoscaling

Horizontal Pod Autoscaler (HPA) configured for Chainlit:
- Min replicas: 2
- Max replicas: 3
- Target CPU: 80%

---

## Development Workflow

### Typical local dev flow:

1. **Start Minikube:** `minikube start`
2. **Enable ingress:** `minikube addons enable ingress`
3. **Create secrets:** (one-time setup)
4. **Install Helm chart:** `helm install search-agent helm`
5. **Port-forward NGINX:** `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80`
6. **Open app:** http://localhost:8080
7. **Make changes:** Edit code/templates
8. **Rebuild image:** `docker build ...` (if code changed)
9. **Upgrade Helm:** `helm upgrade search-agent helm`
10. **Test:** Refresh browser

### Cleaning up:
```bash
# Uninstall Helm release
helm uninstall search-agent

# Delete secrets (if needed)
kubectl delete secret postgres-creds tavily-secret openai-secret

# Stop Minikube
minikube stop

# Delete cluster (nuclear option)
minikube delete
```

---

## Production Considerations

This setup is optimized for **local development**. For production:

### Ingress
- ✅ Use cloud load balancers (AWS ALB, GCP GCLB, Azure App Gateway)
- ✅ Configure TLS/SSL certificates
- ✅ Set up proper DNS (not `/etc/hosts`)
- ✅ Add rate limiting and WAF rules

### Secrets Management
- ✅ Use external secret managers (AWS Secrets Manager, HashiCorp Vault)
- ✅ Rotate secrets regularly
- ✅ Use RBAC to restrict secret access

### Database
- ✅ Use managed database (AWS RDS, Cloud SQL, Azure Database)
- ✅ Configure backups and point-in-time recovery
- ✅ Use connection pooling (PgBouncer)
- ✅ Enable SSL for connections

### Observability
- ✅ Export traces to production observability platform (Datadog, New Relic, Grafana)
- ✅ Set up alerts for errors and latency spikes
- ✅ Configure log aggregation (ELK, Splunk, CloudWatch)

### Scaling
- ✅ Tune HPA based on actual traffic patterns
- ✅ Configure Pod Disruption Budgets (PDB)
- ✅ Use cluster autoscaling for node management

First enable metrics (so we can see the CPU usage):
```
minikube enable addons metrics
```

And now to stress test our deployment to see if autoscaling works:
```
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "seq 1 20 | xargs -P 20 -I {} sh -c 'while true; do wget -q -O- http://chainlit-app; done'"
```
This spawns 20 threads and continues to send them at our app - nginx is working hard!

Open another terminal and see the CPU usage:
```
kubectl get hpa chainlit-app -w
```
Once it passes the target CPU utilization in the values.yaml, it'll spin up a 3rd pod!

Output:
```
NAME           REFERENCE                 TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
chainlit-app   Deployment/chainlit-app   cpu: 68%/50%   2         3         2          20m
chainlit-app   Deployment/chainlit-app   cpu: 68%/50%   2         3         3          20m
```

#### The cooldown test
After you've turned off the spam command, it'll scale back down to 2 replicas after 5 minutes. The HPA won't scale down immediately. It waits for a Stabilization Window (default is 5 minutes) to ensure the traffic isn't coming back before it terminates the 3rd pod. This prevents "flapping" (rapidly adding/removing pods). 