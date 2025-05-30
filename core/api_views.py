from rest_framework.views import APIView
from .models import Staff, Department, School, StudentClass, Student, Attendance, Device
from .serializers import StaffSerializers, DepartmentSerializers, SchoolSerializers, StudentClassSerializers, \
    StudentSerializers, AttendanceSerializers, MyTokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class StaffBySchoolDepartment(APIView):

    def get(self, request, school_id, department_id, staff_id=None):
        if staff_id is not None:
            staff = Staff.objects.filter(
                id=staff_id,
                school_id=school_id,
                department_id=department_id
            ).first()

            if not staff:
                return Response({"detail": "Staff not found"}, status=404)

            serializer = StaffSerializers(staff)
            return Response(serializer.data)

        staff_qs = Staff.objects.filter(
            school_id=school_id,
            department_id=department_id
        )
        serializer = StaffSerializers(staff_qs, many=True)
        return Response(serializer.data)


class DepartmentBySchool(APIView):

    def get(self, request, school_id):
        department_qs = Department.objects.filter(
            school_id=school_id
        )
        serializer = DepartmentSerializers(department_qs, many=True)
        return Response(serializer.data)


class StudentClassView(APIView):

    def get(self, request, school_id):
        class_qs = StudentClass.objects.filter(school_id=school_id)
        serializer = StudentClassSerializers(class_qs, many=True)
        return Response(serializer.data)


class SchoolView(APIView):

    def get(self, request, school_id=None):
        if school_id is not None:
            school = get_object_or_404(School, id=school_id)
            serializer = SchoolSerializers(school)
            return Response(serializer.data)

        else:
            schools = School.objects.all()
            serializer = SchoolSerializers(schools, many=True)
            return Response(serializer.data)


class StudentView(APIView):

    def get(self, request, school_id, class_id, student_id=None):
        if student_id is not None:
            student = Student.objects.filter(
                id=student_id,
                school_id=school_id,
                student_class_id=class_id
            ).first()

            if not student:
                return Response({"detail": "Student not found"}, status=404)

            serializer = StudentSerializers(student)
            return Response(serializer.data)

        student_qs = Student.objects.filter(
            school_id=school_id,
            student_class_id=class_id
        )
        serializer = StudentSerializers(student_qs, many=True)
        return Response(serializer.data)


import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime

from .models import Attendance, Staff, Student, Device
from .serializers import AttendanceSerializers

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from .models import Attendance, Staff, Student, Device
from .serializers import AttendanceSerializers


class AttendanceView(APIView):

    def get(self, request, school_id, department_id=None, staff_id=None, student_class_id=None, student_id=None):
        if staff_id and department_id:
            # Staff attendance
            attendance = Attendance.objects.filter(
                school_id=school_id,
                department_id=department_id,
                staff_id=staff_id
            )
        elif student_id and student_class_id:
            # Student attendance
            attendance = Attendance.objects.filter(
                school_id=school_id,
                student_class_id=student_class_id,
                student_id=student_id
            )
        else:
            return Response({"error": "Missing or invalid parameters"}, status=400)

        serializer = AttendanceSerializers(attendance, many=True)
        return Response(serializer.data)

    def post(self, request, school_id, department_id=None, staff_id=None, student_class_id=None, student_id=None):
        serial = request.data.get("serial")
        timestamp_str = request.data.get("timestamp")

        if not serial or not timestamp_str:
            return Response({"error": "Missing serial or timestamp"}, status=400)

        timestamp = parse_datetime(timestamp_str)
        if not timestamp:
            return Response({"error": "Invalid timestamp format"}, status=400)

        device = Device.objects.filter(serial_number=serial).first()
        if not device:
            return Response({"error": "Device not found"}, status=404)

        # Handle staff attendance
        if staff_id and department_id:
            try:
                staff = Staff.objects.get(id=staff_id, school_id=school_id, department_id=department_id)
            except Staff.DoesNotExist:
                return Response({"error": "Staff not found"}, status=404)

            Attendance.objects.create(
                attendee_type='staff',
                staff=staff,
                arrival_time=timestamp,
                device=device,
                department=staff.department,
                school=staff.school,
            )

        # Handle student attendance
        elif student_id and student_class_id:
            try:
                student = Student.objects.get(id=student_id, school_id=school_id, student_class_id=student_class_id)
            except Student.DoesNotExist:
                return Response({"error": "Student not found"}, status=404)

            Attendance.objects.create(
                attendee_type='student',
                student=student,
                arrival_time=timestamp,
                device=device,
                student_class=student.student_class,
                school=student.school,
            )

        else:
            return Response({"error": "Invalid parameters for staff or student"}, status=400)

        return Response({"success": "Attendance recorded"}, status=201)


class SchoolSummaryView(APIView):
    def get(self, request, school_id):
        staff_count = Staff.objects.filter(school_id=school_id).count()
        student_count = Student.objects.filter(school_id=school_id).count()

        return Response({
            "school_id": school_id,
            "total_staff": staff_count,
            "total_students": student_count
        })


# NOTIFICATION

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    user = request.user
    token = request.data.get('fcm_token')

    if not token:
        return Response({"error": "No token provided."}, status=400)

    try:
        # Check which type of user is logged in
        if hasattr(user, 'staff'):
            user.staff.fcm_token = token
            user.staff.save()
        elif hasattr(user, 'student'):
            user.student.fcm_token = token
            user.student.save()
        elif hasattr(user, 'schooladmin'):
            user.schooladmin.fcm_token = token
            user.schooladmin.save()
        else:
            return Response({"error": "Unknown user type."}, status=400)

        return Response({"message": "FCM token updated successfully."})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
