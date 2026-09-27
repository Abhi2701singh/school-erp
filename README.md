# 🏫 EduManage - Multi-Tenant School Management ERP System

[![Django Version](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Cloud-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A modern, comprehensive, multi-tenant School Enterprise Resource Planning (ERP) platform designed for schools, educational institutes, and academic trusts. **EduManage ERP** provides end-to-end automation for academic administration, student information, fee collection with digital slip verification, classic routine timetable matrices, attendance registers, examinations, homework, and role-based portals.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [User Roles & Permissions](#-user-roles--permissions)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Quick Start & Installation](#-quick-start--installation)
- [Environment Variables](#-environment-variables)
- [Core Modules Breakdown](#-core-modules-breakdown)
  - [1. Fee Management & Student Online Payment](#1-fee-management--student-online-payment)
  - [2. Classic Routine Timetable Grid](#2-classic-routine-timetable-grid)
  - [3. Multi-School Tenant Isolation](#3-multi-school-tenant-isolation)
  - [4. Academics & Student Lifecycle](#4-academics--student-lifecycle)
  - [5. Homework & Study Material Hub](#5-homework--study-material-hub)
- [Deployment Guide](#-deployment-guide)
  - [Deploying to Render](#deploying-to-render)
  - [Neon Serverless PostgreSQL Setup](#neon-serverless-postgresql-setup)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Key Features

- 🏢 **Multi-Tenant Architecture**: Single installation supports multiple independent schools with complete data isolation via thread-local school context.
- 💳 **Smart Fee Collection & Slip Verification**:
  - Itemized fee heads (Tuition, Transport, Exam, Admission, etc.) linked to academic sessions.
  - Student self-service fee portal with automatic past arrears rollup.
  - Proof / Payment slip upload with transaction validation (prevents overpayment).
  - Admin verification workflow (`Pending` ➔ `Approved` / `Rejected`) with instant official PDF receipt generation.
- 📅 **Classic Routine Timetable Matrix**:
  - Full weekly timetable grid (`Monday` to `Saturday`) with period columns (`1st` to `8th` + `Extra Class`).
  - Prominent vertical **`BREAK`** column separator.
  - Subject name displayed with assigned teacher in brackets: `MATH (Abhi Singh)`.
  - 1-click quick delete, cell hover instant add modal, and print-optimized stylesheet.
- 🎓 **Complete Student & Staff Information System**:
  - Admission management with photos, roll numbers, Aadhaar/Govt IDs, and guardian details.
  - Staff & teacher profiles with subject and class allocations.
- 📋 **Daily Attendance Register**:
  - Section-wise daily student attendance marking (`Present`, `Absent`, `Late`, `Half-day`).
  - Automated monthly statistics and student-wise attendance percentages.
- 📊 **Examinations & Report Cards**:
  - Term/Semester examination configuration with custom grading systems.
  - Marksheet entry and automated grade calculation.
- 📚 **Homework & Study Materials**:
  - Class-wise digital homework assignment with submission deadlines.
  - PDF/document study materials repository.
  - School announcements and targeted notice board.
- 🖨️ **Print & PDF Generation**: Built-in PDF challan generation, printable routine sheets, and fee receipts using ReportLab and `@media print` CSS.

---

## 👥 User Roles & Permissions

| Role | Permissions & Capabilities |
| :--- | :--- |
| **Super Admin** | Global system access, multi-school tenant provisioning, global analytics, and school configuration. |
| **School Admin / Principal** | School-level administration, fee verification, timetable builder, student/teacher directory, attendance audits, notices. |
| **Teacher** | Assigned class dashboard, mark daily attendance, assign/delete homework, upload study notes, view teaching schedule. |
| **Student** | Personal dashboard, view fee dues, submit payment proofs, download receipts, view timetable routine, attendance percentage, homework. |
| **Parent** | Multi-child dashboard, track children's attendance, fees, homework, and exam performance. |
| **Accountant** | Fee structure setup, fee invoice generation, offline fee collection, and verification of student online payments. |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client([Web Browser / Mobile View])
    
    subgraph Edge & Security
        CF[Cloudflare Edge / Tunnel]
        WN[WhiteNoise Static Server]
    end

    subgraph Django Application Layer
        TM[Tenant Context Middleware]
        Auth[Role-Based Authentication]
        
        subgraph Core Apps
            SCH[schools: Tenant Config]
            ACC[accounts: User & Auth]
            ACAD[academics: Classes & Timetable]
            STU[students: Admissions & Directory]
            TEA[teachers: Staff Management]
            ATT[attendance: Daily Marking]
            FEE[fees: Dues & Verification]
            EXAM[examinations: Marks & Grading]
            HW[homework: Notes & Notices]
        end
    end

    subgraph Data Tier
        Postgres[(Cloud PostgreSQL / Neon Serverless)]
        Media[(Local / Cloud Media Storage)]
    end

    Client --> CF --> WN --> TM --> Auth
    Auth --> CoreApps
    SCH & ACC & ACAD & STU & TEA & ATT & FEE & EXAM & HW --> Postgres
    STU & HW & FEE --> Media
```

---

## 💻 Tech Stack

- **Backend Framework**: [Django 5.x](https://www.djangoproject.com/) (Python 3.11+)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Production on [Neon Serverless](https://neon.tech/)) / SQLite3 (Development)
- **Database Driver & ORM**: `psycopg2-binary`, `dj-database-url`, Django ORM with Custom Tenant Querysets
- **Frontend UI**: [Bootstrap 5.3](https://getbootstrap.com/), [FontAwesome 6](https://fontawesome.com/), Custom Vanilla JavaScript
- **Static & Media Serving**: [WhiteNoise](https://whitenoise.readthedocs.io/), Gunicorn WSGI
- **Document & PDF Engine**: [ReportLab](https://www.reportlab.com/), `openpyxl` (Excel exports)
- **Deployment Platform**: [Render](https://render.com/), [Cloudflare](https://www.cloudflare.com/)

---

## 📁 Project Directory Structure

```text
school-erp/
├── academics/              # Classes, sections, subjects & routine timetable matrix
│   ├── models.py           # Class, Section, Subject, Timetable models
│   ├── views.py            # Timetable matrix generation & CRUD views
│   └── forms.py            # Academic forms with dynamic tenant filtering
├── accounts/               # Custom User model, RBAC, tenant middleware
│   ├── models.py           # Multi-tenant base model, custom User roles
│   └── middleware.py       # Thread-local tenant context isolation
├── attendance/             # Student daily attendance recording & register
├── dashboard/              # Role-tailored dashboards (Admin, Teacher, Student, Parent)
├── examinations/           # Exam sessions, grading scales, marks entry
├── fees/                   # Invoicing, dues, receipt generation, payment submissions
│   ├── models.py           # FeeHead, FeeStructure, StudentFee, PaymentSubmission
│   └── views.py            # Payment submission & admin verification workflows
├── homework/               # Homework assignments, study materials & notice board
├── schools/                # Multi-school tenant entity & academic sessions
├── students/               # Student directory, admissions, profile cards
├── teachers/               # Staff directory, subject & class allocations
├── templates/              # HTML5 Django templates
│   ├── academics/          # Timetable grid & academic views
│   ├── dashboard/          # SuperAdmin, Admin, Teacher, Student, Parent dashboards
│   ├── fees/               # Fee portal, receipt, challan, payment proof forms
│   └── base.html           # Responsive sidebar layout & topbar
├── static/                 # Custom CSS stylesheets, icons, logos
├── school_erp/             # Main Django project settings & URL configuration
│   ├── settings.py         # Multi-database, session, auth & security settings
│   └── urls.py             # Root URL routing
├── build.sh                # Automated build & migration script for Render
├── render.yaml             # Render infrastructure as code blueprint
├── requirements.txt        # Python package dependencies
└── manage.py               # Django management CLI
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python `3.10` or higher
- Git
- Virtual environment tool (`venv`)

### 1. Clone the Repository
```bash
git clone https://github.com/Abhi2701singh/school-erp.git
cd school-erp
```

### 2. Create and Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
```env
DJANGO_SECRET_KEY=your-secure-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
# Optional: Set DATABASE_URL to your PostgreSQL instance, or leave empty to use SQLite3 locally
# DATABASE_URL=postgresql://user:password@localhost:5432/school_erp
```

### 5. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `DJANGO_SECRET_KEY` | **Yes** | Insecure fallback | Secret key for cryptographic signing. |
| `DJANGO_DEBUG` | No | `False` | Enable/disable debug mode (`True`/`False`). |
| `ALLOWED_HOSTS` | No | `*` | Comma-separated list of allowed hostnames. |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection URL (e.g., Neon Postgres / Supabase). |
| `PYTHON_VERSION` | No | `3.11.8` | Python runtime version for cloud deployments. |

---

## 🔍 Core Modules Breakdown

### 1. Fee Management & Student Online Payment
- **Self-Service Student Payment Portal**: Students can check all fee heads (Tuition, Transport, etc.), current dues, and past arrears.
- **Payment Slip Submission**: Students submit offline or UPI payments by uploading the transaction receipt / slip.
- **Validation**: Strict validation ensures student cannot submit amounts exceeding net dues.
- **Verification Portal**: Admins review payment slips, verify transaction IDs, and approve or reject submissions.
- **Arrears Handling**: Unpaid fee balances automatically carry forward to next month's invoice.

### 2. Classic Routine Timetable Grid
- **Structured Table Matrix**:
  - Rows: Days of the week (`MONDAY` - `SATURDAY`).
  - Columns: Morning periods (`1st`, `2nd`, `3rd`, `4th`), Vertical `BREAK`, Afternoon periods (`5th`, `6th`, `7th`, `8th`, `EXTRA CLASS`).
  - Format: Displays Subject in bold uppercase and `( Teacher Name )` right below.
- **Instant Actions**: Hover over any empty slot to add a class with pre-filled day and period; 1-click delete with confirm dialog.
- **Print Optimization**: Click "Print Routine" to print or export a clean, high-resolution timetable sheet.

### 3. Multi-School Tenant Isolation
- Every database model inherits from `TenantModel`.
- `TenantMiddleware` extracts the active school from the user's session or profile and sets a thread-local context.
- All querysets are automatically scoped to `school=request.school`, preventing cross-tenant data leakage.

### 4. Academics & Student Lifecycle
- Comprehensive student directory with search and filter by Class, Section, and Status.
- Complete guardian and emergency contact details.
- Promotion workflows across academic sessions.

### 5. Homework & Study Material Hub
- Subject-specific homework creation with deadline alerts.
- Downloadable study notes and learning resources.
- Centralized broadcast notice board with role targeting (`ALL`, `TEACHER`, `STUDENT`, `PARENT`).

---

## 🌐 Deployment Guide

### Deploying to Render

This repository includes a preconfigured `render.yaml` and `build.sh` for 1-click deployment to [Render](https://render.com/):

1. Push your code to your GitHub repository.
2. Log in to Render and click **New +** ➔ **Blueprint**.
3. Connect your GitHub repository.
4. Render will read `render.yaml` and configure:
   - Python environment
   - Automated build command (`bash build.sh`)
   - Start command (`gunicorn school_erp.wsgi:application`)
   - Static file collection (`collectstatic` with WhiteNoise)
   - Database migrations (`python manage.py migrate`)

### Neon Serverless PostgreSQL Setup
To ensure persistent cloud storage with zero data loss across deployments:
1. Create a free PostgreSQL database on [Neon](https://neon.tech/).
2. Copy the connection string:
   ```text
   postgresql://<user>:<password>@<endpoint>.neon.tech/<dbname>?sslmode=require
   ```
3. Add `DATABASE_URL` in your Render Environment Variables.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Developed with ❤️ for Schools & Educational Institutions.</sub>
</div>
