# CONNECT TO BUILD — Setup & Run Guide

## Quick Start (Install & Run)

### Step 1: Install Python

Download Python 3.11 or 3.12 from https://python.org/downloads/
During install: check "Add Python to PATH"
Verify: open new terminal → python --version

### Step 2: Set Up Virtual Environment

Open PowerShell in the project directory:

```
cd "C:\Users\HARIBHASKARAN A\Downloads\CONNECT_TO_BUILD"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure .env (Already created)

Open .env and optionally add your Gemini API key:
GEMINI_API_KEY=your-key-here
(App works without it — uses demo fallback)

### Step 4: Run Migrations & Seed

```
python manage.py makemigrations accounts owners workers projects quotations payments complaints compliance
python manage.py migrate
python manage.py seed_demo
```

### Step 5: Run Server

```
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Demo Credentials

Owner: HO-TN-8F42K | Phone: 9876543210 | Password: Demo@1234
Worker: WK-TN-3A91P | Phone: 9876543220 | Password: Demo@1234

## Django Admin

http://127.0.0.1:8000/django-admin/
Run: python manage.py createsuperuser
