# AI-Enabled Employment Matching Platform — Run & Deployment Guide

The original `frontend/` and `backend/` folders are preserved as provided. The helper files in this root folder are additions only.

## Run locally on Windows

Prerequisites: Python 3.10+ (the supplied virtual environment is Windows-specific and should not be relied on across machines), Node.js 20.19+ or 22.12+, and npm.

1. Extract this ZIP.
2. Open a terminal in the extracted project root (the folder containing `frontend` and `backend`).
3. Install backend dependencies:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements-deploy.txt
   ```

4. In terminal 1, start the backend:

   ```powershell
   cd backend
   python manage.py migrate
   python manage.py runserver 127.0.0.1:8000
   ```

5. In terminal 2, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

6. Open the Vite URL shown in the terminal (normally `http://localhost:5173`). The frontend's existing Vite proxy forwards `/api` requests to Django at `http://127.0.0.1:8000`.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal and activate again.

## Important notes

- Django's existing settings use SQLite, `DEBUG=True`, open CORS, and a development secret key. Those settings are preserved per your instruction, but they are **not production-safe**. Do not deploy publicly with real user data until production settings, secret management, database persistence, HTTPS, and allowed hosts are configured.
- Resume matching tasks use Celery/Redis. Basic pages/API may start without a Redis service, but asynchronous resume processing/matching may not work until Redis and a Celery worker are running. Redis is configured at `redis://localhost:6379/0` in the original backend settings.
- The existing SQLite database and uploaded resume files are included from your ZIP. On many cloud platforms, local filesystem data can be ephemeral.

## Hosting on Streamlit Community Cloud

This project is a **React + Vite frontend and Django REST API backend**, not a Streamlit application. Streamlit Community Cloud runs a Streamlit Python app; it does not natively host a Vite/React web server and a separate Django API as a single production web service. The frontend also calls relative `/api` URLs, which rely on the Vite proxy locally.

To preserve the existing frontend without editing it, deploy the frontend and backend as separate services:

1. Deploy `backend/` to a Python web host that supports Django and persistent storage; configure a public HTTPS backend URL and production environment settings.
2. Deploy `frontend/` to a static hosting service that supports Vite builds. A same-origin `/api` reverse proxy or a frontend API base URL configuration is required for production. Since you asked not to change either folder, this ZIP does not rewrite the existing API calls.
3. Streamlit can host a separate dashboard/wrapper, but it cannot directly serve this existing React UI unchanged. A true one-click Streamlit deployment of the full existing app is not possible without either adding a wrapper with different UI functionality or changing deployment/API configuration.

## Files added

- `requirements-deploy.txt`: UTF-8 copy of the supplied backend dependency list, so pip can read it reliably (the original requirements file is preserved unchanged).
- `run_project.bat`: opens separate local backend/frontend terminals.
- `STREAMLIT_DEPLOYMENT.md`: concise hosting notes.
