import 'package:flutter/material.dart';

class AppColors {
  // Primary Palette
  static const Color primary = Color(0xFF2563EB); // Modern Royal Blue
  static const Color primaryDark = Color(0xFF1E40AF);
  static const Color primaryLight = Color(0xFF60A5FA);

  // Accent & Secondary
  static const Color secondary = Color(0xFF0F172A); // Deep Slate
  static const Color accent = Color(0xFFF59E0B); // Vibrant Amber
  static const Color emerald = Color(0xFF10B981); // Success Green
  static const Color rose = Color(0xFFEF4444); // Error / Overdue Red
  static const Color indigo = Color(0xFF6366F1); // Indigo Purple
  static const Color cyan = Color(0xFF06B6D4); // Cyan Blue

  // Background & Surfaces
  static const Color background = Color(0xFFF8FAFC); // Clean Light Slate
  static const Color cardBackground = Color(0xFFFFFFFF);
  static const Color surfaceMuted = Color(0xFFF1F5F9);

  // Routine Timetable Colors (Matching Web Theme)
  static const Color ttNavyHeader = Color(0xFF1E3A5F);
  static const Color ttYellowBanner = Color(0xFFFFE600);
  static const Color ttGreenCell = Color(0xFF8CC63F);
  static const Color ttBorder = Color(0xFF334155);

  // Text Colors
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textMuted = Color(0xFF94A3B8);
  static const Color textWhite = Color(0xFFFFFFFF);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient feeGradient = LinearGradient(
    colors: [Color(0xFF8B5CF6), Color(0xFF6D28D9)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient attendanceGradient = LinearGradient(
    colors: [Color(0xFF10B981), Color(0xFF059669)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient homeworkGradient = LinearGradient(
    colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
