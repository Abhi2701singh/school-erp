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
  String _selectedFilter = 'ALL'; // ALL, P, A, L

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

  List<AttendanceModel> get _filteredHistory {
    if (_selectedFilter == 'ALL') return _history;
    if (_selectedFilter == 'P') return _history.where((e) => e.status == 'P').toList();
    if (_selectedFilter == 'A') return _history.where((e) => e.status == 'A').toList();
    if (_selectedFilter == 'L') return _history.where((e) => e.status == 'L' || e.status == 'LE' || e.status == 'H').toList();
    return _history;
  }

  @override
  Widget build(BuildContext context) {
    final isGoodAttendance = _percentage >= 75.0;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Attendance Register')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading attendance records...')
          : RefreshIndicator(
              onRefresh: _fetchAttendance,
              color: AppColors.primary,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Modern Attendance Circular Progress Banner
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        gradient: AppColors.attendanceGradient,
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF10B981).withValues(alpha: 0.25),
                            blurRadius: 14,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          // Circular Progress Ring
                          SizedBox(
                            width: 80,
                            height: 80,
                            child: Stack(
                              alignment: Alignment.center,
                              children: [
                                SizedBox(
                                  width: 80,
                                  height: 80,
                                  child: CircularProgressIndicator(
                                    value: (_percentage / 100.0).clamp(0.0, 1.0),
                                    strokeWidth: 8,
                                    backgroundColor: Colors.white.withValues(alpha: 0.25),
                                    valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                                    strokeCap: StrokeCap.round,
                                  ),
                                ),
                                Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      '${_percentage.toStringAsFixed(0)}%',
                                      style: GoogleFonts.poppins(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 18),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withValues(alpha: 0.2),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    isGoodAttendance ? 'GOOD STANDING (≥75%)' : 'ATTENDANCE ALERT (<75%)',
                                    style: GoogleFonts.inter(
                                      fontSize: 9.5,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                      letterSpacing: 0.3,
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  'Overall Session Rate',
                                  style: GoogleFonts.poppins(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  '$_presentDays Present out of $_totalDays Days',
                                  style: GoogleFonts.inter(
                                    fontSize: 12,
                                    color: Colors.white.withValues(alpha: 0.85),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),

                    // Quick Stats Metric Cards
                    Row(
                      children: [
                        _buildStatChip('Present', '$_presentDays', AppColors.emerald, AppColors.emeraldSubtle),
                        const SizedBox(width: 8),
                        _buildStatChip('Absent', '$_absentDays', AppColors.rose, AppColors.roseSubtle),
                        const SizedBox(width: 8),
                        _buildStatChip('Leave', '$_leaveDays', AppColors.accent, AppColors.accentSubtle),
                        const SizedBox(width: 8),
                        _buildStatChip('Total', '$_totalDays', AppColors.secondary, AppColors.surfaceMuted),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Filter Chips Bar
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Attendance Logs',
                          style: GoogleFonts.poppins(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        Row(
                          children: [
                            _buildFilterTab('ALL', 'All'),
                            const SizedBox(width: 4),
                            _buildFilterTab('P', 'Present'),
                            const SizedBox(width: 4),
                            _buildFilterTab('A', 'Absent'),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    // Daily Attendance List
                    if (_filteredHistory.isEmpty)
                      const EmptyStateWidget(
                        title: 'No Matching Logs',
                        message: 'No daily attendance entries match this filter.',
                        icon: Icons.event_note_rounded,
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _filteredHistory.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, index) {
                          final item = _filteredHistory[index];
                          return Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: AppColors.border),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.02),
                                  blurRadius: 4,
                                  offset: const Offset(0, 1),
                                ),
                              ],
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: AppColors.surfaceMuted,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: const Icon(Icons.calendar_month_rounded, size: 16, color: AppColors.textSecondary),
                                    ),
                                    const SizedBox(width: 12),
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          item.date,
                                          style: GoogleFonts.inter(
                                            fontSize: 13,
                                            fontWeight: FontWeight.bold,
                                            color: AppColors.textPrimary,
                                          ),
                                        ),
                                        Text(
                                          'Session Class Log',
                                          style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted),
                                        ),
                                      ],
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

  Widget _buildStatChip(String label, String count, Color color, Color bgColor) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          children: [
            Text(
              count,
              style: GoogleFonts.poppins(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: GoogleFonts.inter(
                fontSize: 10.5,
                fontWeight: FontWeight.w500,
                color: AppColors.textSecondary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterTab(String code, String label) {
    final isSelected = _selectedFilter == code;
    return InkWell(
      onTap: () => setState(() => _selectedFilter = code),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primarySubtle : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: isSelected ? AppColors.primary : Colors.transparent),
        ),
        child: Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            color: isSelected ? AppColors.primary : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status, String display) {
    Color color = AppColors.emerald;
    Color bgColor = AppColors.emeraldSubtle;
    IconData icon = Icons.check_circle_rounded;

    if (status == 'A') {
      color = AppColors.rose;
      bgColor = AppColors.roseSubtle;
      icon = Icons.cancel_rounded;
    } else if (status == 'L' || status == 'LE' || status == 'H') {
      color = AppColors.accent;
      bgColor = AppColors.accentSubtle;
      icon = Icons.schedule_rounded;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(8)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 4),
          Text(
            display,
            style: GoogleFonts.inter(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
