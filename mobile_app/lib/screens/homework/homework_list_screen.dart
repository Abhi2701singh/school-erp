import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../models/common_models.dart';
import '../../widgets/common_widgets.dart';

class HomeworkListScreen extends StatefulWidget {
  const HomeworkListScreen({super.key});

  @override
  State<HomeworkListScreen> createState() => _HomeworkListScreenState();
}

class _HomeworkListScreenState extends State<HomeworkListScreen> {
  bool _isLoading = true;
  List<HomeworkModel> _homeworks = [];

  @override
  void initState() {
    super.initState();
    _fetchHomework();
  }

  Future<void> _fetchHomework() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.get(ApiConstants.homework);
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        setState(() {
          _homeworks = data.map((e) => HomeworkModel.fromJson(e)).toList();
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
      appBar: AppBar(title: const Text('Homework & Tasks')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading active homework...')
          : RefreshIndicator(
              onRefresh: _fetchHomework,
              color: AppColors.primary,
              child: _homeworks.isEmpty
                  ? EmptyStateWidget(
                      title: 'All Tasks Completed!',
                      message: 'No pending homework or assignments assigned to your class.',
                      icon: Icons.task_alt_rounded,
                      onRefresh: _fetchHomework,
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                      itemCount: _homeworks.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (context, index) {
                        final hw = _homeworks[index];
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
                                  StatusBadge(
                                    text: hw.subjectName.toUpperCase(),
                                    color: AppColors.primary,
                                    backgroundColor: AppColors.primarySubtle,
                                  ),
                                  Row(
                                    children: [
                                      const Icon(Icons.alarm_rounded, size: 14, color: AppColors.rose),
                                      const SizedBox(width: 4),
                                      Text(
                                        'Due: ${hw.dueDate}',
                                        style: GoogleFonts.inter(
                                          fontSize: 11.5,
                                          fontWeight: FontWeight.bold,
                                          color: AppColors.rose,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                hw.title,
                                style: GoogleFonts.poppins(
                                  fontSize: 14.5,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                hw.description,
                                style: GoogleFonts.inter(
                                  fontSize: 12.5,
                                  color: AppColors.textSecondary,
                                  height: 1.4,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Row(
                                    children: [
                                      const Icon(Icons.person_outline_rounded, size: 14, color: AppColors.textMuted),
                                      const SizedBox(width: 4),
                                      Text(
                                        hw.createdByName,
                                        style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted),
                                      ),
                                    ],
                                  ),
                                  if (hw.attachment != null && hw.attachment!.isNotEmpty)
                                    OutlinedButton.icon(
                                      onPressed: () async {
                                        final uri = Uri.parse(hw.attachment!);
                                        if (await canLaunchUrl(uri)) {
                                          await launchUrl(uri, mode: LaunchMode.externalApplication);
                                        }
                                      },
                                      icon: const Icon(Icons.attach_file_rounded, size: 14),
                                      label: const Text('Download'),
                                      style: OutlinedButton.styleFrom(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                        minimumSize: Size.zero,
                                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                        textStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                ],
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
