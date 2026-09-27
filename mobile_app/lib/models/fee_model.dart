class FeeSummaryModel {
  final double totalInvoiced;
  final double totalPaid;
  final double totalDue;
  final double totalUnderReview;
  final double pastArrears;

  FeeSummaryModel({
    required this.totalInvoiced,
    required this.totalPaid,
    required this.totalDue,
    required this.totalUnderReview,
    required this.pastArrears,
  });

  factory FeeSummaryModel.fromJson(Map<String, dynamic> json) {
    return FeeSummaryModel(
      totalInvoiced: (json['total_invoiced'] ?? 0).toDouble(),
      totalPaid: (json['total_paid'] ?? 0).toDouble(),
      totalDue: (json['total_due'] ?? 0).toDouble(),
      totalUnderReview: (json['total_under_review'] ?? 0).toDouble(),
      pastArrears: (json['past_arrears'] ?? 0).toDouble(),
    );
  }
}

class FeeItemModel {
  final int id;
  final int feeHead;
  final String feeHeadName;
  final double amountDue;
  final double amountDiscount;
  final double amountPaid;
  final double netDue;
  final String dueDate;
  final String status;
  final bool isOverdue;
  final double previousArrears;
  final double totalPayableWithArrears;
  final bool hasPendingSubmission;
  final double underReviewAmount;

  FeeItemModel({
    required this.id,
    required this.feeHead,
    required this.feeHeadName,
    required this.amountDue,
    required this.amountDiscount,
    required this.amountPaid,
    required this.netDue,
    required this.dueDate,
    required this.status,
    required this.isOverdue,
    required this.previousArrears,
    required this.totalPayableWithArrears,
    required this.hasPendingSubmission,
    required this.underReviewAmount,
  });

  factory FeeItemModel.fromJson(Map<String, dynamic> json) {
    return FeeItemModel(
      id: json['id'] ?? 0,
      feeHead: json['fee_head'] ?? 0,
      feeHeadName: json['fee_head_name'] ?? 'Fee',
      amountDue: double.tryParse(json['amount_due']?.toString() ?? '0') ?? 0.0,
      amountDiscount: double.tryParse(json['amount_discount']?.toString() ?? '0') ?? 0.0,
      amountPaid: double.tryParse(json['amount_paid']?.toString() ?? '0') ?? 0.0,
      netDue: double.tryParse(json['net_due']?.toString() ?? '0') ?? 0.0,
      dueDate: json['due_date'] ?? '',
      status: json['status'] ?? 'PENDING',
      isOverdue: json['is_overdue'] ?? false,
      previousArrears: double.tryParse(json['previous_arrears']?.toString() ?? '0') ?? 0.0,
      totalPayableWithArrears: double.tryParse(json['total_payable_with_arrears']?.toString() ?? '0') ?? 0.0,
      hasPendingSubmission: json['has_pending_submission'] ?? false,
      underReviewAmount: double.tryParse(json['under_review_amount']?.toString() ?? '0') ?? 0.0,
    );
  }
}

class PaymentSubmissionModel {
  final int id;
  final String submissionNo;
  final int studentFee;
  final String feeHeadName;
  final double amount;
  final String paymentDate;
  final String paymentMode;
  final String paymentModeDisplay;
  final String transactionId;
  final String? bankName;
  final String? proofFile;
  final String? studentNote;
  final String status;
  final String statusDisplay;
  final String submittedAt;
  final String? rejectionReason;

  PaymentSubmissionModel({
    required this.id,
    required this.submissionNo,
    required this.studentFee,
    required this.feeHeadName,
    required this.amount,
    required this.paymentDate,
    required this.paymentMode,
    required this.paymentModeDisplay,
    required this.transactionId,
    this.bankName,
    this.proofFile,
    this.studentNote,
    required this.status,
    required this.statusDisplay,
    required this.submittedAt,
    this.rejectionReason,
  });

  factory PaymentSubmissionModel.fromJson(Map<String, dynamic> json) {
    return PaymentSubmissionModel(
      id: json['id'] ?? 0,
      submissionNo: json['submission_no'] ?? '',
      studentFee: json['student_fee'] ?? 0,
      feeHeadName: json['fee_head_name'] ?? 'Fee Head',
      amount: double.tryParse(json['amount']?.toString() ?? '0') ?? 0.0,
      paymentDate: json['payment_date'] ?? '',
      paymentMode: json['payment_mode'] ?? 'UPI',
      paymentModeDisplay: json['payment_mode_display'] ?? json['payment_mode'] ?? 'UPI',
      transactionId: json['transaction_id'] ?? '',
      bankName: json['bank_name'],
      proofFile: json['proof_file'],
      studentNote: json['student_note'],
      status: json['status'] ?? 'PENDING_VERIFICATION',
      statusDisplay: json['status_display'] ?? 'Pending Verification',
      submittedAt: json['submitted_at'] ?? '',
      rejectionReason: json['rejection_reason'],
    );
  }
}
