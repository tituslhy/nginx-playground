# Deployment of our app using helm charts

## Notes
•	Chart.yaml apiVersion refers to the Helm chart spec version, not Kubernetes API resources.
	•	apiVersion: v2 → Helm 3+, supports dependencies natively and values.yaml requirements.
	•	apiVersion: v1 → old Helm 2 style (legacy).
•	Your Kubernetes manifests (Deployment, Service, Ingress) use their own API versions like:
	•	Deployment: apps/v1
	•	Service: v1
	•	Ingress (K8s 1.19+): networking.k8s.io/v1

Important: You do NOT need to align Helm chart apiVersion with Kubernetes resource apiVersion. They are separate:
•	Helm’s apiVersion = chart spec.
•	K8s apiVersion = actual resource kind.