import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _keyToken = 'auth_token';
  static const String _keyUserJson = 'user_json';
  static const String _keyRole = 'user_role';
  static const String _keySchoolCode = 'school_code';

  static Future<void> saveAuthData({
    required String token,
    required String userJson,
    required String role,
    String? schoolCode,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyToken, token);
    await prefs.setString(_keyUserJson, userJson);
    await prefs.setString(_keyRole, role);
    if (schoolCode != null) {
      await prefs.setString(_keySchoolCode, schoolCode);
    }
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyToken);
  }

  static Future<String?> getUserJson() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserJson);
  }

  static Future<String?> getRole() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyRole);
  }

  static Future<String?> getSchoolCode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keySchoolCode);
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyToken);
    await prefs.remove(_keyUserJson);
    await prefs.remove(_keyRole);
  }
}
