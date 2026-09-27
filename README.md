<div align="center">

# 🏫 EduManage ERP
### **Next-Generation Multi-Tenant School Management & Academic Operating System**

[![Django Version](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/PostgreSQL-Neon_Serverless-00E599?style=for-the-badge&logo=postgresql&logoColor=black)](https://neon.tech/)
[![Frontend](https://img.shields.io/badge/Bootstrap-5.3_Custom_UI-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Deployment](https://img.shields.io/badge/Deploy-Render_Cloud-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![License](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

<p align="center">
  <b>A production-ready, cloud-native ERP platform built for K-12 Schools, Colleges, and Educational Trusts.</b><br>
  Featuring automatic multi-school data isolation, self-service student fee portal with proof verification, classic routine timetable matrix, daily attendance register, report cards, and role-based access control.
</p>

[✨ Live Features](#-key-features-overview) • [🚀 Quick Start](#-quick-start-guide) • [👥 Role Portals](#-role-based-access-matrix) • [🏗️ Architecture](#-system-architecture) • [🌐 Cloud Deployment](#-cloud-deployment-guide)

---

</div>

## 📑 Table of Contents

- [✨ Key Features Overview](#-key-features-overview)
- [👥 Role-Based Access Matrix](#-role-based-access-matrix)
- [🏗️ System Architecture](#-system-architecture)
- [📦 Core Module Showcase](#-core-module-showcase)
  - [💳 1. Smart Fee Portal & Payment Slip Verification](#1-smart-fee-portal--payment-slip-verification)
  - [📅 2. Classic Routine Timetable Matrix](#2-classic-routine-timetable-matrix)
  - [🏢 3. Zero-Leak Multi-Tenant Engine](#3-zero-leak-multi-tenant-engine)
  - [🎓 4. Student Information & Admission Register](#4-student-information--admission-register)
  - [📋 5. Attendance & Examination Suite](#5-attendance--examination-suite)
- [💻 Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [⚙️ Environment Variables](#️-environment-variables)
- [🌐 Cloud Deployment Guide](#-cloud-deployment-guide)
- [🤝 Contributing & License](#-contributing--license)

---

## ✨ Key Features Overview

<table>
  <tr>
    <td width="50%">
      <h3>🏢 Multi-Tenant SaaS Core</h3>
      <ul>
        <li><b>Zero Cross-Tenant Leakage</b>: Automatic thread-local school context for each request.</li>
        <li><b>Independent School Profiles</b>: Custom branding, logos, school codes, and academic sessions.</li>
        <li><b>Super Admin Control Tower</b>: Provision, manage, and inspect all schools globally.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>💳 Smart Fee Collection & Verification</h3>
      <ul>
        <li><b>Student Self-Service Portal</b>: Direct view of itemized dues and past unpaid arrears.</li>
        <li><b>Payment Proof Upload</b>: Upload UPI / Bank receipts with transaction ID tracking.</li>
        <li><b>Admin Verification Workflow</b>: 1-click Approve / Reject with audit trails and PDF challan generation.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📅 Classic Routine Timetable Grid</h3>
      <ul>
        <li><b>School Routine Matrix</b>: Days (rows) & Periods (1st to 8th + Extra Class).</li>
        <li><b>Prominent BREAK Column</b>: Vertical separator splitting morning & afternoon classes.</li>
        <li><b>Teacher Bracketing</b>: Displays subject with assigned teacher: <code>MATH (Abhi Singh)</code>.</li>
        <li><b>1-Click Print & Add</b>: Direct cell hover quick-add & print-optimized layout.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🎓 Student & Staff Lifecycle</h3>
      <ul>
        <li><b>Complete Student Directory</b>: Roll numbers, admission IDs, DOB, Aadhaar & guardian info.</li>
        <li><b>Staff & Faculty Management</b>: Subject and class allocations with contact records.</li>
        <li><b>Student Promotion Engine</b>: Smooth promotion across academic sessions.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📋 Daily Attendance Register</h3>
      <ul>
        <li><b>Class-wise Daily Marking</b>: Present, Absent, Late, Half-Day, Excused.</li>
        <li><b>Monthly Attendance Logs</b>: Automated percentage calculation and defaulter tracking.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>📚 Homework & Study Material Hub</h3>
      <ul>
        <li><b>Digital Assignments</b>: Assign homework with deadlines and attachments.</li>
        <li><b>E-Learning Notes</b>: PDF/Document repository accessible directly by enrolled students.</li>
        <li><b>Notice Board</b>: Role-targeted announcements for Students, Teachers, and Parents.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 👥 Role-Based Access Matrix

| Module / Feature | Super Admin | School Admin | Principal | Teacher | Student | Parent | Accountant |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Multi-School Management** | 🟢 Full | 🔴 None | 🔴 None | 🔴 None | 🔴 None | 🔴 None | 🔴 None |
| **School Settings & Sessions** | 🟢 Full | 🟢 Full | 🟢 Full | 🔴 None | 🔴 None | 🔴 None | 🔴 None |
| **Fee Structure & Invoicing** | 🟢 Full | 🟢 Full | 🟡 View | 🔴 None | 🔴 None | 🔴 None | 🟢 Full |
| **Fee Verification & Receipts** | 🟢 Full | 🟢 Full | 🟡 View | 🔴 None | 🔵 Pay/Upload | 🔵 Pay/Upload | 🟢 Full |
| **Timetable Routine Matrix** | 🟢 Full | 🟢 Full | 🟢 Full | 🟡 My Schedule | 🟡 Class Routine | 🟡 Child Routine | 🔴 None |
| **Student Directory & Admissions** | 🟢 Full | 🟢 Full | 🟢 Full | 🟡 View Assigned | 🔵 My Profile | 🔵 Child Profile | 🟡 View Dues |
| **Daily Attendance Marking** | 🟢 Full | 🟢 Full | 🟢 Full | 🟢 Assigned Classes | 🟡 View Attendance | 🟡 View Attendance | 🔴 None |
| **Homework & Study Notes** | 🟢 Full | 🟢 Full | 🟢 Full | 🟢 Create & Manage | 🟡 View & Download | 🟡 View & Download | 🔴 None |
| **Examination & Marks** | 🟢 Full | 🟢 Full | 🟢 Full | 🟢 Enter Marks | 🟡 View Report Card | 🟡 View Report Card | 🔴 None |

> **Legend**: 🟢 Manage & Edit • 🟡 Read-Only View • 🔵 Personal Self-Service • 🔴 Restricted

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User([🌐 End-User Browser / Mobile])
    
    subgraph Edge Layer
        CF[Cloudflare Edge / Tunnel]
        WN[WhiteNoise Static Asset Server]
    end

    subgraph Application Tier [Django 5.x Application Server]
        TM[🛡️ TenantContextMiddleware\nExtracts Active School Context]
        Auth[🔐 Role-Based Access Control]
        
        subgraph Core Modules
            MOD_SCH[🏢 Schools & Sessions]
            MOD_ACC[👤 Accounts & Users]
            MOD_ACAD[📅 Academics & Timetable]
            MOD_STU[🎓 Students & Admissions]
            MOD_TEA[👨‍🏫 Teachers & Staff]
            MOD_FEE[💳 Fees & Slip Verification]
            MOD_ATT[📋 Attendance Register]
            MOD_EXAM[📊 Exams & Grade Cards]
            MOD_HW[📚 Homework & Materials]
        end
    end

    subgraph Persistence Layer
        Neon[(🐘 Neon Serverless PostgreSQL\nPerpetual Cloud Storage)]
        Media[(📁 Media Assets / Receipts / Photos)]
    end

    User --> CF --> WN --> TM --> Auth
    Auth --> CoreModules
    MOD_SCH & MOD_ACC & MOD_ACAD & MOD_STU & MOD_TEA & MOD_FEE & MOD_ATT & MOD_EXAM & MOD_HW --> Neon
    MOD_STU & MOD_FEE & MOD_HW --> Media
```

---

## 📦 Core Module Showcase

### 1. Smart Fee Portal & Payment Slip Verification
The fee module allows complete financial transparency between the school administration and parents/students:
- **Ledger Overview**: Real-time breakdown of `Total Invoiced`, `Total Paid`, `Under Review`, and `Net Due`.
- **Automatic Arrears Carried Forward**: Unpaid balance from previous months automatically rolls over into the next month's payable balance.
- **Proof / Slip Upload**: Students can submit digital proof (Transaction ID, Payment Mode, Screenshot / Receipt PDF).
- **Audit Verification**: School admins verify payments with 1-click confirmation or detailed rejection feedback.

```text
Student Portal: [View Due Amount] ──> [Upload Payment Slip + Txn ID]
                                                │
Admin Portal:   [Official PDF Receipt] <── [Verify Slip & Approve]
```

### 2. Classic Routine Timetable Matrix
Replaces cluttered list views with the authentic, classic school routine matrix:
- **Structured Rows & Columns**: Days on rows (`MONDAY` to `SATURDAY`) and periods (`1st` to `8th` + `EXTRA CLASS`).
- **Prominent `BREAK` Separator**: Distinct vertical column dividing the morning and afternoon sessions.
- **Teacher Bracketing**: Clean typography displaying `SUBJECT` in bold uppercase and `( Teacher Name )` right below.
- **Print Optimization**: Dedicated `@media print` CSS formats the routine into a landscape/portrait document for physical distribution.

```text
┌───────────┬──────────────┬──────────────┬──────────────┬──────────────┬───────┬──────────────┬──────────────┐
│   DAYS    │     1st      │     2nd      │     3rd      │     4th      │ BREAK │     5th      │     6th      │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────┼──────────────┼──────────────┤
│  MONDAY   │    MATHS     │   ENGLISH    │   SCIENCE    │    HINDI     │   B   │   HISTORY    │   SPORTS     │
│           │ (Abhi Singh) │(Kaushik S.)  │ (Dr. Sharma) │(Rahul Verma) │   R   │ (Anita Devi) │(Coach Kumar) │
│  TUESDAY  │   ENGLISH    │    MATHS     │   COMPUTER   │   PHYSICS    │   E   │  GEOGRAPHY   │   LIBRARY    │
│           │(Kaushik S.)  │ (Abhi Singh) │ (Pooja Rao)  │ (Dr. Sharma) │   A   │ (Anita Devi) │ (P. Tiwari)  │
│    ...    │     ...      │     ...      │     ...      │     ...      │   K   │     ...      │     ...      │
└───────────┴──────────────┴──────────────┴──────────────┴──────────────┴───────┴──────────────┴──────────────┘
```

### 3. Zero-Leak Multi-Tenant Engine
- Every entity model inherits from `TenantModel` which binds it to a `School` foreign key.
- `TenantManager` automatically filters all queries with the current request's school.
- Eliminates any risk of data spilling across different educational institutions sharing the same cluster.

---

## 💻 Tech Stack

<div align="center">

| Layer | Technologies |
| :--- | :--- |
| **Backend & Core** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white) ![Django REST Framework](https://img.shields.io/badge/DRF-A30000?style=flat-square&logo=django&logoColor=white) |
| **Database & ORM** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white) ![Neon](https://img.shields.io/badge/Neon_Serverless-00E599?style=flat-square&logo=postgresql&logoColor=black) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **Frontend UI** | ![Bootstrap](https://img.shields.io/badge/Bootstrap_5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **Reporting & Docs** | ![ReportLab](https://img.shields.io/badge/ReportLab_PDF-3B82F6?style=flat-square) ![openpyxl](https://img.shields.io/badge/Excel_openpyxl-107C41?style=flat-square&logo=microsoftexcel&logoColor=white) |
| **Web Server & CDN** | ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white) ![WhiteNoise](https://img.shields.io/badge/WhiteNoise-000000?style=flat-square) ![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=flat-square&logo=cloudflare&logoColor=white) |
| **Hosting & Cloud** | ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white) |

</div>

---

## 📁 Project Structure

```text
school-erp/
├── 📁 academics/          # Classes, sections, subjects & routine timetable grid
├── 📁 accounts/           # User model, RBAC roles, tenant middleware & auth
├── 📁 attendance/         # Class-wise daily student attendance marking
├── 📁 dashboard/          # Dynamic dashboards for SuperAdmin, Admin, Teacher, Student, Parent
├── 📁 examinations/       # Exams setup, marks entry, grades & report cards
├── 📁 fees/               # Invoicing, fee heads, online payment proofs & PDF receipts
├── 📁 homework/           # Homework assignments, study material vault, notice board
├── 📁 schools/            # Multi-school tenant entities & academic sessions
├── 📁 students/           # Student admission directory, profiles & guardian records
├── 📁 teachers/           # Staff directory, subject & class allocations
├── 📁 templates/          # Responsive Bootstrap 5 HTML templates
├── 📁 static/             # Custom stylesheets, brand logos & icons
├── 📁 school_erp/         # Django configuration, settings & root URL router
├── 📄 build.sh            # Production deployment script (collectstatic, migrate)
├── 📄 render.yaml         # Render Infrastructure as Code (IaC) blueprint
├── 📄 requirements.txt    # Python dependencies
└── 📄 manage.py           # Django command-line utility
```

---

## 🚀 Quick Start Guide

Follow these steps to run the application on your local machine:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Abhi2701singh/school-erp.git
cd school-erp
```

### 2️⃣ Set Up Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / PowerShell)
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configure Environment
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Add your local settings:
```env
DJANGO_SECRET_KEY=your-local-secret-key-32chars
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
# Leave DATABASE_URL blank to automatically use local SQLite, or add PostgreSQL URL:
# DATABASE_URL=postgresql://user:password@localhost:5432/school_erp
```

### 5️⃣ Run Migrations & Create Administrator
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6️⃣ Start Development Server
```bash
python manage.py runserver
```
Open **`http://127.0.0.1:8000/`** in your browser to access the portal!

---

## ⚙️ Environment Variables

| Variable | Required | Default | Purpose |
| :--- | :---: | :---: | :--- |
| `DJANGO_SECRET_KEY` | **Yes** | Fallback Key | Cryptographic signing key for sessions & tokens. |
| `DJANGO_DEBUG` | No | `False` | Enables Django debug mode (`True` for local dev). |
| `ALLOWED_HOSTS` | No | `*` | Comma-separated domain list allowed to connect. |
| `DATABASE_URL` | No | `SQLite3` | PostgreSQL connection URL (e.g., Neon Cloud Postgres). |
| `PYTHON_VERSION` | No | `3.11.8` | Python runtime version for cloud builders. |

---

## 🌐 Cloud Deployment Guide

### Deploy to Render (Recommended)

This project is pre-configured with **Infrastructure as Code** via [`render.yaml`](file:///Users/abhinavsingh/Documents/school/render.yaml):

1. **Push your repository** to GitHub.
2. Sign in to [Render.com](https://render.com/) and click **New +** ➔ **Blueprint**.
3. Select your `school-erp` repository.
4. Render will automatically configure:
   - Python 3.11 build runtime.
   - Build command: `bash build.sh` (installs packages, compiles static assets with WhiteNoise, runs database migrations).
   - Production web server: `gunicorn school_erp.wsgi:application`.

### Perpetual Cloud Storage with Neon Postgres

To prevent data loss across cloud restarts, connect a **Neon Serverless PostgreSQL** database:
1. Create a free PostgreSQL database on [Neon.tech](https://neon.tech/).
2. Copy your connection string:
   ```text
   postgresql://<user>:<password>@<ep-id>.us-east-1.aws.neon.tech/<dbname>?sslmode=require
   ```
3. Set `DATABASE_URL` in your Render Environment Variables.

---

## 🤝 Contributing & License

We welcome community contributions, suggestions, and improvements!

1. **Fork** the Project.
2. **Create your Feature Branch** (`git checkout -b feature/NewFeature`).
3. **Commit your Changes** (`git commit -m 'Add NewFeature'`).
4. **Push to the Branch** (`git push origin feature/NewFeature`).
5. **Open a Pull Request**.

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/Abhi2701singh">Abhinav Singh</a> for Modern Educational Excellence.</sub>
</div>
