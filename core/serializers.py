from rest_framework import serializers
from .models import Staff, User, Department, School, SchoolAdmin, StudentClass, Student, Attendance
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class StaffSerializers(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Staff
        fields = "__all__"


class DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class SchoolAdminSerializers(serializers.ModelSerializer):
    class Meta:
        model = SchoolAdmin
        fields = ['id']


class SchoolSerializers(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    school_admin = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = "__all__"  # or list them manually + 'user_id'

    def get_school_admin(self, obj):
        admin = getattr(obj, 'schooladmin', None)
        return admin.id if admin else None

    def get_user_id(self, obj):
        # Get the SchoolAdmin object attached to this school
        school_admin = getattr(obj, 'schooladmin', None)
        if school_admin and school_admin.user:
            return school_admin.user.id
        return None


class StudentClassSerializers(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = "__all__"


class StudentSerializers(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = "__all__"


class AttendanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        # Add extra responses here
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['user_role'] = self.user.role
        # If user is a student, include school and student_class info

        if user.role == 'student':
            try:
                student = Student.objects.select_related('school', 'student_class').get(user=user)
                data['school_id'] = student.school.id
                data['school_name'] = student.school.name
                data['student_class_id'] = student.student_class.id if student.student_class else None
                data['student_id'] = student.id
            except Student.DoesNotExist:
                data['school_id'] = None
                data['school_name'] = None
                data['student_class_id'] = None
                data['student_id'] = None

        return data




