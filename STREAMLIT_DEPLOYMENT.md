# Streamlit hosting notes

## Can this exact project be hosted entirely on Streamlit?

Not as-is. The supplied application consists of a React/Vite single-page frontend and a Django REST API. Streamlit Community Cloud expects a Streamlit Python entry-point and does not act as a general reverse proxy/process manager for a React server plus Django API. The existing frontend uses relative `/api` calls and the Vite development proxy is only configured for local development.

## Recommended deployment while preserving the source folders

- Host the Django API (`backend/`) on a Django-compatible Python host.
- Host the Vite frontend (`frontend/`) on a static frontend host.
- Configure a same-origin `/api` reverse proxy, or separately configure the frontend API base URL before production deployment. The latter requires a source change, so it has intentionally not been done in this package.
- Use Streamlit only if you want a separate Streamlit dashboard/wrapper; that would not be the same React interface.

Before public deployment, replace the development secret key, turn off `DEBUG`, restrict `ALLOWED_HOSTS` and CORS, configure HTTPS/CSRF trusted origins, persistent database/media storage, and Redis/Celery if asynchronous tasks are required.
