import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/app_drawer.dart';
import '../auth/login_screen.dart';

class ProfileScreen extends StatelessWidget {
  final ValueChanged<int>? onSelectTab;
  const ProfileScreen({super.key, this.onSelectTab});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final dashboardProvider = Provider.of<DashboardProvider>(context, listen: false);
    final user = authProvider.user;
    final student = dashboardProvider.student ?? authProvider.studentProfile;
    final school = authProvider.school;

    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: AppDrawer(activeIndex: 4, onSelectTab: onSelectTab),
      appBar: AppBar(
        leading: (ModalRoute.of(context)?.canPop ?? false)
            ? IconButton(
                icon: const Icon(Icons.arrow_back_rounded),
                onPressed: () => Navigator.pop(context),
              )
            : Builder(
                builder: (ctx) => IconButton(
                  icon: const Icon(Icons.menu_rounded),
                  tooltip: 'Navigation Menu',
                  onPressed: () => Scaffold.of(ctx).openDrawer(),
                ),
              ),
        title: const Text('My Profile & Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Column(
          children: [
            // Modern Digital Student ID Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: AppColors.heroGradient,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF1E3A5F).withValues(alpha: 0.25),
                    blurRadius: 16,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.school_rounded, color: Colors.white, size: 18),
                          const SizedBox(width: 6),
                          Text(
                            school?.name ?? 'EduManage ERP',
                            style: GoogleFonts.poppins(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.accent,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          'STUDENT ID',
                          style: GoogleFonts.inter(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.black87),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: Colors.white.withValues(alpha: 0.2),
                        child: Text(
                          (student?.fullName.isNotEmpty ?? false)
                              ? student!.fullName.substring(0, 1).toUpperCase()
                              : 'S',
                          style: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              student?.fullName ?? user?.fullName ?? 'Student Account',
                              style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              user?.email ?? 'student@school.edu',
                              style: GoogleFonts.inter(fontSize: 11.5, color: Colors.white.withValues(alpha: 0.8)),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Adm No: ${student?.admissionNo ?? "--"}',
                              style: GoogleFonts.inter(fontSize: 11, color: Colors.white70),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _buildIdInfo('CLASS & SEC', '${student?.className ?? "--"}-${student?.sectionName ?? "--"}'),
                        Container(height: 18, width: 1, color: Colors.white24),
                        _buildIdInfo('ROLL NO', student?.rollNo ?? '--'),
                        Container(height: 18, width: 1, color: Colors.white24),
                        _buildIdInfo('SESSION', student?.sessionName ?? '2026-27'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Academic & Personal Details Card
            if (student != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Student Details',
                      style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                    const Divider(height: 18),
                    _buildInfoRow('Admission Number', student.admissionNo, Icons.badge_rounded),
                    _buildInfoRow('Roll Number', student.rollNo, Icons.pin_rounded),
                    _buildInfoRow('Class & Section', '${student.className} - ${student.sectionName}', Icons.class_rounded),
                    _buildInfoRow('Academic Session', student.sessionName, Icons.calendar_today_rounded),
                    _buildInfoRow('Father Name', student.fatherName, Icons.family_restroom_rounded),
                    _buildInfoRow('Mother Name', student.motherName, Icons.family_restroom_rounded),
                    _buildInfoRow('Parent Phone', student.parentPhone, Icons.phone_rounded),
                  ],
                ),
              ),
              const SizedBox(height: 14),
            ],

            // School Campus Card
            if (school != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'School Campus',
                      style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                    const Divider(height: 18),
                    _buildInfoRow('School Name', school.name, Icons.domain_rounded),
                    _buildInfoRow('School Code', school.code, Icons.tag_rounded),
                    _buildInfoRow('Principal', school.principalName, Icons.person_rounded),
                    _buildInfoRow('Contact Phone', school.phone, Icons.call_rounded),
                    _buildInfoRow('Campus Email', school.email, Icons.email_rounded),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Logout Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () async {
                  final confirm = await showDialog<bool>(
                    context: context,
                    builder: (ctx) => AlertDialog(
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      title: const Text('Confirm Sign Out'),
                      content: const Text('Are you sure you want to log out of your EduManage account?'),
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
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: AppColors.rose),
                  foregroundColor: AppColors.rose,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                icon: const Icon(Icons.logout_rounded, size: 18),
                label: Text('Sign Out', style: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 13.5)),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'EduManage ERP Mobile • v1.0.0 (Build 2026)',
              style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildIdInfo(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(fontSize: 9, fontWeight: FontWeight.w600, color: Colors.white70),
        ),
        const SizedBox(height: 1),
        Text(
          value,
          style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: AppColors.textMuted),
              const SizedBox(width: 8),
              Text(label, style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
            ],
          ),
          Flexible(
            child: Text(
              value.isNotEmpty ? value : '--',
              style: GoogleFonts.inter(fontSize: 12.5, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }
}
