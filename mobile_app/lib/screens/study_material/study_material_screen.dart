import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../widgets/common_widgets.dart';


class StudyMaterialScreen extends StatefulWidget {
  const StudyMaterialScreen({super.key});

  @override
  State<StudyMaterialScreen> createState() => _StudyMaterialScreenState();
}

class _StudyMaterialScreenState extends State<StudyMaterialScreen> {
  bool _isLoading = true;
  List<Map<String, dynamic>> _materials = [];

  @override
  void initState() {
    super.initState();
    _fetchMaterials();
  }

  Future<void> _fetchMaterials() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.get(ApiConstants.studyMaterials);
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        setState(() {
          _materials = data.cast<Map<String, dynamic>>();
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
      appBar: AppBar(title: const Text('Study Materials & Notes')),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading study notes...')
          : RefreshIndicator(
              onRefresh: _fetchMaterials,
              child: _materials.isEmpty
                  ? EmptyStateWidget(
                      title: 'No Notes Found',
                      message: 'Teachers have not uploaded study notes yet.',
                      icon: Icons.menu_book_rounded,
                      onRefresh: _fetchMaterials,
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _materials.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final m = _materials[index];
                        final fileUrl = m['file'] as String?;
                        return Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: AppColors.rose.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(Icons.picture_as_pdf_rounded, color: AppColors.rose, size: 28),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      m['title'] ?? 'Study Notes',
                                      style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                    ),
                                    Text(
                                      '${m['subject_name'] ?? "Subject"} • ${m['class_name'] ?? ""}',
                                      style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                                    ),
                                  ],
                                ),
                              ),
                              if (fileUrl != null && fileUrl.isNotEmpty)
                                IconButton(
                                  icon: const Icon(Icons.download_rounded, color: AppColors.primary),
                                  onPressed: () async {
                                    final uri = Uri.parse(fileUrl);
                                    if (await canLaunchUrl(uri)) {
                                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                                    }
                                  },
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
