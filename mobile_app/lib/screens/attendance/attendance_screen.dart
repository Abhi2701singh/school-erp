import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../models/common_models.dart';
import '../../widgets/common_widgets.dart';

class AttendanceScreen extends StatefulWidget {
  const AttendanceScreen({super.key});

  @override
  State<AttendanceScreen> createState() => _AttendanceScreenState();
}

class _AttendanceScreenState extends State<AttendanceScreen> {
  bool _isLoading = true;
  double _percentage = 100.0;
  int _totalDays = 0;
  int _presentDays = 0;
  int _absentDays = 0;
  int _leaveDays = 0;
  List<AttendanceModel> _history = [];

  @override
  void initState() {
    super.initState();
    _fetchAttendance();
  }

  Future<void> _fetchAttendance() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.get(ApiConstants.attendance);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _percentage = (data['percentage'] ?? 100.0).toDouble();
          _totalDays = data['total_days'] ?? 0;
          _presentDays = data['present_days'] ?? 0;
          _absentDays = data['absent_days'] ?? 0;
          _leaveDays = data['leave_days'] ?? 0;
          _history = (data['history'] as List? ?? []).map((e) => AttendanceModel.fromJson(e)).toList();
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
      appBar: AppBar(title: const Text('Attendance Register')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading attendance logs...')
          : RefreshIndicator(
              onRefresh: _fetchAttendance,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Attendance Percentage Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: AppColors.attendanceGradient,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF10B981).withOpacity(0.3),
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
                                'Overall Attendance',
                                style: GoogleFonts.inter(fontSize: 13, color: Colors.white.withOpacity(0.9)),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                '$_percentage%',
                                style: GoogleFonts.poppins(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              Text(
                                '$_presentDays Present out of $_totalDays Days',
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
                            child: const Icon(Icons.how_to_reg_rounded, size: 36, color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Stat Breakdown Chips
                    Row(
                      children: [
                        _buildAttendanceChip('Present', '$_presentDays', AppColors.emerald),
                        const SizedBox(width: 8),
                        _buildAttendanceChip('Absent', '$_absentDays', AppColors.rose),
                        const SizedBox(width: 8),
                        _buildAttendanceChip('Leave / Half', '$_leaveDays', AppColors.accent),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Attendance History List
                    Text(
                      'Daily Attendance History',
                      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                    const SizedBox(height: 12),

                    if (_history.isEmpty)
                      const EmptyStateWidget(
                        title: 'No Records',
                        message: 'No daily attendance marked for this session.',
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _history.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, index) {
                          final item = _history[index];
                          return Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    const Icon(Icons.calendar_today_rounded, size: 16, color: AppColors.textMuted),
                                    const SizedBox(width: 10),
                                    Text(
                                      item.date,
                                      style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                                    ),
                                  ],
                                ),
                                _buildStatusBadge(item.status, item.statusDisplay),
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

  Widget _buildAttendanceChip(String label, String count, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Column(
          children: [
            Text(count, style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
            Text(label, style: GoogleFonts.inter(fontSize: 11, color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status, String display) {
    Color color = AppColors.emerald;
    if (status == 'A') color = AppColors.rose;
    if (status == 'L' || status == 'LE' || status == 'H') color = AppColors.accent;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
      child: Text(display, style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: color)),
    );
  }
}
