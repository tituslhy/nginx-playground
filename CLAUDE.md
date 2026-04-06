# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker Compose (Local Development)
Use Docker Compose to run the application locally with NGINX load balancing.

- **Build and scale Chainlit to 3 replicas:** `make build_scale`
- **Run the stack:** `make run`
- **Tear down the stack:** `make down`
- **Manual build and scale (without Make):** 
  `docker-compose up -d --build --scale chainlit=3`
- **Manual teardown (without Make):**
  `docker-compose down -v --remove-orphans`

### Kubernetes (Minikube) Setup
The project is designed to be deployed on Kubernetes using Helm.

- **Start Minikube and enable Ingress:**
  `minikube start && minikube addons enable ingress`
- **Install Helm dependencies:** `cd helm && helm dependency update && cd ..`
- **Lint Helm chart:** `helm lint helm`
- **Render Helm templates:** `helm template search-agent helm`
- **Deploy application:** `helm install search-agent helm`
- **Upgrade deployment:** `helm upgrade search-agent helm`
- **Check pod status:** `kubectl get pods`
- **Port-forward NGINX ingress (for local testing):**
  `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80`

### Docker Image Building
To build a custom image for the search agent:
`docker build -t <your_dockerhub_username>/search_agent:0.0.2 -f docker/Dockerfile .`

## Architecture Overview

The project demonstrates NGINX reverse proxy patterns and Kubernetes ingress configuration for a GenAI application.

### Application Functionality
The core of the app is an intelligent agent that uses the **Tavily Search API** to browse the web and answer user queries. 
- **Agentic Workflow**: It leverages `LlamaIndex`'s `AgentWorkflow` to handle complex reasoning and tool execution (searching).
- **Streaming & UI**: The interface provides real/real-time token streaming and clear visual steps for tool usage (e.g., showing when a search is being performed).
- **Observability**: Every interaction is instrumented with **OpenTelemetry**, sending traces to **Phoenix**, which stores them in a **PostgreSQL** database for deep inspection of LLM traces and performance.
- **Traffic Management**: NGINX acts as a reverse proxy, demonstrating advanced configurations like **Session Affinity** (sticky sessions) to ensure WebSocket-based streaming remains stable across multiple application replicas.

### Repository Structure
```text
.
├── app.py                # Main entry point; initializes Chainlit and manages the chat lifecycle.
├── docker-compose.yml    # Orchestrates the multi-container local development environment.
├── Dockerfile            # Defines the container image for the Chainlit application.
├── helm/                 # Kubernetes deployment configuration using Helm charts.
├── nginx/                # NGINX configuration files (reverse proxy/load balancer setup).
├── src/                  # Core application logic.
│   ├── on_chat_start.py  # Handles agent initialization, tool setup, and tracing registration.
│   └── on_message.py     # Manplements the agent execution loop and streaming responses to the UI.
├── utils/                # Helper utilities.
│   └── utils.py          # Contains logic for retrieving secrets and identifying container metadata.
└── CLAUDE.md             # Development guidelines for Claude Code.
```

### Services
- **chainlit-app**: The main GenAI chat interface (built with Chainlit). Configured with session affinity (sticky sessions) for WebSocket streaming.
- **phoenix**: Observability and LLM tracing (Arize Phoenix).
- **db**: PostgreSQL database for persistent storage of traces and chat history.

### Key Infrastructure Patterns
- **Ingress Controller**: Uses NGINX Inverss.
- **Session Affinity**: 
  - **Service level**: `sessionAffinity: ClientIP` ensures the same client IP hits the same pod.
  - **Ingress level**: Cookie-based affinity (`nginx.ingress.kubernetes.io/affinity: "cookie"`) is used for more reliable WebSocket session management.
- **Autoscaling**: Horizontal Pod Autoscalers (HPA) is configured for the `chainlit-app` to scale between 2 and 3 replicas based on CPU utilization.
- **Observability**: OpenTelemetry (OTLP) traces are collected by Phoenix from the Chainlit application.


### Environment Requirements
The deployment requires several Kubernetes secrets to be present:
- `postgres-creds`: Contains `postgres-password`.
- `tavily-secret`: Contains `api-key` for web search.
- `openai-secret`: Contains `api-key` for LLM access.

### Future Work
- **Infrastructure as Code (Terraform)**: Implement Terraform to automate the provisioning of the underlying cloud infrastructure and Kubernetes clusters.
- **CI/CD Pipeline (GitHub Actions)**: Establish a full automation pipeline using GitHub Actions to run automated tests, build Docker images, and deploy the application to Kubernetes clusters.
