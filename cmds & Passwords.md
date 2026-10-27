-> Install backend dependencies:
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements-deploy.txt

-> for frontend:
    cd frontend
    npm install
    npm run dev

-> for backend:
   cd backend
   python manage.py migrate
   python manage.py runserver 127.0.0.1:8000




Passwords :

-> Recruiter account:
   username: MS
   password: 12345678

-> Candidate account:
   username: Shre 
   password: 12345678