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

  String _getOrdinal(int n) {
    if (n >= 11 && n <= 13) return '${n}th';
    switch (n % 10) {
      case 1:
        return '${n}st';
      case 2:
        return '${n}nd';
      case 3:
        return '${n}rd';
      default:
        return '${n}th';
    }
  }

  Widget _buildMatrixGridView(TimetableProvider provider) {
    if (provider.gridRows.isEmpty) {
      return const EmptyStateWidget(
        title: 'Empty Routine Matrix',
        message: 'No routine schedule data available.',
      );
    }

    final firstRow = provider.gridRows.first;
    final morningCells = firstRow.morning;
    final afternoonCells = firstRow.afternoon;
    final hasBreak = provider.breakTiming.isNotEmpty && afternoonCells.isNotEmpty;

    final columnWidths = <int, TableColumnWidth>{
      0: const FixedColumnWidth(95), // Days
    };
    int colIdx = 1;
    for (int i = 0; i < morningCells.length; i++) {
      columnWidths[colIdx++] = const FixedColumnWidth(115);
    }
    if (hasBreak) {
      columnWidths[colIdx++] = const FixedColumnWidth(65); // Break
    }
    for (int i = 0; i < afternoonCells.length; i++) {
      columnWidths[colIdx++] = const FixedColumnWidth(115);
    }

    final headerWidgets = <Widget>[
      _buildMatrixHeaderCell('DAYS', 'WEEKLY'),
      ...morningCells.map((c) => _buildMatrixHeaderCell(
            _getOrdinal(c.periodNumber),
            c.timing.isNotEmpty ? c.timing : (provider.periodTimings[c.periodNumber.toString()] ?? ''),
          )),
      if (hasBreak) _buildMatrixHeaderCell('BREAK', provider.breakTiming),
      ...afternoonCells.map((c) => _buildMatrixHeaderCell(
            _getOrdinal(c.periodNumber),
            c.timing.isNotEmpty ? c.timing : (provider.periodTimings[c.periodNumber.toString()] ?? ''),
          )),
    ];

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
            columnWidths: columnWidths,
            border: TableBorder.all(color: AppColors.ttBorder, width: 1.2),
            children: [
              // Dynamic Header Row
              TableRow(
                decoration: const BoxDecoration(color: AppColors.ttGreenCell),
                children: headerWidgets,
              ),
              // Dynamic Data Rows
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
                    // Morning cells
                    ...row.morning.map((cell) => _buildMatrixDataCell(cell.item)),
                    // Break column
                    if (hasBreak)
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
                              provider.breakTiming.replaceAll(' - ', '\n'),
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
                    // Afternoon cells
                    ...row.afternoon.map((cell) => _buildMatrixDataCell(cell.item)),
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

