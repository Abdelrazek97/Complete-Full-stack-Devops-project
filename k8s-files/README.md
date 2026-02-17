# Kubernetes Deployment

## 1) Build and push Flask image
Update `k8s-files/flask-deployment.yaml` image field, then:

```bash
docker build -f Dockerfile.flask -t <registry>/acadmic-flask:latest .
docker push <registry>/acadmic-flask:latest
```

## 2) Deploy manifests
```bash
kubectl apply -k k8s-files/
```

## 3) Check status
```bash
kubectl get pods -n flask-app-namespace
kubectl get pods -n database-namespace
kubectl get svc -n flask-app-namespace
kubectl get svc -n database-namespace
```

## 4) Access app
- Ingress host: `http://flask.local` (map host to your ingress controller IP)
- Local test with port-forward:
```bash
kubectl port-forward -n flask-app-namespace svc/flask-service 5000:80
```
Then open `http://localhost:5000`.

## 5) Cleanup
```bash
kubectl delete -k k8s-files/
```
