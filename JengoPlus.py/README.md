# JengoPlus MVP
pip install -r requirements.txt
python manage.py makemigrations core && python manage.py migrate
python manage.py createsuperuser   # then set role=Administrator in /admin/ > Users
python manage.py runserver
Setup in /admin/: add Workers, Projects (expected_workers), supervisors (role=Supervisor), ProjectAssignments, Tasks (budget), Disbursements (tick "confirmed" after checking statement).
Production: set DEBUG=0, SECRET_KEY, POSTGRES_* env vars, EVIDENCE_DIR (private path), serve behind HTTPS.
