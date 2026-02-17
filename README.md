# Academic App

A lightweight Flask-based academic management web application with MySQL backend, Docker support, and Kubernetes manifests for deployment.

## Overview

This repository contains a Flask web application for managing academic data (users, programs, semesters, questions, and various evaluation pages). It includes:

- `app.py`: main Flask application entrypoint.
- `templates/`: Jinja2 HTML templates used by the app.
- `static/`: CSS and static assets.
- `k8s-files/`: Kubernetes manifests and helper SQL.
- `docker-compose.yml`: local Docker Compose configuration.
- `requirements.txt`: Python dependencies.

## Prerequisites

- Python 3.10+ (or use included virtual environment in `env/`).
- Docker & Docker Compose (for containerized runs).
- kubectl (for deploying to Kubernetes clusters).

## Quickstart — Local (virtualenv)

1. Create and activate a virtual environment (optional):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally:

```bash
python app.py
```

Open your browser at http://127.0.0.1:5000/ (or as printed by the app).

Alternatively run with Gunicorn for production-like server:

```bash
gunicorn -w 4 app:app
```

## Docker (recommended for parity)

Build and run with Docker Compose:

```bash
docker-compose up --build
```

This will start the Flask app and a MySQL container per `docker-compose.yml`.

To stop and remove containers:

```bash
docker-compose down
```

## Kubernetes

The `k8s-files/` directory contains manifests for deploying the app and MySQL to a Kubernetes cluster. To apply the full kustomized stack:

```bash
kubectl apply -k k8s-files/
```

See `k8s-files/README.md` for more details and secrets management.

## Database

- Example SQL queries and initial data are in `queries.sql` and `k8s-files/queries.sql`.
- Update database credentials via environment variables or the `docker-compose.yml` / Kubernetes secrets before starting.

## Project Structure (high level)

- **Templates**: `templates/` contains the HTML pages used by the app (login, register, views, admin pages).
- **Static**: `static/` holds CSS files (`styles.css`, `style.css`) and other assets.
- **K8s**: `k8s-files/` holds YAMLs for deployments, services, secrets, PVCs and a `README.md`.

## Troubleshooting

- If the app fails to connect to MySQL, ensure the DB is running and credentials match.
- Check container logs for errors:

```bash
docker-compose logs -f
```

or for Kubernetes:

```bash
kubectl logs -l app=flask -n <namespace>
```

## Development notes

- Templates are standard Jinja2 files in `templates/`.
- Add static CSS under `static/` and reference them in templates.
- To add new routes, edit `app.py` and corresponding templates.

## Useful files

- [app.py](app.py) — application entrypoint
- [docker-compose.yml](docker-compose.yml) — Docker Compose config
- [requirements.txt](requirements.txt) — Python deps
- [k8s-files/README.md](k8s-files/README.md) — Kubernetes deployment notes

## License & Contact

This repository does not include an explicit license file. Add one if you plan to publish.

If you want further edits to the README (more details about environment variables, example screenshots, or API endpoints), tell me what to include and I will update it.

---

## GitHub-ready additions

- **Badges:** Add CI, build, and license badges (example below) once you have CI configured and a `LICENSE` file.

Example badge links to add at the top of `README` after creating workflows and license:

```
[![CI](https://img.shields.io/badge/ci-none-lightgrey.svg)](https://github.com/youruser/yourrepo/actions)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
```

## Environment variables

The app reads configuration from environment variables. Typical variables to set when running or publishing:

- `SECRET_KEY` — Flask secret key (set to a strong random value).
- `MYSQL_HOST` — MySQL hostname (e.g., `db` when using Docker Compose).
- `MYSQL_PORT` — MySQL port (default `3306`).
- `MYSQL_USER` — MySQL username.
- `MYSQL_PASSWORD` — MySQL password.
- `MYSQL_DATABASE` — MySQL database name.
- `FLASK_ENV` — `development` or `production`.

Set them locally in a `.env` file (do not commit secrets) and in GitHub Actions or your deployment secrets store.

## Publishing to GitHub

Steps to create a new repository and push the project (replace `youruser/yourrepo`):

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/youruser/yourrepo.git
git push -u origin main
```

If the repository already exists, clone it and copy files, or add the remote and push as shown above.

## Recommended next steps before publishing

- Add a `LICENSE` file (e.g., MIT, Apache-2.0) and update the `README` badge link.
- Add a `.gitignore` (Python, venv, env, .env, __pycache__, .DS_Store, etc.).
- (Optional) Add a GitHub Actions workflow for linting and tests (`.github/workflows/ci.yml`).
- Remove any large, sensitive, or private files from the repo (e.g., the `env/` virtual environment and any real credentials). Use `git rm --cached` if necessary.

## Quick checklist to make the repo GitHub-ready

- [ ] Add `LICENSE`
- [ ] Add `.gitignore`
- [ ] Remove `env/` and other local virtualenv folders from the repository
- [ ] Configure CI workflow (GitHub Actions)
- [ ] Add badges at the top of `README`

---

If you want, I can:

- Add a starter `.gitignore` and `LICENSE` (tell me which license),
- Remove the `env/` folder from Git history safely (I can prepare commands), or
- Add a CI workflow file for tests and linting.


