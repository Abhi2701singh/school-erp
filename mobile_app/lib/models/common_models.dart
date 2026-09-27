class AttendanceModel {
  final int id;
  final String date;
  final String status;
  final String statusDisplay;
  final String? remarks;

  AttendanceModel({
    required this.id,
    required this.date,
    required this.status,
    required this.statusDisplay,
    this.remarks,
  });

  factory AttendanceModel.fromJson(Map<String, dynamic> json) {
    return AttendanceModel(
      id: json['id'] ?? 0,
      date: json['date'] ?? '',
      status: json['status'] ?? 'P',
      statusDisplay: json['status_display'] ?? 'Present',
      remarks: json['remarks'],
    );
  }
}

class HomeworkModel {
  final int id;
  final String className;
  final String sectionName;
  final String subjectName;
  final String title;
  final String description;
  final String? attachment;
  final String assignedDate;
  final String dueDate;
  final String createdByName;

  HomeworkModel({
    required this.id,
    required this.className,
    required this.sectionName,
    required this.subjectName,
    required this.title,
    required this.description,
    this.attachment,
    required this.assignedDate,
    required this.dueDate,
    required this.createdByName,
  });

  factory HomeworkModel.fromJson(Map<String, dynamic> json) {
    return HomeworkModel(
      id: json['id'] ?? 0,
      className: json['class_name'] ?? '',
      sectionName: json['section_name'] ?? '',
      subjectName: json['subject_name'] ?? 'Subject',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      attachment: json['attachment'],
      assignedDate: json['assigned_date'] ?? '',
      dueDate: json['due_date'] ?? '',
      createdByName: json['created_by_name'] ?? 'Teacher',
    );
  }
}

class NoticeModel {
  final int id;
  final String title;
  final String content;
  final String targetRole;
  final String targetRoleDisplay;
  final String? attachment;
  final String createdAt;

  NoticeModel({
    required this.id,
    required this.title,
    required this.content,
    required this.targetRole,
    required this.targetRoleDisplay,
    this.attachment,
    required this.createdAt,
  });

  factory NoticeModel.fromJson(Map<String, dynamic> json) {
    return NoticeModel(
      id: json['id'] ?? 0,
      title: json['title'] ?? '',
      content: json['content'] ?? '',
      targetRole: json['target_role'] ?? 'ALL',
      targetRoleDisplay: json['target_role_display'] ?? 'All',
      attachment: json['attachment'],
      createdAt: json['created_at'] ?? '',
    );
  }
}

class MarkItemModel {
  final int id;
  final String examName;
  final String subjectName;
  final double theoryMarks;
  final double practicalMarks;
  final double totalMarks;
  final double maxMarks;
  final double passMarks;
  final String grade;
  final bool isPass;

  MarkItemModel({
    required this.id,
    required this.examName,
    required this.subjectName,
    required this.theoryMarks,
    required this.practicalMarks,
    required this.totalMarks,
    required this.maxMarks,
    required this.passMarks,
    required this.grade,
    required this.isPass,
  });

  factory MarkItemModel.fromJson(Map<String, dynamic> json) {
    return MarkItemModel(
      id: json['id'] ?? 0,
      examName: json['exam_name'] ?? 'Exam',
      subjectName: json['subject_name'] ?? 'Subject',
      theoryMarks: double.tryParse(json['theory_marks_obtained']?.toString() ?? '0') ?? 0.0,
      practicalMarks: double.tryParse(json['practical_marks_obtained']?.toString() ?? '0') ?? 0.0,
      totalMarks: double.tryParse(json['total_marks_obtained']?.toString() ?? '0') ?? 0.0,
      maxMarks: double.tryParse(json['max_marks']?.toString() ?? '100') ?? 100.0,
      passMarks: double.tryParse(json['pass_marks']?.toString() ?? '33') ?? 33.0,
      grade: json['grade'] ?? 'P',
      isPass: json['is_pass'] ?? true,
    );
  }
}
