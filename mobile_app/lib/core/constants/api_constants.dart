class ApiConstants {
  // Production Cloud Base URL (Render / Custom Domain)
  // For local emulator: 'http://10.0.2.2:8000/api/v1'
  // For iOS simulator: 'http://127.0.0.1:8000/api/v1'
  // For physical device / production: 'https://edumanage-school-erp.onrender.com/api/v1'
  static const String baseUrl = 'https://edumanage-school-erp.onrender.com/api/v1';

  // Auth endpoints
  static const String login = '$baseUrl/auth/login/';
  static const String profile = '$baseUrl/auth/profile/';

  // Dashboards
  static const String studentDashboard = '$baseUrl/student/dashboard/';

  // Timetable Routine Matrix
  static const String timetable = '$baseUrl/timetable/';

  // Fees
  static const String fees = '$baseUrl/fees/';
  static const String feeSubmissions = '$baseUrl/fees/submissions/';

  // Attendance
  static const String attendance = '$baseUrl/attendance/';

  // Homework & Study Materials
  static const String homework = '$baseUrl/homework/';
  static const String studyMaterials = '$baseUrl/study-materials/';

  // Notices & Exams
  static const String notices = '$baseUrl/notices/';
  static const String reportCard = '$baseUrl/exams/report-card/';
}
