import 'dart:io';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../models/fee_model.dart';
import '../../providers/fee_provider.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/common_widgets.dart';

class UploadFeeProofScreen extends StatefulWidget {
  final FeeItemModel fee;

  const UploadFeeProofScreen({super.key, required this.fee});

  @override
  State<UploadFeeProofScreen> createState() => _UploadFeeProofScreenState();
}

class _UploadFeeProofScreenState extends State<UploadFeeProofScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _txnIdController = TextEditingController();
  final _bankNameController = TextEditingController();
  final _noteController = TextEditingController();

  String _selectedPaymentMode = 'UPI';
  File? _selectedProofFile;
  final ImagePicker _picker = ImagePicker();

  final List<Map<String, dynamic>> _paymentModes = [
    {'value': 'UPI', 'label': 'UPI / QR (GPay, PhonePe, Paytm)', 'icon': Icons.qr_code_rounded},
    {'value': 'BANK_TRANSFER', 'label': 'Bank Transfer / NEFT / IMPS', 'icon': Icons.account_balance_rounded},
    {'value': 'NET_BANKING', 'label': 'Net Banking', 'icon': Icons.language_rounded},
    {'value': 'CASH_DEPOSIT', 'label': 'Cash Deposit in Bank', 'icon': Icons.payments_rounded},
    {'value': 'CHEQUE', 'label': 'Cheque / Demand Draft', 'icon': Icons.receipt_rounded},
  ];

  @override
  void initState() {
    super.initState();
    _amountController.text = widget.fee.netDue.toStringAsFixed(2);
  }

  @override
  void dispose() {
    _amountController.dispose();
    _txnIdController.dispose();
    _bankNameController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picked = await _picker.pickImage(source: source, imageQuality: 85);
    if (picked != null) {
      setState(() {
        _selectedProofFile = File(picked.path);
      });
    }
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    final enteredAmount = double.tryParse(_amountController.text) ?? 0.0;

    if (enteredAmount > widget.fee.netDue) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Amount ₹$enteredAmount exceeds remaining due of ₹${widget.fee.netDue.toStringAsFixed(2)}. Overpayment is not permitted.'),
          backgroundColor: AppColors.rose,
        ),
      );
      return;
    }

    final feeProvider = Provider.of<FeeProvider>(context, listen: false);
    final success = await feeProvider.submitPaymentProof(
      feeId: widget.fee.id,
      amount: enteredAmount,
      paymentMode: _selectedPaymentMode,
      transactionId: _txnIdController.text.trim(),
      bankName: _bankNameController.text.trim(),
      studentNote: _noteController.text.trim(),
      proofFile: _selectedProofFile,
    );

    if (!mounted) return;

    if (success) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.check_circle_rounded, color: AppColors.emerald, size: 26),
              SizedBox(width: 8),
              Text('Slip Submitted!'),
            ],
          ),
          content: Text(
            'Your payment receipt of ₹${enteredAmount.toStringAsFixed(2)} has been submitted for review. School administration will verify and credit your balance.',
            style: GoogleFonts.inter(fontSize: 13),
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                Navigator.pop(context);
              },
              child: const Text('Back to Fees'),
            ),
          ],
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(feeProvider.errorMessage ?? 'Failed to submit payment slip.'),
          backgroundColor: AppColors.rose,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final feeProvider = Provider.of<FeeProvider>(context);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Submit Payment Slip'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Fee Info Banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.primarySubtle,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.fee.feeHeadName,
                      style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.primary),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Net Due Payable:', style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
                        Text(
                          '₹${widget.fee.netDue.toStringAsFixed(2)}',
                          style: GoogleFonts.poppins(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.rose),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),

              // Amount to Pay
              CustomTextField(
                controller: _amountController,
                label: 'Payment Amount (₹)',
                hint: 'Enter payment amount',
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                prefixIcon: Icons.currency_rupee_rounded,
                validator: (val) {
                  if (val == null || val.isEmpty) return 'Enter amount';
                  final numVal = double.tryParse(val);
                  if (numVal == null || numVal <= 0) return 'Enter valid amount';
                  if (numVal > widget.fee.netDue) return 'Cannot exceed ₹${widget.fee.netDue.toStringAsFixed(2)}';
                  return null;
                },
              ),
              const SizedBox(height: 14),

              // Payment Mode Dropdown
              Text(
                'Payment Mode',
                style: GoogleFonts.inter(fontSize: 12.5, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 6),
              DropdownButtonFormField<String>(
                initialValue: _selectedPaymentMode,
                decoration: const InputDecoration(
                  contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
                items: _paymentModes.map((m) {
                  return DropdownMenuItem<String>(
                    value: m['value'] as String,
                    child: Row(
                      children: [
                        Icon(m['icon'] as IconData, size: 16, color: AppColors.textSecondary),
                        const SizedBox(width: 8),
                        Text(m['label'] as String, style: GoogleFonts.inter(fontSize: 12.5)),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _selectedPaymentMode = val;
                    });
                  }
                },
              ),
              const SizedBox(height: 14),

              // Transaction / UTR ID
              CustomTextField(
                controller: _txnIdController,
                label: 'Transaction / UTR / Reference ID',
                hint: 'e.g. 423456789012 or Cheque No.',
                prefixIcon: Icons.tag_rounded,
                validator: (val) {
                  if (val == null || val.trim().isEmpty) return 'Enter Transaction / UTR ID';
                  return null;
                },
              ),
              const SizedBox(height: 14),

              // Bank / App Name
              CustomTextField(
                controller: _bankNameController,
                label: 'Bank / UPI App Name (Optional)',
                hint: 'e.g. Google Pay, PhonePe, SBI, HDFC',
                prefixIcon: Icons.account_balance_rounded,
              ),
              const SizedBox(height: 14),

              // Attach Receipt / Screenshot
              Text(
                'Payment Slip / Screenshot',
                style: GoogleFonts.inter(fontSize: 12.5, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 6),

              if (_selectedProofFile != null) ...[
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.image_rounded, color: AppColors.primary, size: 24),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _selectedProofFile!.path.split('/').last,
                          style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close_rounded, color: AppColors.rose, size: 18),
                        onPressed: () => setState(() => _selectedProofFile = null),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
              ],

              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickImage(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library_rounded, size: 16),
                      label: const Text('Gallery'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 10),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt_rounded, size: 16),
                      label: const Text('Camera'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 10),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              // Student Note
              CustomTextField(
                controller: _noteController,
                label: 'Notes / Remarks (Optional)',
                hint: 'Any remarks for school accounts team...',
                maxLines: 2,
              ),
              const SizedBox(height: 22),

              // Submit Button
              SizedBox(
                width: double.infinity,
                child: CustomButton(
                  text: 'Submit Slip for Review',
                  isLoading: feeProvider.isSubmitting,
                  icon: Icons.send_rounded,
                  onPressed: _handleSubmit,
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}
