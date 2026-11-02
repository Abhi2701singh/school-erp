import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../core/constants/app_colors.dart';
import '../providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../screens/main_navigation_screen.dart';
import '../screens/timetable/timetable_screen.dart';
import '../screens/attendance/attendance_screen.dart';
import '../screens/fees/fee_portal_screen.dart';
import '../screens/homework/homework_list_screen.dart';
import '../screens/exams/report_card_screen.dart';
import '../screens/study_material/study_material_screen.dart';
import '../screens/notices/notice_list_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/auth/login_screen.dart';

class AppDrawer extends StatelessWidget {
  final int activeIndex;

  const AppDrawer({super.key, this.activeIndex = -1});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final dashboardProvider = Provider.of<DashboardProvider>(context, listen: false);
    final student = dashboardProvider.student ?? authProvider.studentProfile;
    final user = authProvider.user;
    final school = authProvider.school;

    return Drawer(
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.horizontal(right: Radius.circular(20)),
      ),
      child: SafeArea(
        top: false,
        child: Column(
          children: [
            // Header with modern school & student info
            Container(
              width: double.infinity,
              padding: EdgeInsets.fromLTRB(20, MediaQuery.of(context).padding.top + 20, 20, 20),
              decoration: const BoxDecoration(
                gradient: AppColors.heroGradient,
                borderRadius: BorderRadius.only(bottomRight: Radius.circular(24)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
                        ),
                        child: const Icon(Icons.school_rounded, color: Colors.white, size: 24),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              school?.name ?? 'EduManage ERP',
                              style: GoogleFonts.poppins(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              'Code: ${school?.code ?? "CAMPUS"}',
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
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
                    ),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 20,
                          backgroundColor: Colors.white.withValues(alpha: 0.2),
                          child: Text(
                            (student?.fullName.isNotEmpty ?? false)
                                ? student!.fullName.substring(0, 1).toUpperCase()
                                : 'S',
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                student?.fullName ?? user?.fullName ?? 'Student Account',
                                style: GoogleFonts.poppins(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 2),
                              Wrap(
                                spacing: 6,
                                runSpacing: 4,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: AppColors.accent,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      '${student?.className ?? "--"}-${student?.sectionName ?? "--"}',
                                      style: GoogleFonts.inter(
                                        fontSize: 9,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.black87,
                                      ),
                                    ),
                                  ),
                                  Text(
                                    'Roll: ${student?.rollNo ?? "--"}',
                                    style: GoogleFonts.inter(
                                      fontSize: 10,
                                      color: Colors.white.withValues(alpha: 0.85),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Scrollable Menu Items
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                children: [
                  _buildSectionHeader('ACADEMIC PORTAL'),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.space_dashboard_rounded,
                    title: 'Dashboard Overview',
                    isSelected: activeIndex == 0,
                    onTap: () {
                      Navigator.pop(context);
                      if (activeIndex != 0) {
                        Navigator.pushAndRemoveUntil(
                          context,
                          MaterialPageRoute(builder: (_) => const MainNavigationScreen(initialIndex: 0)),
                          (route) => false,
                        );
                      }
                    },
                  ),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.calendar_today_rounded,
                    title: 'Routine Timetable',
                    isSelected: activeIndex == 1,
                    onTap: () {
                      Navigator.pop(context);
                      if (activeIndex == 1) return;
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const TimetableScreen()));
                    },
                  ),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.how_to_reg_rounded,
                    title: 'Daily Attendance',
                    isSelected: activeIndex == 5,
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const AttendanceScreen()));
                    },
                  ),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.assignment_rounded,
                    title: 'Homework & Tasks',
                    isSelected: activeIndex == 3,
                    badge: dashboardProvider.homeworks.isNotEmpty ? '${dashboardProvider.homeworks.length}' : null,
                    badgeColor: AppColors.accent,
                    onTap: () {
                      Navigator.pop(context);
                      if (activeIndex == 3) return;
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const HomeworkListScreen()));
                    },
                  ),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.auto_stories_rounded,
                    title: 'Study Materials',
                    isSelected: activeIndex == 6,
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const StudyMaterialScreen()));
                    },
                  ),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.military_tech_rounded,
                    title: 'Exams & Report Card',
                    isSelected: activeIndex == 7,
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportCardScreen()));
                    },
                  ),

                  const SizedBox(height: 12),
                  _buildSectionHeader('FINANCE & NOTICES'),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.account_balance_wallet_rounded,
                    title: 'Fee Dues & Slips',
                    isSelected: activeIndex == 2,
                    badge: dashboardProvider.pendingFeeCount > 0 ? '${dashboardProvider.pendingFeeCount}' : null,
                    badgeColor: AppColors.rose,
                    onTap: () {
                      Navigator.pop(context);
                      if (activeIndex == 2) return;
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const FeePortalScreen()));
                    },
                  ),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.campaign_rounded,
                    title: 'Announcements',
                    isSelected: activeIndex == 8,
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const NoticeListScreen()));
                    },
                  ),

                  const SizedBox(height: 12),
                  _buildSectionHeader('PROFILE & ACCOUNT'),
                  _buildDrawerTile(
                    context: context,
                    icon: Icons.account_circle_rounded,
                    title: 'Student Profile',
                    isSelected: activeIndex == 4,
                    onTap: () {
                      Navigator.pop(context);
                      if (activeIndex == 4) return;
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen()));
                    },
                  ),
                ],
              ),
            ),

            // Sign out button & app info
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: AppColors.border, width: 1)),
              ),
              child: Column(
                children: [
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    dense: true,
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.roseSubtle,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.logout_rounded, color: AppColors.rose, size: 20),
                    ),
                    title: Text(
                      'Sign Out',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: AppColors.rose,
                      ),
                    ),
                    onTap: () async {
                      Navigator.pop(context);
                      final confirm = await showDialog<bool>(
                        context: context,
                        builder: (ctx) => AlertDialog(
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          title: const Text('Confirm Sign Out'),
                          content: const Text('Are you sure you want to log out of your school account?'),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                            ElevatedButton(
                              onPressed: () => Navigator.pop(ctx, true),
                              style: ElevatedButton.styleFrom(backgroundColor: AppColors.rose),
                              child: const Text('Sign Out'),
                            ),
                          ],
                        ),
                      );

                      if (confirm == true && context.mounted) {
                        await authProvider.logout();
                        if (context.mounted) {
                          Navigator.of(context).pushAndRemoveUntil(
                            MaterialPageRoute(builder: (_) => const LoginScreen()),
                            (route) => false,
                          );
                        }
                      }
                    },
                  ),
                  Text(
                    'EduManage ERP Mobile • v1.0.0',
                    style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 12, top: 8, bottom: 6),
      child: Text(
        title,
        style: GoogleFonts.poppins(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: AppColors.textMuted,
          letterSpacing: 1.1,
        ),
      ),
    );
  }

  Widget _buildDrawerTile({
    required BuildContext context,
    required IconData icon,
    required String title,
    required VoidCallback onTap,
    bool isSelected = false,
    String? badge,
    Color badgeColor = AppColors.primary,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 2),
      decoration: BoxDecoration(
        color: isSelected ? AppColors.primarySubtle : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        onTap: onTap,
        dense: true,
        visualDensity: const VisualDensity(horizontal: 0, vertical: -1),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        leading: Icon(
          icon,
          size: 20,
          color: isSelected ? AppColors.primary : AppColors.textSecondary,
        ),
        title: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 13,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            color: isSelected ? AppColors.primary : AppColors.textPrimary,
          ),
        ),
        trailing: badge != null
            ? Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: badgeColor,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  badge,
                  style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              )
            : const Icon(Icons.chevron_right_rounded, size: 16, color: AppColors.textMuted),
      ),
    );
  }
}
