# Streamlit Demo

A lightweight Streamlit demo for keyword-based resume-to-job similarity.

## Run locally

```bash
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

Choose this repository, branch `main`, and main file path `streamlit_app.py`.

This is a separate demo UI and does not automatically connect to the original Django API or React frontend. The full application requires separate deployment and API configuration; read [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md).
