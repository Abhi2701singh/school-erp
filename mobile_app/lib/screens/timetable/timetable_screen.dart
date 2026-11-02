import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/timetable_provider.dart';
import '../../models/timetable_model.dart';
import '../../widgets/common_widgets.dart';
import '../../widgets/app_drawer.dart';

class TimetableScreen extends StatefulWidget {
  final ValueChanged<int>? onSelectTab;
  const TimetableScreen({super.key, this.onSelectTab});

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
    // Default to today's day if it falls Mon-Sat
    final weekday = DateTime.now().weekday; // 1=Mon, ..., 6=Sat, 7=Sun
    final initialIndex = (weekday >= 1 && weekday <= 6) ? (weekday - 1) : 0;
    _tabController = TabController(length: _days.length, vsync: this, initialIndex: initialIndex);

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
      drawer: AppDrawer(activeIndex: 1, onSelectTab: widget.onSelectTab),
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
        title: const Text('Class Timetable Routine'),
        actions: [
          IconButton(
            icon: Icon(
              _isMatrixView ? Icons.view_agenda_rounded : Icons.grid_view_rounded,
              color: AppColors.primary,
            ),
            tooltip: _isMatrixView ? 'Switch to Daily Timeline' : 'Switch to Weekly Matrix',
            onPressed: () {
              setState(() {
                _isMatrixView = !_isMatrixView;
              });
            },
          ),
        ],
      ),
      body: timetableProvider.isLoading
          ? const LoadingIndicator(message: 'Loading weekly routine schedule...')
          : Column(
              children: [
                // Modern Class Routine Header Card
                _buildClassHeaderCard(timetableProvider),

                if (_isMatrixView)
                  Expanded(child: _buildMatrixGridView(timetableProvider))
                else ...[
                  // Day Selector Tabs with modern capsule styling
                  Container(
                    width: double.infinity,
                    color: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: TabBar(
                      controller: _tabController,
                      isScrollable: true,
                      indicatorSize: TabBarIndicatorSize.tab,
                      indicator: BoxDecoration(
                        color: AppColors.primary,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      labelColor: Colors.white,
                      unselectedLabelColor: AppColors.textSecondary,
                      labelStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold),
                      unselectedLabelStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500),
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      labelPadding: const EdgeInsets.symmetric(horizontal: 14),
                      tabs: _days.map((d) => Tab(text: d.substring(0, 3).toUpperCase())).toList(),
                    ),
                  ),
                  const Divider(height: 1),
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

  Widget _buildClassHeaderCard(TimetableProvider provider) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
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
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.primarySubtle,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.class_rounded, color: AppColors.primary, size: 20),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Class ${provider.selectedClass.toUpperCase()} - Sec ${provider.selectedSection.toUpperCase()}',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  Text(
                    'Academic Session Routine',
                    style: GoogleFonts.inter(fontSize: 11, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.surfaceMuted,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  _isMatrixView ? Icons.grid_on_rounded : Icons.view_day_rounded,
                  size: 13,
                  color: AppColors.textSecondary,
                ),
                const SizedBox(width: 4),
                Text(
                  _isMatrixView ? 'Matrix' : 'Daily',
                  style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                ),
              ],
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
        message: 'No periods scheduled in the active routine for $dayName.',
        icon: Icons.event_busy_rounded,
        onRefresh: () => provider.fetchTimetable(),
      );
    }

    final hasBreak = provider.hasBreak && provider.breakAfterPeriod > 0;
    final morningEntries = hasBreak
        ? dayEntries.where((e) => e.periodNumber <= provider.breakAfterPeriod).toList()
        : dayEntries;
    final afternoonEntries = hasBreak
        ? dayEntries.where((e) => e.periodNumber > provider.breakAfterPeriod).toList()
        : <TimetableEntryModel>[];

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      children: [
        if (morningEntries.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 8),
            child: Text(
              hasBreak ? 'MORNING SESSION' : 'DAILY CLASSES',
              style: GoogleFonts.poppins(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.primary,
                letterSpacing: 1,
              ),
            ),
          ),
          ...morningEntries.map((entry) => _buildPeriodCard(entry, provider)),
          const SizedBox(height: 10),
        ],

        // Recess / Lunch Break Card
        if (hasBreak) ...[
          _buildLunchBreakCard(provider.breakTiming.isNotEmpty ? provider.breakTiming : '11:40 AM - 12:20 PM'),
          const SizedBox(height: 10),
        ],

        if (afternoonEntries.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 8),
            child: Text(
              'AFTERNOON SESSION',
              style: GoogleFonts.poppins(
                fontSize: 11,
                fontWeight: FontWeight.w700,
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
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.accentSubtle,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFFDE68A)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.accent,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.restaurant_rounded, color: Colors.white, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'RECESS / LUNCH BREAK',
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF92400E),
                    letterSpacing: 0.3,
                  ),
                ),
                Text(
                  'Meals & Refreshment Time',
                  style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFFB45309)),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFFCD34D)),
            ),
            child: Text(
              breakTime,
              style: GoogleFonts.inter(
                fontSize: 10.5,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF92400E),
              ),
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
      margin: const EdgeInsets.only(bottom: 8),
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
              border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
            ),
            child: Center(
              child: Text(
                'P${entry.periodNumber}',
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
                  entry.subjectName.toUpperCase(),
                  style: GoogleFonts.poppins(
                    fontSize: 13.5,
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
                        entry.teacherName,
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
              periodTiming.replaceAll(' - ', '\n'),
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
      0: const FixedColumnWidth(85), // Day label
    };
    int colIdx = 1;
    for (int i = 0; i < morningCells.length; i++) {
      columnWidths[colIdx++] = const FixedColumnWidth(105);
    }
    if (hasBreak) {
      columnWidths[colIdx++] = const FixedColumnWidth(60); // Break
    }
    for (int i = 0; i < afternoonCells.length; i++) {
      columnWidths[colIdx++] = const FixedColumnWidth(105);
    }

    final headerWidgets = <Widget>[
      _buildMatrixHeaderCell('DAY', 'SESSION'),
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
        padding: const EdgeInsets.all(14),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.border),
          ),
          child: Table(
            defaultColumnWidth: const FixedColumnWidth(105),
            columnWidths: columnWidths,
            border: TableBorder.all(color: AppColors.border, width: 0.8),
            children: [
              TableRow(
                decoration: const BoxDecoration(
                  color: Color(0xFFF1F5F9),
                ),
                children: headerWidgets,
              ),
              ...provider.gridRows.map((row) {
                return TableRow(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 4),
                      color: AppColors.surfaceMuted,
                      child: Center(
                        child: Text(
                          row.dayDisplay,
                          style: GoogleFonts.inter(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                    ...row.morning.map((cell) => _buildMatrixDataCell(cell.item)),
                    if (hasBreak)
                      Container(
                        color: AppColors.accentSubtle,
                        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 2),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              'RECESS',
                              style: GoogleFonts.inter(
                                fontSize: 8.5,
                                fontWeight: FontWeight.w800,
                                color: const Color(0xFF92400E),
                              ),
                            ),
                          ],
                        ),
                      ),
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
            style: GoogleFonts.poppins(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
            textAlign: TextAlign.center,
          ),
          if (timeSlot.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(
              timeSlot,
              style: GoogleFonts.inter(
                fontSize: 8.5,
                fontWeight: FontWeight.w500,
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
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
        padding: const EdgeInsets.symmetric(vertical: 16),
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
            item.teacherName,
            style: GoogleFonts.inter(fontSize: 9, fontWeight: FontWeight.w500, color: AppColors.textSecondary),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
