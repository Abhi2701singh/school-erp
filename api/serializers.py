from rest_framework import serializers
from accounts.models import User
from schools.models import School, AcademicSession, Notice
from academics.models import Class, Section, Subject, Timetable
from students.models import Student
from teachers.models import Teacher
from attendance.models import StudentAttendance, TeacherAttendance
from fees.models import FeeHead, FeeStructure, StudentFee, PaymentSubmission, FeePayment
from examinations.models import Exam, MarksEntry
from homework.models import Homework, StudyMaterial


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'logo', 'address', 'phone', 'email', 'website', 'principal_name', 'affiliation_no', 'established_year']


class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'profile_picture']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'numeric_value']


class SectionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_level.name', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'class_level', 'class_name', 'name', 'stream']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'subject_type', 'max_marks', 'pass_marks']


class TimetableSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Timetable
        fields = [
            'id', 'class_level', 'class_name', 'section', 'section_name',
            'subject', 'subject_name', 'teacher_user', 'teacher_name',
            'day', 'period_number', 'start_time', 'end_time'
        ]

    def get_teacher_name(self, obj):
        if obj.teacher_user:
            return obj.teacher_user.get_full_name() or obj.teacher_user.username
        return "Teacher"


class StudentProfileSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='current_class.name', read_only=True)
    section_name = serializers.CharField(source='current_section.name', read_only=True)
    session_name = serializers.CharField(source='academic_session.name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'admission_no', 'roll_no', 'first_name', 'last_name', 'full_name',
            'dob', 'gender', 'blood_group', 'photo', 'govt_id', 'address',
            'admission_date', 'current_class', 'class_name', 'current_section', 'section_name',
            'academic_session', 'session_name', 'father_name', 'mother_name',
            'guardian_name', 'parent_phone', 'status'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TeacherProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    assigned_classes_list = ClassSerializer(source='assigned_classes', many=True, read_only=True)
    assigned_subjects_list = SubjectSerializer(source='assigned_subjects', many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'staff_id', 'full_name', 'qualification', 'designation',
            'phone', 'address', 'joining_date', 'is_class_teacher',
            'class_teacher_for_class', 'class_teacher_for_section',
            'assigned_classes_list', 'assigned_subjects_list'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class FeeHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeHead
        fields = ['id', 'name', 'description']


class StudentFeeSerializer(serializers.ModelSerializer):
    fee_head_name = serializers.CharField(source='fee_head.name', read_only=True)
    net_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    previous_arrears = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_payable_with_arrears = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_pending_submission = serializers.BooleanField(read_only=True)
    under_review_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = StudentFee
        fields = [
            'id', 'fee_head', 'fee_head_name', 'academic_session',
            'amount_due', 'amount_discount', 'amount_paid', 'net_due',
            'due_date', 'status', 'is_overdue', 'previous_arrears',
            'total_payable_with_arrears', 'has_pending_submission', 'under_review_amount'
        ]


class PaymentSubmissionSerializer(serializers.ModelSerializer):
    fee_head_name = serializers.CharField(source='student_fee.fee_head.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_mode_display = serializers.CharField(source='get_payment_mode_display', read_only=True)

    class Meta:
        model = PaymentSubmission
        fields = [
            'id', 'submission_no', 'student_fee', 'fee_head_name',
            'amount', 'payment_date', 'payment_mode', 'payment_mode_display',
            'transaction_id', 'bank_name', 'proof_file', 'student_note',
            'status', 'status_display', 'submitted_at', 'rejection_reason'
        ]
        read_only_fields = ['submission_no', 'status', 'submitted_at', 'rejection_reason']


class StudentAttendanceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'date', 'class_level', 'class_name', 'section', 'section_name',
            'student', 'status', 'status_display', 'remarks'
        ]


class HomeworkSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = [
            'id', 'class_level', 'class_name', 'section', 'section_name',
            'subject', 'subject_name', 'title', 'description',
            'attachment', 'assigned_date', 'due_date', 'created_by_name'
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username


class StudyMaterialSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'class_level', 'class_name', 'subject', 'subject_name',
            'title', 'description', 'file', 'uploaded_at', 'uploaded_by_name'
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() or obj.uploaded_by.username


class NoticeSerializer(serializers.ModelSerializer):
    target_role_display = serializers.CharField(source='get_target_role_display', read_only=True)

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'target_role', 'target_role_display',
            'attachment', 'is_active', 'created_at'
        ]


class ExamSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_level.name', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type', 'class_level', 'class_name', 'start_date', 'end_date', 'is_published']


class MarksEntrySerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    max_marks = serializers.DecimalField(source='subject.max_marks', max_digits=5, decimal_places=2, read_only=True)
    pass_marks = serializers.DecimalField(source='subject.pass_marks', max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = MarksEntry
        fields = [
            'id', 'exam', 'exam_name', 'subject', 'subject_name',
            'theory_marks_obtained', 'practical_marks_obtained',
            'total_marks_obtained', 'max_marks', 'pass_marks',
            'grade', 'is_pass', 'remarks'
        ]
