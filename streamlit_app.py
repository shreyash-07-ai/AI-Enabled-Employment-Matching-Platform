import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

DJANGO_HOST = "127.0.0.1"
DJANGO_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173
FRONTEND_URL = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}/login"

_processes = []


def port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def start_backend() -> None:
    if port_is_open(DJANGO_HOST, DJANGO_PORT):
        return

    # Use the same Python interpreter that launched Streamlit.
    subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        cwd=BACKEND_DIR,
        check=True,
    )

    process = subprocess.Popen(
        [
            sys.executable,
            "manage.py",
            "runserver",
            f"{DJANGO_HOST}:{DJANGO_PORT}",
            "--noreload",
        ],
        cwd=BACKEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    _processes.append(process)


def start_frontend() -> None:
    if port_is_open(FRONTEND_HOST, FRONTEND_PORT):
        return

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise RuntimeError(
            "Node.js/npm was not found. Install Node.js and make sure 'npm' "
            "works in a new terminal."
        )

    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        subprocess.run([npm, "install"], cwd=FRONTEND_DIR, check=True)

    process = subprocess.Popen(
        [npm, "run", "dev", "--", "--host", FRONTEND_HOST],
        cwd=FRONTEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    _processes.append(process)


def wait_for_services(timeout: int = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_is_open(DJANGO_HOST, DJANGO_PORT) and port_is_open(
            FRONTEND_HOST, FRONTEND_PORT
        ):
            return
        time.sleep(1)

    raise RuntimeError(
        "The frontend/backend did not start within the expected time. "
        "Check that Python dependencies and Node.js/npm are installed."
    )


def stop_children() -> None:
    for process in _processes:
        if process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass


import atexit

atexit.register(stop_children)


st.set_page_config(
    page_title="AI-Enabled Employment Matching Platform",
    page_icon="🎯",
    layout="wide",
)

st.title("AI-Enabled Employment Matching Platform")

try:
    with st.spinner("Starting the existing Django backend and React frontend..."):
        start_backend()
        start_frontend()
        wait_for_services()

    st.success("Application is running.")
    st.caption(
        "This is the original React + Django application. "
        "Streamlit is only being used as the local launcher."
    )

    components.iframe(
        FRONTEND_URL,
        height=900,
        scrolling=True,
    )

except subprocess.CalledProcessError as exc:
    st.error("A project startup command failed.")
    st.code(str(exc))

except Exception as exc:
    st.error("The application could not be started.")
    st.exception(exc)
