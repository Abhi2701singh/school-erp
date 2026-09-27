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
      appBar: AppBar(title: const Text('Homework & Assignments')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading homework tasks...')
          : RefreshIndicator(
              onRefresh: _fetchHomework,
              child: _homeworks.isEmpty
                  ? EmptyStateWidget(
                      title: 'No Homework Assigned',
                      message: 'You are all caught up! No active tasks for your class.',
                      icon: Icons.task_alt_rounded,
                      onRefresh: _fetchHomework,
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _homeworks.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final hw = _homeworks[index];
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
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: AppColors.primary.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      hw.subjectName.toUpperCase(),
                                      style: GoogleFonts.inter(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: AppColors.primary,
                                      ),
                                    ),
                                  ),
                                  Row(
                                    children: [
                                      const Icon(Icons.alarm_rounded, size: 14, color: AppColors.rose),
                                      const SizedBox(width: 4),
                                      Text(
                                        'Due: ${hw.dueDate}',
                                        style: GoogleFonts.inter(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                          color: AppColors.rose,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 10),
                              Text(
                                hw.title,
                                style: GoogleFonts.poppins(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                hw.description,
                                style: GoogleFonts.inter(
                                  fontSize: 13,
                                  color: AppColors.textSecondary,
                                  height: 1.4,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    'By ${hw.createdByName}',
                                    style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted),
                                  ),
                                  if (hw.attachment != null && hw.attachment!.isNotEmpty)
                                    TextButton.icon(
                                      onPressed: () async {
                                        final uri = Uri.parse(hw.attachment!);
                                        if (await canLaunchUrl(uri)) {
                                          await launchUrl(uri, mode: LaunchMode.externalApplication);
                                        }
                                      },
                                      icon: const Icon(Icons.attach_file_rounded, size: 16),
                                      label: const Text('Download File'),
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
