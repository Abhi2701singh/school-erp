import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/timetable_provider.dart';
import '../../models/timetable_model.dart';
import '../../widgets/common_widgets.dart';

class TimetableScreen extends StatefulWidget {
  const TimetableScreen({super.key});

  @override
  State<TimetableScreen> createState() => _TimetableScreenState();
}

class _TimetableScreenState extends State<TimetableScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final List<String> _days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  bool _isMatrixView = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _days.length, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<TimetableProvider>(context, listen: false).fetchTimetable();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final timetableProvider = Provider.of<TimetableProvider>(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Class Timetable Routine'),
        actions: [
          IconButton(
            icon: Icon(_isMatrixView ? Icons.view_agenda_outlined : Icons.grid_view_rounded),
            tooltip: _isMatrixView ? 'Switch to Daily View' : 'Switch to Full Matrix Grid',
            onPressed: () {
              setState(() {
                _isMatrixView = !_isMatrixView;
              });
            },
          ),
        ],
      ),
      body: timetableProvider.isLoading
          ? const LoadingIndicator(message: 'Loading weekly routine...')
          : Column(
              children: [
                // Top Classic Routine Header Banner (Matching web theme)
                _buildRoutineBanner(timetableProvider),

                // View Switcher: Matrix Grid vs Day Tab View
                if (_isMatrixView)
                  Expanded(child: _buildMatrixGridView(timetableProvider))
                else ...[
                  // Day Selector Tabs
                  Container(
                    color: Colors.white,
                    child: TabBar(
                      controller: _tabController,
                      isScrollable: true,
                      labelColor: AppColors.primary,
                      unselectedLabelColor: AppColors.textSecondary,
                      indicatorColor: AppColors.primary,
                      indicatorWeight: 3,
                      labelStyle: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.bold),
                      unselectedLabelStyle: GoogleFonts.inter(fontSize: 13),
                      tabs: _days.map((d) => Tab(text: d.toUpperCase())).toList(),
                    ),
                  ),
                  Expanded(
                    child: TabBarView(
                      controller: _tabController,
                      children: _days.map((day) => _buildDayScheduleList(day, timetableProvider)).toList(),
                    ),
                  ),
                ],
              ],
            ),
    );
  }

  Widget _buildRoutineBanner(TimetableProvider provider) {
    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        color: AppColors.ttNavyHeader,
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Text(
              'TIME TABLE',
              style: GoogleFonts.poppins(
                fontSize: 18,
                fontWeight: FontWeight.w900,
                color: const Color(0xFFFFE600),
                letterSpacing: 2.5,
              ),
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 6),
            color: AppColors.ttYellowBanner,
            child: Text(
              'ROUTINE FOR CLASS ${provider.selectedClass.toUpperCase()} - SECTION ${provider.selectedSection.toUpperCase()}',
              style: GoogleFonts.poppins(
                fontSize: 12,
                fontWeight: FontWeight.w900,
                color: const Color(0xFFB71C1C),
                letterSpacing: 1,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDayScheduleList(String dayName, TimetableProvider provider) {
    final dayEntries = provider.allEntries.where((e) => e.day.toLowerCase() == dayName.toLowerCase()).toList()
      ..sort((a, b) => a.periodNumber.compareTo(b.periodNumber));

    if (dayEntries.isEmpty) {
      return EmptyStateWidget(
        title: 'No Classes for $dayName',
        message: 'No periods scheduled for this day in the active routine.',
        icon: Icons.event_busy_rounded,
        onRefresh: () => provider.fetchTimetable(),
      );
    }

    final morningEntries = dayEntries.where((e) => e.periodNumber <= 4).toList();
    final afternoonEntries = dayEntries.where((e) => e.periodNumber >= 5).toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Morning Periods
        if (morningEntries.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(bottom: 8, left: 4),
            child: Text(
              'MORNING SESSION',
              style: GoogleFonts.poppins(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: AppColors.primary,
                letterSpacing: 1,
              ),
            ),
          ),
          ...morningEntries.map((entry) => _buildPeriodCard(entry, provider)),
          const SizedBox(height: 12),
        ],

        // Lunch Break Banner Card
        _buildLunchBreakCard(provider.breakTiming),
        const SizedBox(height: 12),

        // Afternoon Periods
        if (afternoonEntries.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(bottom: 8, left: 4),
            child: Text(
              'AFTERNOON SESSION',
              style: GoogleFonts.poppins(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: AppColors.primary,
                letterSpacing: 1,
              ),
            ),
          ),
          ...afternoonEntries.map((entry) => _buildPeriodCard(entry, provider)),
        ],
      ],
    );
  }

  Widget _buildLunchBreakCard(String breakTime) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFFBEB), Color(0xFFFEF3C7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFFCD34D), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFD97706).withOpacity(0.08),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFFF59E0B),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.restaurant_rounded, color: Colors.white, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'LUNCH / RECESS BREAK',
                  style: GoogleFonts.poppins(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: const Color(0xFF92400E),
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Rest, refreshments & meal time',
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    color: const Color(0xFFB45309),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFF59E0B)),
            ),
            child: Text(
              breakTime,
              style: GoogleFonts.inter(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                color: const Color(0xFFB45309),
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodCard(TimetableEntryModel entry, TimetableProvider provider) {
    final periodTiming = provider.periodTimings[entry.periodNumber.toString()] ??
        '${entry.startTime} - ${entry.endTime}';

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
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
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppColors.ttGreenCell.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.ttGreenCell),
            ),
            child: Center(
              child: Text(
                'P${entry.periodNumber}',
                style: GoogleFonts.poppins(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1E293B),
                ),
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.subjectName.toUpperCase(),
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Teacher: ${entry.teacherName}',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.surfaceMuted,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Text(
              periodTiming.replaceAll(' - ', '\n'),
              style: GoogleFonts.inter(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: const Color(0xFF1E3A5F),
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMatrixGridView(TimetableProvider provider) {
    if (provider.gridRows.isEmpty) {
      return const EmptyStateWidget(
        title: 'Empty Routine Matrix',
        message: 'No routine schedule data available.',
      );
    }

    final p1Time = provider.periodTimings['1'] ?? '09:00 - 09:40';
    final p2Time = provider.periodTimings['2'] ?? '09:40 - 10:20';
    final p3Time = provider.periodTimings['3'] ?? '10:20 - 11:00';
    final p4Time = provider.periodTimings['4'] ?? '11:00 - 11:40';
    final breakTime = provider.breakTiming;
    final p5Time = provider.periodTimings['5'] ?? '12:20 - 01:00';
    final p6Time = provider.periodTimings['6'] ?? '01:00 - 01:40';
    final p7Time = provider.periodTimings['7'] ?? '01:40 - 02:20';
    final p8Time = provider.periodTimings['8'] ?? '02:20 - 03:00';
    final p9Time = provider.periodTimings['9'] ?? '03:00 - 03:40';

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(12),
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: AppColors.ttBorder, width: 2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Table(
            defaultColumnWidth: const FixedColumnWidth(115),
            columnWidths: const {
              0: FixedColumnWidth(95), // Days
              5: FixedColumnWidth(65), // Break
              10: FixedColumnWidth(115), // Extra class
            },
            border: TableBorder.all(color: AppColors.ttBorder, width: 1.2),
            children: [
              // Header Row
              TableRow(
                decoration: const BoxDecoration(color: AppColors.ttGreenCell),
                children: [
                  _buildMatrixHeaderCell('DAYS', 'WEEKLY'),
                  _buildMatrixHeaderCell('1st', p1Time),
                  _buildMatrixHeaderCell('2nd', p2Time),
                  _buildMatrixHeaderCell('3rd', p3Time),
                  _buildMatrixHeaderCell('4th', p4Time),
                  _buildMatrixHeaderCell('BREAK', breakTime),
                  _buildMatrixHeaderCell('5th', p5Time),
                  _buildMatrixHeaderCell('6th', p6Time),
                  _buildMatrixHeaderCell('7th', p7Time),
                  _buildMatrixHeaderCell('8th', p8Time),
                  _buildMatrixHeaderCell('EXTRA', p9Time),
                ],
              ),
              // Data Rows
              ...provider.gridRows.map((row) {
                return TableRow(
                  children: [
                    // Day column
                    Container(
                      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 4),
                      color: AppColors.ttGreenCell,
                      child: Center(
                        child: Text(
                          row.dayDisplay,
                          style: GoogleFonts.inter(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                    // Morning cells (1 to 4)
                    ...row.morning.take(4).map((cell) => _buildMatrixDataCell(cell.item)),
                    // Break column
                    Container(
                      color: AppColors.ttGreenCell,
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 2),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFE600),
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(color: const Color(0xFFB71C1C)),
                            ),
                            child: Text(
                              'LUNCH',
                              style: GoogleFonts.inter(
                                fontSize: 8,
                                fontWeight: FontWeight.w900,
                                color: const Color(0xFFB71C1C),
                              ),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'B\nR\nE\nA\nK',
                            style: GoogleFonts.inter(
                              fontSize: 10,
                              fontWeight: FontWeight.w900,
                              color: Colors.black87,
                              height: 1.2,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            breakTime.replaceAll(' - ', '\n'),
                            style: GoogleFonts.inter(
                              fontSize: 8,
                              fontWeight: FontWeight.w700,
                              color: const Color(0xFF1E3A5F),
                              height: 1.1,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                    // Afternoon cells (5 to 8 + Extra)
                    ...row.afternoon.take(5).map((cell) => _buildMatrixDataCell(cell.item)),
                  ],
                );
              }),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMatrixHeaderCell(String title, String timeSlot) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            title,
            style: GoogleFonts.inter(
              fontSize: 11,
              fontWeight: FontWeight.w900,
              color: Colors.black87,
            ),
            textAlign: TextAlign.center,
          ),
          if (timeSlot.isNotEmpty) ...[
            const SizedBox(height: 3),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.8),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: Colors.black12),
              ),
              child: Text(
                timeSlot,
                style: GoogleFonts.inter(
                  fontSize: 8,
                  fontWeight: FontWeight.w700,
                  color: const Color(0xFF1E3A5F),
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMatrixDataCell(TimetableEntryModel? item) {
    if (item == null) {
      return Container(
        color: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: const Center(
          child: Text('-', style: TextStyle(color: Colors.black26)),
        ),
      );
    }

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            item.subjectName.toUpperCase(),
            style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            '(${item.teacherName})',
            style: GoogleFonts.inter(fontSize: 9, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

