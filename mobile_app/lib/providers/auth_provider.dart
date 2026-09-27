import 'dart:convert';
import 'package:flutter/material.dart';
import '../core/constants/api_constants.dart';
import '../core/services/api_service.dart';
import '../core/services/storage_service.dart';
import '../models/user_model.dart';
import '../models/student_model.dart';

class AuthProvider with ChangeNotifier {
  bool _isLoading = false;
  String? _errorMessage;
  UserModel? _user;
  SchoolModel? _school;
  StudentModel? _studentProfile;
  String? _token;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  UserModel? get user => _user;
  SchoolModel? get school => _school;
  StudentModel? get studentProfile => _studentProfile;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;

  Future<bool> tryAutoLogin() async {
    final token = await StorageService.getToken();
    final userJson = await StorageService.getUserJson();
    if (token != null && userJson != null) {
      _token = token;
      _user = UserModel.fromJson(jsonDecode(userJson));
      notifyListeners();
      await fetchProfile();
      return true;
    }
    return false;
  }

  Future<bool> login({
    required String username,
    required String password,
    String? schoolCode,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await ApiService.post(ApiConstants.login, {
        'username': username,
        'password': password,
        'school_code': schoolCode ?? '',
      });

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _token = data['token'];
        _user = UserModel.fromJson(data['user']);
        if (data['school'] != null) {
          _school = SchoolModel.fromJson(data['school']);
        }
        if (data['student_profile'] != null) {
          _studentProfile = StudentModel.fromJson(data['student_profile']);
        }

        await StorageService.saveAuthData(
          token: _token!,
          userJson: jsonEncode(data['user']),
          role: _user!.role,
          schoolCode: schoolCode,
        );

        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = data['error'] ?? 'Login failed. Please check credentials.';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Network connection error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> fetchProfile() async {
    try {
      final response = await ApiService.get(ApiConstants.profile);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _user = UserModel.fromJson(data['user']);
        if (data['school'] != null) {
          _school = SchoolModel.fromJson(data['school']);
        }
        if (data['student_profile'] != null) {
          _studentProfile = StudentModel.fromJson(data['student_profile']);
        }
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    _school = null;
    _studentProfile = null;
    await StorageService.clear();
    notifyListeners();
  }
}
