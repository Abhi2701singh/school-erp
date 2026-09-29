import 'dart:convert';
import 'package:flutter/material.dart';
import '../core/constants/api_constants.dart';
import '../core/services/api_service.dart';
import '../models/timetable_model.dart';

class TimetableProvider with ChangeNotifier {
  bool _isLoading = false;
  String? _errorMessage;

  String _selectedClass = '';
  String _selectedSection = '';
  Map<String, String> _periodTimings = {};
  String _breakTiming = '11:40 AM - 12:20 PM';
  List<GridRowModel> _gridRows = [];
  List<TimetableEntryModel> _allEntries = [];
  int _selectedDayIndex = 0; // 0=Mon, 1=Tue, 2=Wed, etc.

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get selectedClass => _selectedClass;
  String get selectedSection => _selectedSection;
  Map<String, String> get periodTimings => _periodTimings;
  String get breakTiming => _breakTiming;
  List<GridRowModel> get gridRows => _gridRows;
  List<TimetableEntryModel> get allEntries => _allEntries;
  int get selectedDayIndex => _selectedDayIndex;

  void setSelectedDayIndex(int index) {
    _selectedDayIndex = index;
    notifyListeners();
  }

  Future<void> fetchTimetable({int? classId, int? sectionId}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      String url = ApiConstants.timetable;
      if (classId != null) {
        url += '?class_id=$classId';
        if (sectionId != null) {
          url += '&section_id=$sectionId';
        }
      }

      final response = await ApiService.get(url);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        final cls = data['selected_class'];
        _selectedClass = cls != null ? cls['name'] ?? '' : '';

        final sec = data['selected_section'];
        _selectedSection = sec != null ? sec['name'] ?? '' : '';

        _breakTiming = data['break_timing'] ?? '11:40 AM - 12:20 PM';

        final rawTimings = data['period_timings'];
        if (rawTimings is Map) {
          _periodTimings = rawTimings.map((k, v) => MapEntry(k.toString(), v.toString()));
        } else {
          _periodTimings = {
            '1': '09:00 AM - 09:40 AM',
            '2': '09:40 AM - 10:20 AM',
            '3': '10:20 AM - 11:00 AM',
            '4': '11:00 AM - 11:40 AM',
            '5': '12:20 PM - 01:00 PM',
            '6': '01:00 PM - 01:40 PM',
            '7': '01:40 PM - 02:20 PM',
            '8': '02:20 PM - 03:00 PM',
            '9': '03:00 PM - 03:40 PM',
          };
        }

        _gridRows = (data['grid_rows'] as List? ?? []).map((e) => GridRowModel.fromJson(e)).toList();
        _allEntries = (data['all_entries'] as List? ?? []).map((e) => TimetableEntryModel.fromJson(e)).toList();

        // Default to current weekday if valid
        final now = DateTime.now();
        if (now.weekday >= 1 && now.weekday <= 6) {
          _selectedDayIndex = now.weekday - 1;
        }

        _isLoading = false;
        notifyListeners();
      } else {
        _errorMessage = 'Failed to load timetable';
        _isLoading = false;
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = 'Error: $e';
      _isLoading = false;
      notifyListeners();
    }
  }
}
