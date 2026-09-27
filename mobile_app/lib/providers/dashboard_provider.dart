import 'dart:convert';
import 'package:flutter/material.dart';
import '../core/constants/api_constants.dart';
import '../core/services/api_service.dart';
import '../models/student_model.dart';
import '../models/fee_model.dart';
import '../models/timetable_model.dart';
import '../models/common_models.dart';

class DashboardProvider with ChangeNotifier {
  bool _isLoading = false;
  String? _errorMessage;

  StudentModel? _student;
  double _attendancePercentage = 100.0;
  int _totalDays = 0;
  int _presentDays = 0;
  int _absentDays = 0;
  int _leaveDays = 0;

  FeeSummaryModel? _feeSummary;
  int _pendingFeeCount = 0;

  List<HomeworkModel> _homeworks = [];
  List<NoticeModel> _notices = [];
  List<TimetableEntryModel> _todaySchedule = [];
  String _todayDay = '';

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  StudentModel? get student => _student;
  double get attendancePercentage => _attendancePercentage;
  int get totalDays => _totalDays;
  int get presentDays => _presentDays;
  int get absentDays => _absentDays;
  int get leaveDays => _leaveDays;
  FeeSummaryModel? get feeSummary => _feeSummary;
  int get pendingFeeCount => _pendingFeeCount;
  List<HomeworkModel> get homeworks => _homeworks;
  List<NoticeModel> get notices => _notices;
  List<TimetableEntryModel> get todaySchedule => _todaySchedule;
  String get todayDay => _todayDay;

  Future<void> fetchDashboardData() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await ApiService.get(ApiConstants.studentDashboard);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        if (data['student'] != null) {
          _student = StudentModel.fromJson(data['student']);
        }

        final att = data['attendance'] ?? {};
        _attendancePercentage = (att['percentage'] ?? 100.0).toDouble();
        _totalDays = att['total_days'] ?? 0;
        _presentDays = att['present_days'] ?? 0;
        _absentDays = att['absent_days'] ?? 0;
        _leaveDays = att['leave_days'] ?? 0;

        final fees = data['fees'] ?? {};
        _feeSummary = FeeSummaryModel.fromJson(fees);
        _pendingFeeCount = fees['pending_fee_items_count'] ?? 0;

        _homeworks = (data['homeworks'] as List? ?? []).map((e) => HomeworkModel.fromJson(e)).toList();
        _notices = (data['notices'] as List? ?? []).map((e) => NoticeModel.fromJson(e)).toList();
        _todaySchedule = (data['today_schedule'] as List? ?? []).map((e) => TimetableEntryModel.fromJson(e)).toList();
        _todayDay = data['today_day'] ?? '';

        _isLoading = false;
        notifyListeners();
      } else {
        _errorMessage = 'Failed to load dashboard data (${response.statusCode})';
        _isLoading = false;
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = 'Network error: $e';
      _isLoading = false;
      notifyListeners();
    }
  }
}
