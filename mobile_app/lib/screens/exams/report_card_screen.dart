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
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Result Overview Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFFF59E0B).withOpacity(0.3),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
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
                                'Overall Performance',
                                style: GoogleFonts.inter(fontSize: 13, color: Colors.white.withOpacity(0.9)),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                '$_percentage%',
                                style: GoogleFonts.poppins(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              Text(
                                '$_totalObtained / $_totalMax Total Marks',
                                style: GoogleFonts.inter(fontSize: 12, color: Colors.white70),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.workspace_premium_rounded, size: 36, color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    Text(
                      'Subject Marks & Grades',
                      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                    const SizedBox(height: 12),

                    if (_marks.isEmpty)
                      const EmptyStateWidget(
                        title: 'No Results Published',
                        message: 'Exam marks have not been published for this session yet.',
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _marks.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final m = _marks[index];
                          return Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      m.subjectName,
                                      style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                    ),
                                    Text(
                                      'Theory: ${m.theoryMarks} | Practical: ${m.practicalMarks}',
                                      style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                                    ),
                                  ],
                                ),
                                Row(
                                  children: [
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.end,
                                      children: [
                                        Text(
                                          '${m.totalMarks} / ${m.maxMarks}',
                                          style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                        ),
                                        Text(
                                          m.isPass ? 'PASS' : 'FAIL',
                                          style: GoogleFonts.inter(
                                            fontSize: 10,
                                            fontWeight: FontWeight.bold,
                                            color: m.isPass ? AppColors.emerald : AppColors.rose,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(width: 12),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                      decoration: BoxDecoration(
                                        color: AppColors.primary.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(
                                        m.grade.isNotEmpty ? m.grade : 'A',
                                        style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.primary),
                                      ),
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
