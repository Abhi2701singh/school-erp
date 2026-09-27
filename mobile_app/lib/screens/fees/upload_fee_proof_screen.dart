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

  final List<Map<String, String>> _paymentModes = [
    {'value': 'UPI', 'label': 'UPI / QR Code (GPay, PhonePe, Paytm)'},
    {'value': 'BANK_TRANSFER', 'label': 'Bank Transfer / NEFT / IMPS'},
    {'value': 'NET_BANKING', 'label': 'Net Banking'},
    {'value': 'CASH_DEPOSIT', 'label': 'Cash Deposit in School A/C'},
    {'value': 'CHEQUE', 'label': 'Cheque / Demand Draft'},
  ];

  @override
  void initState() {
    super.initState();
    // Default amount to remaining net due
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

    // Strict Validation: Cannot exceed remaining net due
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
              Icon(Icons.check_circle_rounded, color: AppColors.emerald, size: 28),
              SizedBox(width: 8),
              Text('Proof Submitted!'),
            ],
          ),
          content: Text(
            'Your payment slip of ₹${enteredAmount.toStringAsFixed(2)} has been submitted for verification. School administration will verify and approve your receipt.',
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
          content: Text(feeProvider.errorMessage ?? 'Failed to submit payment proof.'),
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
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Fee Info Banner
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.primary.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.fee.feeHeadName,
                      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.primary),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Net Due Payable:', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                        Text(
                          '₹${widget.fee.netDue.toStringAsFixed(2)}',
                          style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.rose),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

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
              const SizedBox(height: 16),

              // Payment Mode Dropdown
              Text(
                'Payment Mode',
                style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 6),
              DropdownButtonFormField<String>(
                value: _selectedPaymentMode,
                decoration: const InputDecoration(),
                items: _paymentModes.map((m) {
                  return DropdownMenuItem<String>(
                    value: m['value'],
                    child: Text(m['label']!, style: GoogleFonts.inter(fontSize: 13)),
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
              const SizedBox(height: 16),

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
              const SizedBox(height: 16),

              // Bank / App Name (Optional)
              CustomTextField(
                controller: _bankNameController,
                label: 'Bank / UPI App Name (Optional)',
                hint: 'e.g. Google Pay, PhonePe, SBI, HDFC',
                prefixIcon: Icons.account_balance_rounded,
              ),
              const SizedBox(height: 16),

              // Attach Receipt / Screenshot
              Text(
                'Payment Proof / Receipt Screenshot',
                style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),

              if (_selectedProofFile != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.image_rounded, color: AppColors.primary, size: 28),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _selectedProofFile!.path.split('/').last,
                          style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close_rounded, color: AppColors.rose, size: 20),
                        onPressed: () {
                          setState(() {
                            _selectedProofFile = null;
                          });
                        },
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
                      icon: const Icon(Icons.photo_library_rounded, size: 18),
                      label: const Text('Gallery'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt_rounded, size: 18),
                      label: const Text('Camera'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Student Note (Optional)
              CustomTextField(
                controller: _noteController,
                label: 'Notes / Remarks (Optional)',
                hint: 'Any message for the school accountant...',
                maxLines: 2,
              ),
              const SizedBox(height: 28),

              // Submit Button
              SizedBox(
                width: double.infinity,
                child: CustomButton(
                  text: 'Submit Payment Slip for Review',
                  isLoading: feeProvider.isSubmitting,
                  icon: Icons.send_rounded,
                  onPressed: _handleSubmit,
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
