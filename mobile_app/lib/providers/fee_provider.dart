import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import '../core/constants/api_constants.dart';
import '../core/services/api_service.dart';
import '../models/fee_model.dart';

class FeeProvider with ChangeNotifier {
  bool _isLoading = false;
  bool _isSubmitting = false;
  String? _errorMessage;
  String? _successMessage;

  FeeSummaryModel? _summary;
  List<FeeItemModel> _fees = [];
  List<PaymentSubmissionModel> _submissions = [];

  bool get isLoading => _isLoading;
  bool get isSubmitting => _isSubmitting;
  String? get errorMessage => _errorMessage;
  String? get successMessage => _successMessage;
  FeeSummaryModel? get summary => _summary;
  List<FeeItemModel> get fees => _fees;
  List<PaymentSubmissionModel> get submissions => _submissions;

  Future<void> fetchFees() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await ApiService.get(ApiConstants.fees);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['summary'] != null) {
          _summary = FeeSummaryModel.fromJson(data['summary']);
        }
        _fees = (data['fees'] as List? ?? []).map((e) => FeeItemModel.fromJson(e)).toList();
        _isLoading = false;
        notifyListeners();
      } else {
        _errorMessage = 'Failed to load fees';
        _isLoading = false;
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = 'Error: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchSubmissions() async {
    try {
      final response = await ApiService.get(ApiConstants.feeSubmissions);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List? ?? [];
        _submissions = data.map((e) => PaymentSubmissionModel.fromJson(e)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<bool> submitPaymentProof({
    required int feeId,
    required double amount,
    required String paymentMode,
    required String transactionId,
    String? bankName,
    String? studentNote,
    File? proofFile,
  }) async {
    _isSubmitting = true;
    _errorMessage = null;
    _successMessage = null;
    notifyListeners();

    try {
      final fields = {
        'student_fee_id': feeId.toString(),
        'amount': amount.toStringAsFixed(2),
        'payment_mode': paymentMode,
        'transaction_id': transactionId,
        'bank_name': bankName ?? '',
        'student_note': studentNote ?? '',
      };

      final response = await ApiService.postMultipart(
        ApiConstants.feeSubmissions,
        fields: fields,
        file: proofFile,
        fileField: 'proof_file',
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        _successMessage = data['message'] ?? 'Payment proof submitted successfully!';
        _isSubmitting = false;
        notifyListeners();
        await fetchFees();
        await fetchSubmissions();
        return true;
      } else {
        _errorMessage = data['error'] ?? 'Submission failed';
        _isSubmitting = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Submission error: $e';
      _isSubmitting = false;
      notifyListeners();
      return false;
    }
  }
}
