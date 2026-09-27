import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/fee_provider.dart';
import '../../models/fee_model.dart';
import '../../widgets/common_widgets.dart';
import 'upload_fee_proof_screen.dart';

class FeePortalScreen extends StatefulWidget {
  const FeePortalScreen({super.key});

  @override
  State<FeePortalScreen> createState() => _FeePortalScreenState();
}

class _FeePortalScreenState extends State<FeePortalScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final p = Provider.of<FeeProvider>(context, listen: false);
      p.fetchFees();
      p.fetchSubmissions();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final feeProvider = Provider.of<FeeProvider>(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Fee Portal & Payments'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.primary,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          labelStyle: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 13),
          tabs: const [
            Tab(text: 'Fee Dues & Invoices'),
            Tab(text: 'Payment Submissions'),
          ],
        ),
      ),
      body: feeProvider.isLoading
          ? const LoadingIndicator(message: 'Loading fee records...')
          : TabBarView(
              controller: _tabController,
              children: [
                _buildFeeDuesTab(feeProvider),
                _buildSubmissionsTab(feeProvider),
              ],
            ),
    );
  }

  Widget _buildFeeDuesTab(FeeProvider provider) {
    final summary = provider.summary;

    return RefreshIndicator(
      onRefresh: () async {
        await provider.fetchFees();
        await provider.fetchSubmissions();
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Financial Summary Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: AppColors.feeGradient,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF8B5CF6).withOpacity(0.3),
                    blurRadius: 16,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Total Outstanding Due',
                        style: GoogleFonts.inter(color: Colors.white.withOpacity(0.9), fontSize: 13),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          summary?.totalDue == 0 ? 'CLEARED' : 'PENDING',
                          style: GoogleFonts.inter(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '₹${summary?.totalDue.toStringAsFixed(2) ?? "0.00"}',
                    style: GoogleFonts.poppins(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  if ((summary?.pastArrears ?? 0) > 0) ...[
                    const SizedBox(height: 4),
                    Text(
                      'Includes ₹${summary?.pastArrears.toStringAsFixed(2)} past unpaid arrears',
                      style: GoogleFonts.inter(color: Colors.yellowAccent, fontSize: 11, fontWeight: FontWeight.w600),
                    ),
                  ],
                  const Divider(color: Colors.white24, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildMiniStat('Invoiced', '₹${summary?.totalInvoiced.toStringAsFixed(0) ?? "0"}'),
                      _buildMiniStat('Paid', '₹${summary?.totalPaid.toStringAsFixed(0) ?? "0"}'),
                      _buildMiniStat('Under Review', '₹${summary?.totalUnderReview.toStringAsFixed(0) ?? "0"}'),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Invoices List
            Text(
              'Fee Breakdown',
              style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 12),

            if (provider.fees.isEmpty)
              const EmptyStateWidget(
                title: 'No Fee Invoices',
                message: 'No fee structures or dues assigned for your class.',
              )
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: provider.fees.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final fee = provider.fees[index];
                  return _buildFeeCard(fee);
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniStat(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: GoogleFonts.inter(fontSize: 11, color: Colors.white70)),
        const SizedBox(height: 2),
        Text(value, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white)),
      ],
    );
  }

  Widget _buildFeeCard(FeeItemModel fee) {
    final isPaid = fee.status == 'PAID' || fee.netDue <= 0;
    final isUnderReview = fee.hasPendingSubmission;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  fee.feeHeadName,
                  style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                ),
              ),
              _buildStatusPill(fee),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Due Date', style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted)),
                  Text(fee.dueDate, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('Net Payable', style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted)),
                  Text(
                    '₹${fee.netDue.toStringAsFixed(2)}',
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: isPaid ? AppColors.emerald : AppColors.rose,
                    ),
                  ),
                ],
              ),
            ],
          ),
          if (fee.previousArrears > 0) ...[
            const SizedBox(height: 6),
            Text(
              '+ ₹${fee.previousArrears.toStringAsFixed(2)} past arrears (Total: ₹${fee.totalPayableWithArrears.toStringAsFixed(2)})',
              style: GoogleFonts.inter(fontSize: 11, color: AppColors.rose, fontWeight: FontWeight.w500),
            ),
          ],
          const SizedBox(height: 14),
          if (!isPaid)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: isUnderReview
                    ? null
                    : () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => UploadFeeProofScreen(fee: fee)),
                        );
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor: isUnderReview ? AppColors.accent : AppColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: Icon(isUnderReview ? Icons.hourglass_top_rounded : Icons.upload_file_rounded, size: 18),
                label: Text(
                  isUnderReview ? 'Slip Under Review' : 'Pay / Submit Payment Slip',
                  style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildStatusPill(FeeItemModel fee) {
    if (fee.status == 'PAID' || fee.netDue <= 0) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(color: AppColors.emerald.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
        child: Text('PAID', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.emerald)),
      );
    } else if (fee.hasPendingSubmission) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(color: AppColors.accent.withOpacity(0.15), borderRadius: BorderRadius.circular(8)),
        child: Text('UNDER REVIEW', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: const Color(0xFFB45309))),
      );
    } else if (fee.isOverdue) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(color: AppColors.rose.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
        child: Text('OVERDUE', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.rose)),
      );
    } else {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(color: AppColors.surfaceMuted, borderRadius: BorderRadius.circular(8)),
        child: Text('PENDING', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSecondary)),
      );
    }
  }

  Widget _buildSubmissionsTab(FeeProvider provider) {
    return RefreshIndicator(
      onRefresh: () => provider.fetchSubmissions(),
      child: provider.submissions.isEmpty
          ? EmptyStateWidget(
              title: 'No Payment Submissions',
              message: 'You have not submitted any fee payment slips yet.',
              icon: Icons.receipt_long_rounded,
              onRefresh: () => provider.fetchSubmissions(),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: provider.submissions.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final item = provider.submissions[index];
                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            item.submissionNo,
                            style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.primary),
                          ),
                          _buildSubmissionStatusBadge(item.status, item.statusDisplay),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        item.feeHeadName,
                        style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Amount: ₹${item.amount.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.bold)),
                          Text(item.paymentModeDisplay, style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text('Txn ID: ${item.transactionId}', style: GoogleFonts.inter(fontSize: 12, color: AppColors.textMuted)),
                      if (item.rejectionReason != null && item.rejectionReason!.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(color: AppColors.rose.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                          child: Text(
                            'Reason: ${item.rejectionReason}',
                            style: GoogleFonts.inter(fontSize: 11, color: AppColors.rose, fontWeight: FontWeight.w500),
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              },
            ),
    );
  }

  Widget _buildSubmissionStatusBadge(String status, String display) {
    Color color = AppColors.accent;
    if (status == 'VERIFIED') color = AppColors.emerald;
    if (status == 'REJECTED') color = AppColors.rose;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(6)),
      child: Text(display, style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: color)),
    );
  }
}
