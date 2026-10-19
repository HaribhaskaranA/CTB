# 🏗️ CONNECT TO BUILD (CTB)

> **A Trusted Digital Ecosystem for Home Construction and Renovation**

CONNECT TO BUILD (CTB) is a full-stack web platform designed to streamline, organize, and secure the home construction process in India. By bridging the gap between house owners and verified construction professionals (masons, electricians, plumbers, carpenters, painters, civil contractors, and architects), CTB transforms an unorganized industry into a transparent, milestone-driven digital workflow.

---

## 🌟 Key Highlights & Innovations

- 🛡️ **Privacy-First Architecture**: Contact numbers, personal addresses, and government ID numbers are strictly safeguarded. Direct contact details are concealed until a quote is accepted and work is assigned.
- 📱 **Real-Time SMS / OTP Verification**: Twilio Verify integration with built-in sandbox demo mode ensures authentic mobile numbers before account activation.
- 📁 **Private Government ID Verification**: Secure document storage via Supabase Private Storage (`government-ids`) for trade and identity documents.
- 🤖 **AI Project Assistant**: Powered by Google Gemini to parse plain-language construction desires (e.g. *"I want to build a 3BHK house in 1800 sq.ft with an open terrace and budget of 60 lakhs"*) into structured architectural specifications.
- 🗺️ **Automated 12-Stage Construction Roadmap**: Auto-generates complete building stages (Planning, Site Prep, Foundation, Structural, Electrical, Plumbing, Roofing, Flooring, Carpentry, Painting, Inspection, Completed) with progress sliders and photo evidence.
- 📜 **Regulatory & Compliance Checklists**: Local building plan approvals (CMDA, BBMP, ULB, TANGEDCO clearances) with demo disclaimers.
- 🔍 **Worker Verification & Application Tracking**: New workers receive an application tracking ID (`TRK-TN-XXXXX`) upon sign-up; their login credentials remain protected until verified by platform administrators.
- 💳 **Milestone Payment & Dispute Resolution**: Stage-based payment records and a formal dispute management system.

---

## 🏗️ Architecture & Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 4.2+ (MVT Architecture + REST APIs) |
| **Language** | Python 3.11 / 3.12 / 3.13 |
| **Database** | PostgreSQL (Hosted on Supabase) via `dj-database-url` |
| **Cloud Storage** | Supabase Storage (Private encrypted bucket for verification docs) |
| **Identity & SMS** | Twilio Verify API (SMS OTP with fallback demo simulation) |
| **Generative AI** | Google Gemini API (`google-generativeai`) |
| **Frontend UI** | HTML5, Bootstrap 5, Bootstrap Icons, Custom CSS Design Tokens |
| **Color Palette** | Dark Navy (`#1A2744`), Construction Orange (`#E86329`), Off-White (`#F8FAFC`) |
| **Internationalization** | Multi-language translation layer (`translations.js` supporting English, Tamil, and more) |

---

## 📂 Project Structure

```
CONNECT_TO_BUILD/
├── accounts/          # Custom User model, Twilio OTP services, auth views & tracking
├── owners/            # House owner profiles, private serialization, owner dashboard
├── workers/           # Worker profiles, digital passport, trade certificates, verification
├── projects/          # Projects, 12-stage milestones, photo evidence, roadmap engine
├── quotations/        # Worker bidding, quotation comparison, and acceptance flow
├── payments/          # Stage-based payment tracking and records
├── complaints/        # Grievance redressal and dispute management
├── compliance/        # State-level municipal and building regulations
├── config/            # Django project settings, root URLs, and WSGI/ASGI handlers
├── static/
│   ├── css/main.css   # Custom CSS design system (tokens, cards, roadmap, pulse)
│   └── js/            # Client scripts: OTP auto-focus, AI assist, filters, translations
├── templates/
│   ├── base.html      # Responsive layout with role-aware sidebars and notification toasts
│   ├── landing.html   # High-converting landing page with role-based entrypoints
│   ├── auth/          # Login, OTP verification, Owner/Worker registration & success
│   ├── owner/         # Owner dashboard, project creation, compliance, worker search
│   ├── shared/        # Shared screens: 12-stage roadmap, payments, complaints
│   └── worker/        # Worker dashboard, digital passport, profile edit, project search
├── .env.example       # Template for environment configuration
├── manage.py          # Django management script
└── requirements.txt   # Python package dependencies
```

---

## 🚀 Step-by-Step User Guide (How to Use CTB)

### 1. For House Owners

1. **Sign Up & Verification**:
   - Navigate to **Register as House Owner** (`/register/owner/`).
   - Enter your name, city, state, and mobile number.
   - Click **Send OTP** to receive an SMS verification code via Twilio (or use the displayed Demo OTP).
   - Enter the 6-digit OTP to verify your phone number, set a password, and optionally upload an ID document.
   - Upon submission, you will receive a unique Owner ID (e.g., `HO-TN-8F42K`).

2. **Login**:
   - Go to `/login/`, select **House Owner**, enter your Owner ID and registered phone number.
   - Complete the OTP step to enter your **Owner Dashboard**.

3. **Create a Construction Project**:
   - Click **New Project** in the sidebar.
   - **Step 1 (Land Status)**: Confirm whether you already own land or need land assistance.
   - **Step 2 (Compliance)**: Review the municipal checklist for building permits, environmental approvals, and electricity connections.
   - **Step 3 (Requirements)**: Enter room specifications (bedrooms, bathrooms, built-up sq.ft, floors, budget).
     > 💡 *Tip*: Use the **AI Assistant** sidebar box to describe your project in plain words (e.g., *"2 floors, 3 bedrooms, 1500 sqft, budget 50L"*) and click **Auto-fill Form**!
   - Click **Create Project & Generate Roadmap**.

4. **Manage the 12-Stage Roadmap**:
   - Your project automatically generates 12 sequential milestones from Planning to Completion.
   - Click on each stage on the left to inspect tasks, assign verified workers, and monitor completion percentages.

5. **Hire Verified Workers**:
   - Go to **Find Workers** (`/projects/workers/search/`).
   - Filter by trade (Mason, Electrician, Plumber, Carpenter, Painter, Civil Contractor), city, minimum experience, and daily rates.
   - Only workers verified by the platform are displayed.
   - View their public profile and request a quotation for specific stages.

6. **Track Payments & Complaints**:
   - Record milestone advance or completion payments (`/payments/`).
   - Raise a complaint (`/complaints/`) if any work quality or timeline issues arise.

---

### 2. For Workers & Trade Specialists

1. **Register as a Worker**:
   - Navigate to **Register as Worker** (`/register/worker/`).
   - Fill in your trade profession (Mason, Electrician, Plumber, Carpenter, etc.), years of experience, daily rate, skills, and service areas.
   - Upload any trade trade certificates, ITI diplomas, or past work photos.
   - Submit the form to receive an **Application Tracking ID** (e.g., `TRK-TN-4WDLL`).

2. **Track Application Status**:
   - Go to **Track Status** (`/worker/track-status/`).
   - Enter your Tracking ID to view the review status (`PENDING`, `UNDER_REVIEW`, or `VERIFIED`).
   - *Security Note*: While pending, your Worker Login ID remains hidden. Once the administrator marks your profile as `VERIFIED` in Supabase, your Login ID (e.g., `WK-TN-3A91P`) will be revealed.

3. **Login & Dashboard**:
   - Login with your Worker ID and phone number.
   - Your dashboard shows only your real platform metrics (starts fresh with 0 completed projects and "New" rating).

4. **Digital Work Passport**:
   - View your verified **Digital Passport** (`/worker/passport/`), showcasing verified trade badges, skills, approved certificates, and finished platform milestones.

5. **Browse Projects & Submit Quotes**:
   - Navigate to **Find Projects** (`/worker/projects/`).
   - View active projects posted by house owners that match your skills.
   - Click **Submit Quote** to submit your estimated cost and completion days.

---

### 3. For Platform Administrators

1. Access the Django Admin panel at `/django-admin/`.
2. Inspect `WorkerProfile` records in the **Workers** table.
3. Review uploaded trade certificates and identification documents.
4. Use the admin action **"Mark selected workers as VERIFIED"** to approve applications.
5. Once approved, the worker's application tracking page immediately reflects their verified badge and displays their login credentials.

---

## 💻 Local Setup & Installation

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Git
- PostgreSQL database (or Supabase account)

### 1. Clone the Repository
```bash
git clone https://github.com/HaribhaskaranA/CTB.git
cd CTB
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `.env` with your settings:
```env
DEBUG=True
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@db.xxxx.supabase.co:5432/postgres
DEMO_MODE=True

# Optional: Google Gemini API (for AI assistant)
GEMINI_API_KEY=your-gemini-api-key

# Optional: Twilio Verify (for live SMS OTP)
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_VERIFY_SERVICE_SID=VAxxxx

# Optional: Supabase Storage (for document uploads)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

### 5. Apply Migrations & Seed Demo Data
```bash
python manage.py migrate
python manage.py seed_demo
```

### 6. Start Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## 🔑 Demo Login Credentials

Pre-seeded demo credentials for instant evaluation (Password: `Demo@1234`):

| Role | User ID | Phone Number | Password |
|---|---|---|---|
| **House Owner** | `HO-TN-8F42K` | `9876543210` | `Demo@1234` |
| **Worker (Electrician)** | `WK-TN-3A91P` | `9876543220` | `Demo@1234` |
| **Worker (Mason)** | `WK-TN-7B22Q` | `9876543221` | `Demo@1234` |

---

## 🛡️ License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
