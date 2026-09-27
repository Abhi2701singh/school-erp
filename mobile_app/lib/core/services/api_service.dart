import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'storage_service.dart';

class ApiService {
  static Future<Map<String, String>> _getHeaders({bool isMultipart = false}) async {
    final token = await StorageService.getToken();
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Token $token';
    }
    return headers;
  }

  static Future<http.Response> get(String url) async {
    final headers = await _getHeaders();
    return await http.get(Uri.parse(url), headers: headers);
  }

  static Future<http.Response> post(String url, Map<String, dynamic> body) async {
    final headers = await _getHeaders();
    return await http.post(
      Uri.parse(url),
      headers: headers,
      body: jsonEncode(body),
    );
  }

  static Future<http.Response> postMultipart(
    String url, {
    required Map<String, String> fields,
    File? file,
    String fileField = 'proof_file',
  }) async {
    final uri = Uri.parse(url);
    final request = http.MultipartRequest('POST', uri);

    final headers = await _getHeaders(isMultipart: true);
    request.headers.addAll(headers);
    request.fields.addAll(fields);

    if (file != null && await file.exists()) {
      final ext = file.path.split('.').last.toLowerCase();
      String mimeType = 'image/jpeg';
      if (ext == 'png') mimeType = 'image/png';
      if (ext == 'pdf') mimeType = 'application/pdf';
      if (ext == 'webp') mimeType = 'image/webp';

      final typeParts = mimeType.split('/');
      request.files.add(await http.MultipartFile.fromPath(
        fileField,
        file.path,
        contentType: MediaType(typeParts[0], typeParts[1]),
      ));
    }

    final streamedResponse = await request.send();
    return await http.Response.fromStream(streamedResponse);
  }
}
