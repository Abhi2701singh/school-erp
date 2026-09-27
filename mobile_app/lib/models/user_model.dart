class UserModel {
  final int id;
  final String username;
  final String email;
  final String firstName;
  final String lastName;
  final String fullName;
  final String role;
  final String? phone;
  final String? profilePicture;

  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.fullName,
    required this.role,
    this.phone,
    this.profilePicture,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      fullName: json['full_name'] ?? json['username'] ?? '',
      role: json['role'] ?? 'STUDENT',
      phone: json['phone'],
      profilePicture: json['profile_picture'],
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'username': username,
    'email': email,
    'first_name': firstName,
    'last_name': lastName,
    'full_name': fullName,
    'role': role,
    'phone': phone,
    'profile_picture': profilePicture,
  };
}

class SchoolModel {
  final int id;
  final String name;
  final String code;
  final String? logo;
  final String address;
  final String phone;
  final String email;
  final String principalName;

  SchoolModel({
    required this.id,
    required this.name,
    required this.code,
    this.logo,
    required this.address,
    required this.phone,
    required this.email,
    required this.principalName,
  });

  factory SchoolModel.fromJson(Map<String, dynamic> json) {
    return SchoolModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      code: json['code'] ?? '',
      logo: json['logo'],
      address: json['address'] ?? '',
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      principalName: json['principal_name'] ?? '',
    );
  }
}
