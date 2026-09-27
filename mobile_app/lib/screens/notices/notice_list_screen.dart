import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../models/common_models.dart';
import '../../widgets/common_widgets.dart';

class NoticeListScreen extends StatefulWidget {
  const NoticeListScreen({super.key});

  @override
  State<NoticeListScreen> createState() => _NoticeListScreenState();
}

class _NoticeListScreenState extends State<NoticeListScreen> {
  bool _isLoading = true;
  List<NoticeModel> _notices = [];

  @override
  void initState() {
    super.initState();
    _fetchNotices();
  }

  Future<void> _fetchNotices() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.get(ApiConstants.notices);
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        setState(() {
          _notices = data.map((e) => NoticeModel.fromJson(e)).toList();
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
      appBar: AppBar(title: const Text('School Announcements')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading announcements...')
          : RefreshIndicator(
              onRefresh: _fetchNotices,
              child: _notices.isEmpty
                  ? EmptyStateWidget(
                      title: 'No Announcements',
                      message: 'No new notices published by the school administration.',
                      icon: Icons.campaign_rounded,
                      onRefresh: _fetchNotices,
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _notices.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final n = _notices[index];
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
                                      n.targetRoleDisplay,
                                      style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary),
                                    ),
                                  ),
                                  Text(
                                    n.createdAt.split('T').first,
                                    style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 10),
                              Text(
                                n.title,
                                style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                n.content,
                                style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary, height: 1.4),
                              ),
                              if (n.attachment != null && n.attachment!.isNotEmpty) ...[
                                const SizedBox(height: 10),
                                TextButton.icon(
                                  onPressed: () async {
                                    final uri = Uri.parse(n.attachment!);
                                    if (await canLaunchUrl(uri)) {
                                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                                    }
                                  },
                                  icon: const Icon(Icons.attachment_rounded, size: 16),
                                  label: const Text('View Attachment'),
                                ),
                              ],
                            ],
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
