class TimetableEntryModel {
  final int id;
  final int classLevel;
  final String className;
  final int section;
  final String sectionName;
  final int subject;
  final String subjectName;
  final int? teacherUser;
  final String teacherName;
  final String day;
  final int periodNumber;
  final String startTime;
  final String endTime;

  TimetableEntryModel({
    required this.id,
    required this.classLevel,
    required this.className,
    required this.section,
    required this.sectionName,
    required this.subject,
    required this.subjectName,
    this.teacherUser,
    required this.teacherName,
    required this.day,
    required this.periodNumber,
    required this.startTime,
    required this.endTime,
  });

  factory TimetableEntryModel.fromJson(Map<String, dynamic> json) {
    return TimetableEntryModel(
      id: json['id'] ?? 0,
      classLevel: json['class_level'] ?? 0,
      className: json['class_name'] ?? '',
      section: json['section'] ?? 0,
      sectionName: json['section_name'] ?? '',
      subject: json['subject'] ?? 0,
      subjectName: json['subject_name'] ?? '',
      teacherUser: json['teacher_user'],
      teacherName: json['teacher_name'] ?? 'Teacher',
      day: json['day'] ?? 'Monday',
      periodNumber: json['period_number'] ?? 1,
      startTime: json['start_time'] ?? '',
      endTime: json['end_time'] ?? '',
    );
  }
}

class GridCellModel {
  final int periodNumber;
  final String timing;
  final TimetableEntryModel? item;

  GridCellModel({required this.periodNumber, this.timing = '', this.item});

  factory GridCellModel.fromJson(Map<String, dynamic> json) {
    return GridCellModel(
      periodNumber: json['period_number'] ?? 1,
      timing: json['timing'] ?? '',
      item: json['item'] != null ? TimetableEntryModel.fromJson(json['item']) : null,
    );
  }
}

class GridRowModel {
  final String day;
  final String dayDisplay;
  final List<GridCellModel> morning;
  final List<GridCellModel> afternoon;

  GridRowModel({
    required this.day,
    required this.dayDisplay,
    required this.morning,
    required this.afternoon,
  });

  factory GridRowModel.fromJson(Map<String, dynamic> json) {
    return GridRowModel(
      day: json['day'] ?? 'Monday',
      dayDisplay: json['day_display'] ?? 'MONDAY',
      morning: (json['morning'] as List? ?? []).map((e) => GridCellModel.fromJson(e)).toList(),
      afternoon: (json['afternoon'] as List? ?? []).map((e) => GridCellModel.fromJson(e)).toList(),
    );
  }
}
