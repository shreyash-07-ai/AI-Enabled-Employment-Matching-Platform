@echo off
setlocal
start "Django backend" cmd /k "cd /d %~dp0backend && python manage.py migrate && python manage.py runserver 127.0.0.1:8000"
start "React frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"
echo Backend and frontend terminals opened. Open the Vite URL shown in the frontend terminal.
