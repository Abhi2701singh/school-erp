class StudentModel {
  final int id;
  final String admissionNo;
  final String rollNo;
  final String firstName;
  final String lastName;
  final String fullName;
  final String dob;
  final String gender;
  final String? bloodGroup;
  final String? photo;
  final String? govtId;
  final String address;
  final int currentClass;
  final String className;
  final int currentSection;
  final String sectionName;
  final String sessionName;
  final String fatherName;
  final String motherName;
  final String parentPhone;
  final String status;

  StudentModel({
    required this.id,
    required this.admissionNo,
    required this.rollNo,
    required this.firstName,
    required this.lastName,
    required this.fullName,
    required this.dob,
    required this.gender,
    this.bloodGroup,
    this.photo,
    this.govtId,
    required this.address,
    required this.currentClass,
    required this.className,
    required this.currentSection,
    required this.sectionName,
    required this.sessionName,
    required this.fatherName,
    required this.motherName,
    required this.parentPhone,
    required this.status,
  });

  factory StudentModel.fromJson(Map<String, dynamic> json) {
    return StudentModel(
      id: json['id'] ?? 0,
      admissionNo: json['admission_no'] ?? '',
      rollNo: json['roll_no'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      fullName: json['full_name'] ?? '${json['first_name'] ?? ''} ${json['last_name'] ?? ''}'.trim(),
      dob: json['dob'] ?? '',
      gender: json['gender'] ?? 'M',
      bloodGroup: json['blood_group'],
      photo: json['photo'],
      govtId: json['govt_id'],
      address: json['address'] ?? '',
      currentClass: json['current_class'] ?? 0,
      className: json['class_name'] ?? '',
      currentSection: json['current_section'] ?? 0,
      sectionName: json['section_name'] ?? '',
      sessionName: json['session_name'] ?? '',
      fatherName: json['father_name'] ?? '',
      motherName: json['mother_name'] ?? '',
      parentPhone: json['parent_phone'] ?? '',
      status: json['status'] ?? 'ACTIVE',
    );
  }
}
