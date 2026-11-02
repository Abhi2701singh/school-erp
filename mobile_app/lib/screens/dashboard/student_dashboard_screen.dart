import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/stat_card.dart';
import '../../widgets/common_widgets.dart';
import '../../widgets/app_drawer.dart';
import '../timetable/timetable_screen.dart';
import '../fees/fee_portal_screen.dart';
import '../attendance/attendance_screen.dart';
import '../homework/homework_list_screen.dart';
import '../notices/notice_list_screen.dart';
import '../exams/report_card_screen.dart';
import '../study_material/study_material_screen.dart';
import '../profile/profile_screen.dart';

class StudentDashboardScreen extends StatefulWidget {
  final ValueChanged<int>? onSelectTab;
  const StudentDashboardScreen({super.key, this.onSelectTab});

  @override
  State<StudentDashboardScreen> createState() => _StudentDashboardScreenState();
}

class _StudentDashboardScreenState extends State<StudentDashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<DashboardProvider>(context, listen: false).fetchDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final dashboardProvider = Provider.of<DashboardProvider>(context);
    final student = dashboardProvider.student ?? authProvider.studentProfile;
    final school = authProvider.school;

    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: AppDrawer(activeIndex: 0, onSelectTab: widget.onSelectTab),
      appBar: AppBar(
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu_rounded, color: AppColors.textPrimary, size: 24),
            onPressed: () => Scaffold.of(context).openDrawer(),
            tooltip: 'Navigation Menu',
          ),
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.school_rounded, color: AppColors.primary, size: 20),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    school?.name ?? 'EduManage ERP',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    'Campus Portal',
                    style: GoogleFonts.inter(fontSize: 10.5, color: AppColors.textSecondary, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_none_rounded, size: 23),
                tooltip: 'Announcements',
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const NoticeListScreen()));
                },
              ),
              if (dashboardProvider.notices.isNotEmpty)
                Positioned(
                  top: 10,
                  right: 10,
                  child: Container(
                    padding: const EdgeInsets.all(3),
                    decoration: const BoxDecoration(
                      color: AppColors.rose,
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(minWidth: 8, minHeight: 8),
                  ),
                ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: InkWell(
              onTap: () {
                if (widget.onSelectTab != null) {
                  widget.onSelectTab!(4);
                } else {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen()));
                }
              },
              borderRadius: BorderRadius.circular(20),
              child: CircleAvatar(
                radius: 16,
                backgroundColor: AppColors.primary.withValues(alpha: 0.12),
                child: Text(
                  (student?.fullName.isNotEmpty ?? false)
                      ? student!.fullName.substring(0, 1).toUpperCase()
                      : 'S',
                  style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.primary),
                ),
              ),
            ),
          ),
        ],
      ),
      body: dashboardProvider.isLoading
          ? const LoadingIndicator(message: 'Loading campus dashboard...')
          : RefreshIndicator(
              onRefresh: () => dashboardProvider.fetchDashboardData(),
              color: AppColors.primary,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Student Profile Hero Banner
                    _buildStudentProfileCard(student),
                    const SizedBox(height: 18),

                    // Quick Shortcuts Grid
                    const SectionHeader(title: 'Quick Actions'),
                    const SizedBox(height: 10),
                    _buildQuickShortcutsGrid(context),
                    const SizedBox(height: 20),

                    // Overview Stat Cards
                    const SectionHeader(title: 'Key Academic Stats'),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: StatCard(
                            title: 'Attendance',
                            value: '${dashboardProvider.attendancePercentage}%',
                            subtitle: '${dashboardProvider.presentDays}/${dashboardProvider.totalDays} Days Present',
                            icon: Icons.how_to_reg_rounded,
                            gradient: AppColors.attendanceGradient,
                            onTap: () {
                              Navigator.push(context, MaterialPageRoute(builder: (_) => const AttendanceScreen()));
                            },
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: StatCard(
                            title: 'Fee Dues',
                            value: '₹${dashboardProvider.feeSummary?.totalDue.toStringAsFixed(0) ?? "0"}',
                            subtitle: dashboardProvider.pendingFeeCount > 0
                                ? '${dashboardProvider.pendingFeeCount} Due Invoices'
                                : 'All Cleared',
                            icon: Icons.account_balance_wallet_rounded,
                            gradient: AppColors.feeGradient,
                            onTap: () {
                              if (widget.onSelectTab != null) {
                                widget.onSelectTab!(2);
                              } else {
                                Navigator.push(context, MaterialPageRoute(builder: (_) => const FeePortalScreen()));
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: StatCard(
                            title: 'Homework',
                            value: '${dashboardProvider.homeworks.length}',
                            subtitle: 'Active Tasks',
                            icon: Icons.assignment_turned_in_rounded,
                            gradient: AppColors.homeworkGradient,
                            onTap: () {
                              if (widget.onSelectTab != null) {
                                widget.onSelectTab!(3);
                              } else {
                                Navigator.push(context, MaterialPageRoute(builder: (_) => const HomeworkListScreen()));
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: StatCard(
                            title: 'Notices',
                            value: '${dashboardProvider.notices.length}',
                            subtitle: 'Recent Updates',
                            icon: Icons.campaign_rounded,
                            gradient: AppColors.noticeGradient,
                            onTap: () {
                              Navigator.push(context, MaterialPageRoute(builder: (_) => const NoticeListScreen()));
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 22),

                    // Today's Routine Schedule Preview
                    SectionHeader(
                      title: "Today's Schedule (${dashboardProvider.todayDay})",
                      actionText: 'Full Routine',
                      onActionTap: () {
                        if (widget.onSelectTab != null) {
                          widget.onSelectTab!(1);
                        } else {
                          Navigator.push(context, MaterialPageRoute(builder: (_) => const TimetableScreen()));
                        }
                      },
                    ),
                    const SizedBox(height: 10),
                    if (dashboardProvider.todaySchedule.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: AppColors.surfaceMuted,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Icon(Icons.event_available_rounded, color: AppColors.textMuted, size: 24),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'No Scheduled Classes Today',
                                    style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    'Relax or check the full weekly timetable routine.',
                                    style: GoogleFonts.inter(fontSize: 11.5, color: AppColors.textSecondary),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: dashboardProvider.todaySchedule.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, index) {
                          final item = dashboardProvider.todaySchedule[index];
                          return Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: AppColors.border),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.02),
                                  blurRadius: 6,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 44,
                                  height: 44,
                                  decoration: BoxDecoration(
                                    color: AppColors.primarySubtle,
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
                                  ),
                                  child: Center(
                                    child: Text(
                                      'P${item.periodNumber}',
                                      style: GoogleFonts.poppins(
                                        fontSize: 13,
                                        fontWeight: FontWeight.bold,
                                        color: AppColors.primary,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item.subjectName.toUpperCase(),
                                        style: GoogleFonts.poppins(
                                          fontSize: 13,
                                          fontWeight: FontWeight.bold,
                                          color: AppColors.textPrimary,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 2),
                                      Row(
                                        children: [
                                          const Icon(Icons.person_outline_rounded, size: 13, color: AppColors.textMuted),
                                          const SizedBox(width: 4),
                                          Expanded(
                                            child: Text(
                                              item.teacherName,
                                              style: GoogleFonts.inter(
                                                fontSize: 11.5,
                                                fontWeight: FontWeight.w500,
                                                color: AppColors.textSecondary,
                                              ),
                                              maxLines: 1,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: AppColors.surfaceMuted,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    '${item.startTime}\n${item.endTime}',
                                    style: GoogleFonts.inter(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w600,
                                      color: AppColors.textPrimary,
                                      height: 1.2,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),

                    const SizedBox(height: 22),

                    // Recent School Notices
                    SectionHeader(
                      title: 'School Announcements',
                      actionText: 'View All',
                      onActionTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NoticeListScreen())),
                    ),
                    const SizedBox(height: 10),
                    if (dashboardProvider.notices.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: Center(
                          child: Text(
                            'No announcements published yet.',
                            style: GoogleFonts.inter(fontSize: 12.5, color: AppColors.textSecondary),
                          ),
                        ),
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: dashboardProvider.notices.length > 3 ? 3 : dashboardProvider.notices.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, index) {
                          final notice = dashboardProvider.notices[index];
                          return InkWell(
                            onTap: () {
                              Navigator.push(context, MaterialPageRoute(builder: (_) => const NoticeListScreen()));
                            },
                            borderRadius: BorderRadius.circular(14),
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(color: AppColors.border),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          notice.title,
                                          style: GoogleFonts.poppins(
                                            fontSize: 13,
                                            fontWeight: FontWeight.bold,
                                            color: AppColors.textPrimary,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      StatusBadge(
                                        text: notice.targetRoleDisplay,
                                        color: AppColors.primary,
                                        backgroundColor: AppColors.primarySubtle,
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    notice.content,
                                    style: GoogleFonts.inter(
                                      fontSize: 11.5,
                                      color: AppColors.textSecondary,
                                      height: 1.35,
                                    ),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildStudentProfileCard(student) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppColors.heroGradient,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1E3A5F).withValues(alpha: 0.25),
            blurRadius: 16,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Stack(
                children: [
                  CircleAvatar(
                    radius: 26,
                    backgroundColor: Colors.white.withValues(alpha: 0.2),
                    child: Text(
                      (student?.fullName.isNotEmpty ?? false)
                          ? student!.fullName.substring(0, 1).toUpperCase()
                          : 'S',
                      style: GoogleFonts.poppins(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: AppColors.emerald,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      student?.fullName ?? 'Student Account',
                      style: GoogleFonts.poppins(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Adm No: ${student?.admissionNo ?? "--"}',
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        color: Colors.white.withValues(alpha: 0.75),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildCardInfoPill('CLASS', '${student?.className ?? "--"} (${student?.sectionName ?? "--"})'),
                Container(height: 20, width: 1, color: Colors.white.withValues(alpha: 0.2)),
                _buildCardInfoPill('ROLL NO', '${student?.rollNo ?? "--"}'),
                Container(height: 20, width: 1, color: Colors.white.withValues(alpha: 0.2)),
                _buildCardInfoPill('SESSION', student?.sessionName ?? '2026-27'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCardInfoPill(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 9,
            fontWeight: FontWeight.w600,
            color: Colors.white.withValues(alpha: 0.7),
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 1),
        Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 11.5,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickShortcutsGrid(BuildContext context) {
    final shortcuts = [
      {
        'icon': Icons.calendar_today_rounded,
        'label': 'Routine',
        'color': AppColors.primary,
        'bgColor': AppColors.primarySubtle,
        'onTap': () {
          if (widget.onSelectTab != null) {
            widget.onSelectTab!(1);
          } else {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const TimetableScreen()));
          }
        },
      },
      {
        'icon': Icons.how_to_reg_rounded,
        'label': 'Attendance',
        'color': AppColors.emerald,
        'bgColor': AppColors.emeraldSubtle,
        'onTap': () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AttendanceScreen())),
      },
      {
        'icon': Icons.account_balance_wallet_rounded,
        'label': 'Fees',
        'color': AppColors.violet,
        'bgColor': AppColors.violetSubtle,
        'onTap': () {
          if (widget.onSelectTab != null) {
            widget.onSelectTab!(2);
          } else {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const FeePortalScreen()));
          }
        },
      },
      {
        'icon': Icons.assignment_rounded,
        'label': 'Homework',
        'color': AppColors.accent,
        'bgColor': AppColors.accentSubtle,
        'onTap': () {
          if (widget.onSelectTab != null) {
            widget.onSelectTab!(3);
          } else {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const HomeworkListScreen()));
          }
        },
      },
      {
        'icon': Icons.auto_stories_rounded,
        'label': 'Notes',
        'color': AppColors.cyan,
        'bgColor': AppColors.cyanSubtle,
        'onTap': () => Navigator.push(context, MaterialPageRoute(builder: (_) => const StudyMaterialScreen())),
      },
      {
        'icon': Icons.military_tech_rounded,
        'label': 'Report Card',
        'color': const Color(0xFFF97316),
        'bgColor': const Color(0xFFFFF7ED),
        'onTap': () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportCardScreen())),
      },
      {
        'icon': Icons.campaign_rounded,
        'label': 'Notices',
        'color': const Color(0xFF0284C7),
        'bgColor': const Color(0xFFF0F9FF),
        'onTap': () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NoticeListScreen())),
      },
      {
        'icon': Icons.account_circle_rounded,
        'label': 'Profile',
        'color': AppColors.secondaryLight,
        'bgColor': AppColors.surfaceMuted,
        'onTap': () {
          if (widget.onSelectTab != null) {
            widget.onSelectTab!(4);
          } else {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen()));
          }
        },
      },
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: shortcuts.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 0.88,
      ),
      itemBuilder: (context, index) {
        final item = shortcuts[index];
        return InkWell(
          onTap: item['onTap'] as VoidCallback,
          borderRadius: BorderRadius.circular(14),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(9),
                  decoration: BoxDecoration(
                    color: item['bgColor'] as Color,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(item['icon'] as IconData, color: item['color'] as Color, size: 20),
                ),
                const SizedBox(height: 5),
                Text(
                  item['label'] as String,
                  style: GoogleFonts.inter(
                    fontSize: 10.5,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
