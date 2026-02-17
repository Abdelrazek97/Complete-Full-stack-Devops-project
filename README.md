# 🎓 Academic App

![Flask](https://img.shields.io/badge/Flask-Python%203.10+-black?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5?logo=kubernetes)

A lightweight **Flask-based academic management system** for managing users, programs, semesters, questions, and evaluation workflows.

The application is fully containerized and production-ready with **Docker, Docker Compose, and Kubernetes deployment manifests**.

---

## 📌 Features

- Academic data management system
- MySQL relational database
- Jinja2 templating
- Dockerized development environment
- Kubernetes deployment support
- Gunicorn production server

---

## 🏗️ Architecture

Client (Browser)
│
▼
Flask App (Gunicorn)
│
▼
MySQL


### Deployment Options

- 🧪 Local development → Virtualenv  
- 🐳 Containerized → Docker Compose  
- ☸️ Production → Kubernetes  

---

## 📂 Project Structure

.
├── app.py
├── requirements.txt
├── docker-compose.yml
├── templates/
├── static/
└── k8s-files/
├── deployments
├── services
├── secrets
├── pvc
└── README.md


---

## ⚙️ Prerequisites

- Python **3.10+**
- Docker & Docker Compose
- kubectl (for Kubernetes deployment)
- MySQL (or use the containerized service)

---

## 🚀 Quick Start

### 🔹 Run Locally (Virtual Environment)

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
python app.py
Open:

http://127.0.0.1:5000
🔹 Run with Gunicorn (Production-like)
gunicorn -w 4 app:app

🔹 Run with Docker Compose (Recommended)
docker-compose up --build

Stop containers:
docker-compose down

☸️ Kubernetes Deployment
Apply the full stack:

kubectl apply -k k8s-files/
Check resources:

kubectl get pods
kubectl get svc
View logs:

kubectl logs -l app=flask -n <namespace>
For more details:

k8s-files/README.md