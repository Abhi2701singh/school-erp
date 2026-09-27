# 📱 EduManage ERP - Flutter Mobile Application

A cross-platform (Android & iOS) mobile application for **EduManage School ERP**. Connected directly to the centralized **Django 5.x REST API** and **Neon PostgreSQL Cloud Database** for instant real-time synchronization.

---

## 🌟 Key Features

- 🔐 **Multi-Role Authentication**: Student, Parent, Teacher, and Administrator login with optional School Code verification.
- 📊 **Dynamic Dashboard**:
  - Student profile card with Class, Section, and Roll No.
  - Real-time Attendance percentage gauge.
  - Outstanding Fee Dues with past arrears notice.
  - Active Homework and School Announcements.
  - Today's Class Routine preview.
- 📅 **Classic Routine Timetable Matrix**:
  - **Weekly Matrix Grid View**: Classic school routine layout with `DAYS` (Monday-Saturday), periods (1st-8th + Extra Class), and vertical `BREAK` column.
  - **Day-by-Day View**: Swipeable day tabs with period timing and `( Teacher Name )` underneath subjects.
- 💳 **Smart Fee Portal & Digital Slip Upload**:
  - Itemized breakdown of Tuition, Transport, Admission, and Exam fees.
  - Unpaid past arrears rollup.
  - **Payment Proof Submission**: Upload UPI / Bank receipt screenshot with transaction ID (overpayment is strictly validated).
  - Track verification status (`Pending Verification` ➔ `Approved`).
- 📋 **Daily Attendance Register**:
  - Monthly attendance percentage, present/absent counts, and historical date logs.
- 📚 **Homework & Study Materials**:
  - Active homework assignments with due dates and downloadable attachments.
  - Searchable subject-wise study notes and PDF documents.
- 📢 **School Notice Board**:
  - Real-time announcements with role-based targeting and attachments.
- 🏆 **Examination & Report Cards**:
  - Term results, theory/practical breakdown, overall percentage, and grades.

---

## 🚀 Running the App Locally

### Prerequisites
- [Flutter SDK](https://flutter.dev/docs/get-started/install) (`>= 3.0.0`)
- Android Studio / Xcode
- An Android device or Emulator

### 1. Install Dependencies
```bash
cd mobile_app
flutter pub get
```

### 2. Configure Backend URL
Open `lib/core/constants/api_constants.dart` and set your backend URL:
- **Production (Render)**: `https://edumanage-school-erp.onrender.com/api/v1`
- **Android Emulator**: `http://10.0.2.2:8000/api/v1`
- **iOS Simulator**: `http://127.0.0.1:8000/api/v1`

### 3. Run the App
```bash
flutter run
```

### 4. Build Android APK
```bash
flutter build apk --release
```
The output file will be generated at `build/app/outputs/flutter-apk/app-release.apk`.
