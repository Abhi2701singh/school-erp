import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../models/common_models.dart';
import '../../widgets/common_widgets.dart';

class ReportCardScreen extends StatefulWidget {
  const ReportCardScreen({super.key});

  @override
  State<ReportCardScreen> createState() => _ReportCardScreenState();
}

class _ReportCardScreenState extends State<ReportCardScreen> {
  bool _isLoading = true;
  double _percentage = 0.0;
  double _totalObtained = 0.0;
  double _totalMax = 0.0;
  List<MarkItemModel> _marks = [];

  @override
  void initState() {
    super.initState();
    _fetchReportCard();
  }

  Future<void> _fetchReportCard() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.get(ApiConstants.reportCard);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _percentage = (data['percentage'] ?? 0.0).toDouble();
          _totalObtained = (data['total_obtained'] ?? 0.0).toDouble();
          _totalMax = (data['total_max'] ?? 0.0).toDouble();
          _marks = (data['marks'] as List? ?? []).map((e) => MarkItemModel.fromJson(e)).toList();
          _isLoading = false;
        });
      }
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Examination & Report Card')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading examination results...')
          : RefreshIndicator(
              onRefresh: _fetchReportCard,
              color: AppColors.primary,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Result Overview Card
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        gradient: AppColors.reportGradient,
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFFF97316).withValues(alpha: 0.25),
                            blurRadius: 16,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Overall Examination Score',
                                style: GoogleFonts.inter(fontSize: 12.5, color: Colors.white.withValues(alpha: 0.9)),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${_percentage.toStringAsFixed(1)}%',
                                style: GoogleFonts.poppins(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '${_totalObtained.toStringAsFixed(0)} / ${_totalMax.toStringAsFixed(0)} Total Marks',
                                style: GoogleFonts.inter(fontSize: 11.5, color: Colors.white70),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.2),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.workspace_premium_rounded, size: 32, color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    const SectionHeader(title: 'Subject Marks & Grades'),
                    const SizedBox(height: 10),

                    if (_marks.isEmpty)
                      const EmptyStateWidget(
                        title: 'No Results Published',
                        message: 'Exam marks have not been published for this academic term yet.',
                        icon: Icons.assessment_rounded,
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _marks.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final m = _marks[index];
                          final ratio = m.maxMarks > 0 ? (m.totalMarks / m.maxMarks).clamp(0.0, 1.0) : 0.0;
                          return Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: AppColors.border),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.02),
                                  blurRadius: 6,
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
                                        m.subjectName,
                                        style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: AppColors.primarySubtle,
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                      child: Text(
                                        m.grade.isNotEmpty ? 'Grade: ${m.grade}' : 'Grade: A',
                                        style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: ratio,
                                    minHeight: 6,
                                    backgroundColor: AppColors.surfaceMuted,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      m.isPass ? AppColors.emerald : AppColors.rose,
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      'Theory: ${m.theoryMarks} | Practical: ${m.practicalMarks}',
                                      style: GoogleFonts.inter(fontSize: 11.5, color: AppColors.textSecondary),
                                    ),
                                    Row(
                                      children: [
                                        Text(
                                          '${m.totalMarks} / ${m.maxMarks}',
                                          style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                        ),
                                        const SizedBox(width: 6),
                                        StatusBadge(
                                          text: m.isPass ? 'PASS' : 'FAIL',
                                          color: m.isPass ? AppColors.emerald : AppColors.rose,
                                          backgroundColor: m.isPass ? AppColors.emeraldSubtle : AppColors.roseSubtle,
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                  ],
                ),
              ),
            ),
    );
  }
}
